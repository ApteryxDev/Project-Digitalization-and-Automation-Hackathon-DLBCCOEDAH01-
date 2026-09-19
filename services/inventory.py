"""Small inventory rules shared by demo and Shopify modes."""

import math
import re

from config import RESTOCK_MONTHS_COVER, RESTOCK_SAFETY_FACTOR


def valid_barcode(value):
    """Return True when the value contains exactly eight digits.

    The shop already used 8-digit identifiers on the physical jewelry. During
    development I therefore reused these identifiers instead of introducing a
    second QR-code system.
    """
    barcode = str(value).strip()
    return bool(re.fullmatch(r"\d{8}", barcode))


def restock(item):
    """Calculate the prototype's simple order-up-to recommendation.

    Six months of sales are converted to average monthly demand. The target
    then covers the configured number of months plus a fixed safety factor.
    This is deliberately a transparent rule rather than a forecasting model:
    the available sales history is still limited and the shop needs to be able
    to understand how a recommendation was produced.
    """
    sold_last_six_months = int(item.get("sold_6m") or 0)
    current_stock = int(item.get("inventory_quantity") or 0)

    average_monthly_sales = sold_last_six_months / 6
    target_stock = math.ceil(
        average_monthly_sales * RESTOCK_MONTHS_COVER * RESTOCK_SAFETY_FACTOR
    )
    recommended_order = max(0, target_stock - current_stock)

    return {
        **item,
        "avg_monthly_sales": round(average_monthly_sales, 2),
        "target_stock": target_stock,
        "recommended_order": recommended_order,
    }
