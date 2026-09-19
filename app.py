import os
from flask import Flask, render_template, request, jsonify, send_file, session
import config
from services.demo_data import DEMO_PRODUCTS, find_demo_product, update_demo_inventory
from services.inventory import valid_barcode, restock
from services.shopify import ShopifyService
from services.labels import create_small_tag_pdf, create_a4_sheet

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "phase2-local-demo-secret")
shop = ShopifyService()
SCANNED = []

def effective_mode():
    """Return the data source selected for the current browser session.

    I kept the demo mode after connecting Shopify because it is useful for
    testing the interface and label workflow without API credentials.
    """
    mode = session.get("data_mode", config.DATA_MODE)
    return mode if mode in ("demo", "api") else "demo"

def find_product(code):
    """Look up one barcode using the currently selected data source."""
    if effective_mode() == "api":
        return shop.find_barcode(code)
    return find_demo_product(code)

def selected(codes):
    """Return the scanned products selected for label generation."""
    source = SCANNED + (DEMO_PRODUCTS if effective_mode() == "demo" else [])
    products_by_barcode = {item["barcode"]: item for item in source}
    return [products_by_barcode[code] for code in codes if code in products_by_barcode]

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/status")
def status():
    return jsonify(mode=effective_mode(), shopify_configured=shop.configured())

@app.post("/api/mode")
def set_mode():
    mode = str((request.get_json() or {}).get("mode", "")).lower()
    if mode not in ("demo", "api"):
        return jsonify(error="Mode must be demo or api."), 400
    session["data_mode"] = mode
    SCANNED.clear()
    return jsonify(ok=True, mode=mode, shopify_configured=shop.configured())

@app.get("/api/scanned")
def scanned():
    return jsonify(SCANNED)

@app.post("/api/scan")
def scan():
    code = str((request.get_json() or {}).get("barcode", "")).strip()
    if not valid_barcode(code):
        return jsonify(error="Barcode must be exactly 8 digits."), 400
    try:
        item = find_product(code)
    except Exception as e:
        return jsonify(error=str(e)), 502
    if not item:
        return jsonify(error="Barcode not found."), 404
    SCANNED[:] = [x for x in SCANNED if x["barcode"] != code]
    SCANNED.insert(0, item)
    return jsonify(item=item, items=SCANNED)

@app.delete("/api/scanned")
def clear_scanned():
    SCANNED.clear()
    return jsonify(ok=True)

@app.delete("/api/scanned/<code>")
def remove(code):
    SCANNED[:] = [x for x in SCANNED if x["barcode"] != code]
    return jsonify(ok=True)

@app.post("/api/inventory/update")
def inventory_update():
    payload = request.get_json() or {}
    code = str(payload.get("barcode", "")).strip()
    qty = payload.get("quantity")
    if not valid_barcode(code) or type(qty) is not int or qty < 0:
        return jsonify(error="Valid 8-digit barcode and integer quantity >= 0 required."), 400
    try:
        if effective_mode() == "demo":
            new = update_demo_inventory(code, qty)
        else:
            new = shop.set_inventory(code, qty)
    except Exception as e:
        return jsonify(error=str(e)), 400
    for x in SCANNED:
        if x["barcode"] == code:
            x["inventory_quantity"] = new
    return jsonify(ok=True, quantity=new, message=f"Inventory updated to {new}.")

@app.get("/api/restock")
def restock_api():
    items = [dict(x) for x in (DEMO_PRODUCTS if effective_mode() == "demo" else SCANNED)]
    try:
        if effective_mode() == "api":
            counts = shop.sold_counts_6m([x["barcode"] for x in items])
            for x in items:
                x["sold_6m"] = counts.get(x["barcode"], 0)
        return jsonify([restock(x) for x in items])
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.post("/labels/a4.pdf")
def a4():
    codes = request.form.getlist("codes")
    rows = request.form.get("rows", 4)
    cols = request.form.get("columns", 3)
    buf = create_a4_sheet(selected(codes), rows, cols, "box")
    return send_file(buf, mimetype="application/pdf", as_attachment=False, download_name="box_labels_A4.pdf")

@app.post("/labels/small.pdf")
def small_pdf():
    payload = request.get_json(silent=True) or {}
    codes = payload.get("codes") or request.form.getlist("codes")
    copies = int(payload.get("copies") or request.form.get("copies") or 1)
    items = selected(codes)
    if not items:
        return jsonify(error="Select at least one item."), 400
    buf = create_small_tag_pdf(items, copies)
    download = request.args.get("download") == "1"
    return send_file(
        buf,
        mimetype="application/pdf",
        as_attachment=download,
        download_name="jewelry_small_tags.pdf",
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=config.FLASK_PORT, debug=True)
