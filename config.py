"""Configuration values for the Phase 2 prototype.

Values are read from the local .env file so credentials do not have to be
written directly into the application source code.
"""

import os

from dotenv import load_dotenv

load_dotenv()

DATA_MODE = os.getenv("DATA_MODE", "demo").lower()
FLASK_PORT = int(os.getenv("FLASK_PORT", "5001"))

# Shopify credentials are intentionally kept outside the repository.
SHOPIFY_SHOP = os.getenv("SHOPIFY_SHOP", "").replace("https://", "").rstrip("/")
SHOPIFY_CLIENT_ID = os.getenv("SHOPIFY_CLIENT_ID", "")
SHOPIFY_CLIENT_SECRET = os.getenv("SHOPIFY_CLIENT_SECRET", "")
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2026-07")

# Parameters used by the simple restocking rule described in the report.
RESTOCK_MONTHS_COVER = float(os.getenv("RESTOCK_MONTHS_COVER", "3"))
RESTOCK_SAFETY_FACTOR = float(os.getenv("RESTOCK_SAFETY_FACTOR", "1.20"))
