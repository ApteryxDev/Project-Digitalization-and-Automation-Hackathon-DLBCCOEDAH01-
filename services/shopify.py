import time,requests
from datetime import date,timedelta
from config import SHOPIFY_SHOP,SHOPIFY_CLIENT_ID,SHOPIFY_CLIENT_SECRET,SHOPIFY_API_VERSION
class ShopifyError(RuntimeError): pass
class ShopifyService:
 def __init__(self): self.token=None; self.expires=0
 def configured(self): return bool(SHOPIFY_SHOP and SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET)
 def _token(self):
  if self.token and time.time()<self.expires-60:return self.token
  r=requests.post(f'https://{SHOPIFY_SHOP}/admin/oauth/access_token',json={'grant_type':'client_credentials','client_id':SHOPIFY_CLIENT_ID,'client_secret':SHOPIFY_CLIENT_SECRET},timeout=15); r.raise_for_status(); d=r.json(); self.token=d['access_token']; self.expires=time.time()+int(d.get('expires_in',86400)); return self.token
 def gql(self,q,v=None):
  r=requests.post(f'https://{SHOPIFY_SHOP}/admin/api/{SHOPIFY_API_VERSION}/graphql.json',headers={'X-Shopify-Access-Token':self._token(),'Content-Type':'application/json'},json={'query':q,'variables':v or {}},timeout=25); r.raise_for_status(); d=r.json()
  if d.get('errors'): raise ShopifyError(str(d['errors']))
  return d['data']
 def find_barcode(self,code):
  q='''query($s:String!){productVariants(first:10,query:$s){nodes{id title sku barcode price inventoryQuantity selectedOptions{name value} image{url} inventoryItem{id inventoryLevels(first:10){nodes{location{id} quantities(names:["available"]){name quantity}}}} product{title featuredMedia{preview{image{url}}}}}}}'''
  nodes=self.gql(q,{'s':f'barcode:{code}'})['productVariants']['nodes']; print(f'[Shopify] Barcode searched: {code}\n[Shopify] Variants returned: {len(nodes)}')
  v=next((x for x in nodes if str(x.get('barcode') or '')==code),None)
  if not v:return None
  opts=', '.join(f"{o['name']}: {o['value']}" for o in v.get('selectedOptions',[]) if o.get('value')!='Default Title')
  img=(v.get('image') or {}).get('url') or ((((v.get('product') or {}).get('featuredMedia') or {}).get('preview') or {}).get('image') or {}).get('url')
  levels=[]
  for l in ((v.get('inventoryItem') or {}).get('inventoryLevels') or {}).get('nodes',[]):
   qs=l.get('quantities') or []; avail=next((x.get('quantity') for x in qs if x.get('name')=='available'),None); levels.append({'location_id':l['location']['id'],'available':avail})
  return {'title':v['product']['title'],'variant':opts,'sku':v.get('sku') or '','barcode':code,'price':v.get('price'),'image':img,'inventory_quantity':v.get('inventoryQuantity') or 0,'inventory_item_id':(v.get('inventoryItem') or {}).get('id'),'inventory_levels':levels}
 def set_inventory(self,code,qty):
  item=self.find_barcode(code); levels=[x for x in (item or {}).get('inventory_levels',[]) if x.get('available') is not None]
  if not item: raise ShopifyError('Barcode not found.')
  if len(levels)!=1: raise ShopifyError('Exactly one inventory location is required to publish safely.')
  # Absolute available quantity. compareQuantity helps avoid silently overwriting concurrent changes.
  q='''mutation($input:InventorySetQuantitiesInput!){inventorySetQuantities(input:$input){inventoryAdjustmentGroup{changes{name delta}} userErrors{field message}}}'''
  inp={'name':'available','reason':'correction','ignoreCompareQuantity':False,'quantities':[{'inventoryItemId':item['inventory_item_id'],'locationId':levels[0]['location_id'],'quantity':qty,'compareQuantity':levels[0]['available']}]}
  out=self.gql(q,{'input':inp})['inventorySetQuantities']; errs=out.get('userErrors') or []
  if errs: raise ShopifyError('; '.join(e['message'] for e in errs))
  return qty
 def sold_counts_6m(self,codes):
  if not codes:return {}
  since=(date.today()-timedelta(days=183)).isoformat(); q='''query($s:String!,$after:String){orders(first:100,after:$after,query:$s){nodes{lineItems(first:100){nodes{quantity variant{barcode}}}} pageInfo{hasNextPage endCursor}}}'''
  counts={c:0 for c in codes}; after=None
  while True:
   d=self.gql(q,{'s':f'created_at:>={since}','after':after})['orders']
   for o in d['nodes']:
    for li in o['lineItems']['nodes']:
     b=((li.get('variant') or {}).get('barcode') or '');
     if b in counts: counts[b]+=int(li.get('quantity') or 0)
   if not d['pageInfo']['hasNextPage']:break
   after=d['pageInfo']['endCursor']
  return counts
