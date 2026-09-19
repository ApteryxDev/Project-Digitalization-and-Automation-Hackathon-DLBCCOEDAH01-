import math,re
from config import RESTOCK_MONTHS_COVER,RESTOCK_SAFETY_FACTOR

def valid_barcode(v): return bool(re.fullmatch(r'\d{8}',str(v).strip()))
def restock(item):
 sold=int(item.get('sold_6m') or 0); current=int(item.get('inventory_quantity') or 0)
 monthly=sold/6; target=math.ceil(monthly*RESTOCK_MONTHS_COVER*RESTOCK_SAFETY_FACTOR)
 return {**item,'avg_monthly_sales':round(monthly,2),'target_stock':target,'recommended_order':max(0,target-current)}
