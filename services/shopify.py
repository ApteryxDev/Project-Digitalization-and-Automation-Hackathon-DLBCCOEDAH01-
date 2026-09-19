"""Shopify Admin GraphQL integration used by the prototype.

The service is intentionally small: it only contains the operations needed by
this project (barcode lookup, inventory correction and recent sales counts).
Keeping this code separate from Flask made it easier to test the interface in
demo mode while the Shopify permissions were still being configured.
"""

import time
from datetime import date, timedelta

import requests

from config import (
    SHOPIFY_API_VERSION,
    SHOPIFY_CLIENT_ID,
    SHOPIFY_CLIENT_SECRET,
    SHOPIFY_SHOP,
)


class ShopifyError(RuntimeError):
    """Raised when Shopify returns a response the prototype cannot safely use."""


class ShopifyService:
    def __init__(self):
        self.token = None
        self.expires = 0

    def configured(self):
        """Check whether the three required Shopify settings are present."""
        return bool(SHOPIFY_SHOP and SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET)

    def _token(self):
        """Get an access token and reuse it until shortly before expiration."""
        if self.token and time.time() < self.expires - 60:
            return self.token

        response = requests.post(
            f"https://{SHOPIFY_SHOP}/admin/oauth/access_token",
            json={
                "grant_type": "client_credentials",
                "client_id": SHOPIFY_CLIENT_ID,
                "client_secret": SHOPIFY_CLIENT_SECRET,
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        self.token = data["access_token"]
        self.expires = time.time() + int(data.get("expires_in", 86400))
        return self.token

    def gql(self, query, variables=None):
        """Send one GraphQL request and surface Shopify-level errors."""
        response = requests.post(
            f"https://{SHOPIFY_SHOP}/admin/api/{SHOPIFY_API_VERSION}/graphql.json",
            headers={
                "X-Shopify-Access-Token": self._token(),
                "Content-Type": "application/json",
            },
            json={"query": query, "variables": variables or {}},
            timeout=25,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("errors"):
            raise ShopifyError(str(data["errors"]))
        return data["data"]

    def find_barcode(self, code):
        """Find the exact Shopify variant that uses an 8-digit barcode."""
        query = """
        query($search: String!) {
          productVariants(first: 10, query: $search) {
            nodes {
              id title sku barcode price inventoryQuantity
              selectedOptions { name value }
              image { url }
              inventoryItem {
                id
                inventoryLevels(first: 10) {
                  nodes {
                    location { id }
                    quantities(names: ["available"]) { name quantity }
                  }
                }
              }
              product {
                title
                featuredMedia { preview { image { url } } }
              }
            }
          }
        }
        """
        data = self.gql(query, {"search": f"barcode:{code}"})
        variants = data["productVariants"]["nodes"]

        # Shopify search can return approximate matches, so the barcode is
        # checked again before a product is accepted.
        variant = next(
            (v for v in variants if str(v.get("barcode") or "") == code),
            None,
        )
        if not variant:
            return None

        options = ", ".join(
            f"{option['name']}: {option['value']}"
            for option in variant.get("selectedOptions", [])
            if option.get("value") != "Default Title"
        )

        image_url = (variant.get("image") or {}).get("url")
        if not image_url:
            product = variant.get("product") or {}
            preview = (product.get("featuredMedia") or {}).get("preview") or {}
            image_url = (preview.get("image") or {}).get("url")

        inventory_levels = []
        level_nodes = (
            ((variant.get("inventoryItem") or {}).get("inventoryLevels") or {})
            .get("nodes", [])
        )
        for level in level_nodes:
            quantities = level.get("quantities") or []
            available = next(
                (q.get("quantity") for q in quantities if q.get("name") == "available"),
                None,
            )
            inventory_levels.append(
                {
                    "location_id": level["location"]["id"],
                    "available": available,
                }
            )

        return {
            "title": variant["product"]["title"],
            "variant": options,
            "sku": variant.get("sku") or "",
            "barcode": code,
            "price": variant.get("price"),
            "image": image_url,
            "inventory_quantity": variant.get("inventoryQuantity") or 0,
            "inventory_item_id": (variant.get("inventoryItem") or {}).get("id"),
            "inventory_levels": inventory_levels,
        }

    def set_inventory(self, code, quantity):
        """Publish an absolute inventory quantity for one unambiguous location."""
        item = self.find_barcode(code)
        if not item:
            raise ShopifyError("Barcode not found.")

        levels = [
            level
            for level in item.get("inventory_levels", [])
            if level.get("available") is not None
        ]
        if len(levels) != 1:
            raise ShopifyError(
                "Exactly one inventory location is required to publish safely."
            )

        # The interface keeps +/- changes local until the user presses Publish.
        # compareQuantity also prevents silently overwriting a stock value that
        # changed in Shopify after the product was scanned.
        mutation = """
        mutation($input: InventorySetQuantitiesInput!) {
          inventorySetQuantities(input: $input) {
            inventoryAdjustmentGroup { changes { name delta } }
            userErrors { field message }
          }
        }
        """
        level = levels[0]
        input_data = {
            "name": "available",
            "reason": "correction",
            "ignoreCompareQuantity": False,
            "quantities": [
                {
                    "inventoryItemId": item["inventory_item_id"],
                    "locationId": level["location_id"],
                    "quantity": quantity,
                    "compareQuantity": level["available"],
                }
            ],
        }

        result = self.gql(mutation, {"input": input_data})["inventorySetQuantities"]
        errors = result.get("userErrors") or []
        if errors:
            raise ShopifyError("; ".join(error["message"] for error in errors))
        return quantity

    def sold_counts_6m(self, codes):
        """Count quantities sold for the requested barcodes over ~six months."""
        if not codes:
            return {}

        since = (date.today() - timedelta(days=183)).isoformat()
        query = """
        query($search: String!, $after: String) {
          orders(first: 100, after: $after, query: $search) {
            nodes {
              lineItems(first: 100) {
                nodes { quantity variant { barcode } }
              }
            }
            pageInfo { hasNextPage endCursor }
          }
        }
        """

        counts = {code: 0 for code in codes}
        after = None

        # Orders are paginated because a real shop can easily exceed one page.
        while True:
            data = self.gql(
                query,
                {"search": f"created_at:>={since}", "after": after},
            )["orders"]

            for order in data["nodes"]:
                for line_item in order["lineItems"]["nodes"]:
                    barcode = ((line_item.get("variant") or {}).get("barcode") or "")
                    if barcode in counts:
                        counts[barcode] += int(line_item.get("quantity") or 0)

            if not data["pageInfo"]["hasNextPage"]:
                break
            after = data["pageInfo"]["endCursor"]

        return counts
