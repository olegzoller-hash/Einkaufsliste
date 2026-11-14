"""Conservative, opt-in adapters. No browser automation, no access bypass.
JSON: documented normalized feed only; HTML: JSON-LD or explicit product attributes.
Never guess a price, valid interval, region or store.
"""
import json
from html.parser import HTMLParser
from datetime import datetime, date
from zoneinfo import ZoneInfo

class StructuredHTML(HTMLParser):
    def __init__(self):
        super().__init__(); self.ld=[];self.products=[];self._script=False;self._buffer=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='script' and 'ld+json' in a.get('type','').lower():
            self._script=True;self._buffer=[]
        if a.get('data-product-name') and a.get('data-offer-price') and a.get('data-valid-from') and a.get('data-valid-to'):
            self.products.append({'name':a['data-product-name'],'price':a['data-offer-price'],'validFrom':a['data-valid-from'],'validTo':a['data-valid-to']})
    def handle_data(self,data):
        if self._script:self._buffer.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self._script:
            self._script=False
            try:self.ld.append(json.loads(''.join(self._buffer)))
            except json.JSONDecodeError:pass

def find_product_nodes(node):
    if isinstance(node,list):
        for item in node: yield from find_product_nodes(item)
    elif isinstance(node,dict):
        t=node.get('@type',[])
        if isinstance(t,str):t=[t]
        if any(str(x).lower().split('/')[-1]=='product' for x in t):yield node
        for value in node.values():
            if isinstance(value,(list,dict)):yield from find_product_nodes(value)

def iso_date(value):
    if not isinstance(value,str):return None
    try:return date.fromisoformat(value[:10]).isoformat()
    except ValueError:return None

def parse_price(value):
    if isinstance(value,bool) or value is None:return None
    if isinstance(value,(int,float)):
        n=float(value)
    elif isinstance(value,str):
        raw=value.replace('€','').replace(' ','').strip()
        if not raw or any(c not in '0123456789,.' for c in raw):return None
        if ',' in raw and '.' in raw: raw=raw.replace('.','').replace(',','.')
        elif ',' in raw:raw=raw.replace(',','.')
        try:n=float(raw)
        except ValueError:return None
    else:return None
    if n!=n or not 0<n<100000:return None
    return round(n,2)

def normalize(raw,source,today=None):
    today=today or datetime.now(ZoneInfo('Europe/Berlin')).date()
    if not isinstance(raw,list):raise ValueError('Angebotsliste muss Array sein')
    cleaned=[]
    for item in raw:
        if not isinstance(item,dict):continue
        name=item.get('name');price=parse_price(item.get('price'))
        start=iso_date(item.get('validFrom'));end=iso_date(item.get('validTo'))
        if not isinstance(name,str) or not name.strip() or len(name)>180 or price is None or not start or not end:continue
        if not(date.fromisoformat(start)<=today<=date.fromisoformat(end)):continue
        url=item.get('sourceUrl') or source['sourceUrl']
        if not isinstance(url,str) or not url.startswith('https://'):continue
        cleaned.append({'name':name.strip(),'market':source['id'],'price':price,'validFrom':start,'validTo':end,'sourceUrl':url})
    return cleaned

def parse_json(body,source):
    data=json.loads(body)
    if not isinstance(data,dict) or not isinstance(data.get('offers'),list):raise ValueError('JSON-Feed benötigt Objekt mit offers-Array')
    # Market in vendor feed cannot override the configured market
    return normalize(data['offers'],source)

def parse_html(body,source):
    if isinstance(body,bytes):body=body.decode('utf-8')
    p=StructuredHTML();p.feed(body)
    rows=list(p.products)
    for obj in p.ld:
        for product in find_product_nodes(obj):
            offers=product.get('offers')
            if not isinstance(offers,(dict,list)):continue
            for offer in offers if isinstance(offers,list) else [offers]:
                if not isinstance(offer,dict):continue
                # Valid-from is often absent on SEO pages; don't manufacture it.
                rows.append({'name':product.get('name'),'price':offer.get('price'),'validFrom':offer.get('validFrom'),'validTo':offer.get('validThrough') or offer.get('priceValidUntil'), 'sourceUrl':product.get('url') or source['sourceUrl']})
    return normalize(rows,source)

def parse_response(body,source):
    typ=source.get('sourceType')
    if typ=='json':return parse_json(body,source)
    if typ=='html':return parse_html(body,source)
    raise ValueError('Unbekannter Quellentyp '+str(typ))
