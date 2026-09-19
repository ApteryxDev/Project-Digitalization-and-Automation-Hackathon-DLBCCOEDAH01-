DEMO_PRODUCTS = [
    {"title":"Solitaire Ring","variant":"Color: Gold, Size: 54","sku":"","barcode":"10010101","inventory_quantity":8,"sold_6m":12,"price":"79.90","image":"/static/demo/10010101.png","image_file":"static/demo/10010101.png"},
    {"title":"Solitaire Ring","variant":"Color: Silver, Size: 56","sku":"","barcode":"10010102","inventory_quantity":5,"sold_6m":8,"price":"74.90","image":"/static/demo/10010102.png","image_file":"static/demo/10010102.png"},
    {"title":"Drop Earrings","variant":"Color: Gold","sku":"","barcode":"20014101","inventory_quantity":4,"sold_6m":15,"price":"49.90","image":"/static/demo/20014101.png","image_file":"static/demo/20014101.png"},
    {"title":"Fine Chain Necklace","variant":"Color: Gold, Length: 45 cm","sku":"","barcode":"30008101","inventory_quantity":7,"sold_6m":10,"price":"59.90","image":"/static/demo/30008101.png","image_file":"static/demo/30008101.png"},
    {"title":"Jupiter Necklace","variant":"Color: Steel","sku":"","barcode":"40022001","inventory_quantity":0,"sold_6m":18,"price":"44.90","image":"/static/demo/40022001.png","image_file":"static/demo/40022001.png"},
    {"title":"Celeste Bracelet","variant":"Color: Rose Gold","sku":"","barcode":"50033001","inventory_quantity":3,"sold_6m":11,"price":"39.90","image":"/static/demo/50033001.png","image_file":"static/demo/50033001.png"},
    {"title":"Nova Ring","variant":"Color: White, Size: 52","sku":"","barcode":"60044001","inventory_quantity":6,"sold_6m":7,"price":"69.90","image":"/static/demo/60044001.png","image_file":"static/demo/60044001.png"},
    {"title":"Moon Pendant","variant":"Color: Silver","sku":"","barcode":"70055001","inventory_quantity":2,"sold_6m":13,"price":"34.90","image":"/static/demo/70055001.png","image_file":"static/demo/70055001.png"},
    {"title":"Classic Hoops","variant":"Color: Gold","sku":"","barcode":"80066001","inventory_quantity":9,"sold_6m":16,"price":"42.90","image":"/static/demo/80066001.png","image_file":"static/demo/80066001.png"},
    {"title":"Venus Bracelet","variant":"Color: Black Steel","sku":"","barcode":"90077001","inventory_quantity":1,"sold_6m":9,"price":"37.90","image":"/static/demo/90077001.png","image_file":"static/demo/90077001.png"},
]
def find_demo_product(code):
    return next((dict(x) for x in DEMO_PRODUCTS if x["barcode"] == code), None)
def update_demo_inventory(code, quantity):
    for item in DEMO_PRODUCTS:
        if item["barcode"] == code:
            item["inventory_quantity"] = int(quantity); return item["inventory_quantity"]
    raise ValueError("Demo barcode not found.")
