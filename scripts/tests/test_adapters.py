import sys,unittest,json,tempfile
from pathlib import Path
from datetime import date,datetime
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from adapters import parse_response,normalize,parse_price
SRC={'id':'hit','sourceType':'html','sourceUrl':'https://www.hit.de/maerkte/meschede/angebote'}
TODAY=datetime.now(ZoneInfo('Europe/Berlin')).date().isoformat()

class AdapterTests(unittest.TestCase):
 def test_html_jsonld(self):
  html=f"""<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Product","name":"Butter","offers":{{"price":"1,49","validFrom":"{TODAY}","priceValidUntil":"{TODAY}"}}}}</script>"""
  self.assertEqual(parse_response(html,SRC)[0]['price'],1.49)
 def test_html_data_attributes(self):
  body=f'<div data-product-name="Milch" data-offer-price="0,99" data-valid-from="{TODAY}" data-valid-to="{TODAY}"></div>'
  self.assertEqual(parse_response(body,SRC)[0]['name'],'Milch')
 def test_missing_dates_dropped(self):
  html='<script type="application/ld+json">{"@type":"Product","name":"Butter","offers":{"price":"1.49"}}</script>'
  self.assertEqual(parse_response(html,SRC),[])
 def test_inactive_dropped(self):
  self.assertEqual(normalize([{'name':'Butter','price':1,'validFrom':'2020-01-01','validTo':'2020-01-02'}],SRC),[])
 def test_json_feed(self):
  data={'offers':[{'name':'Gurke','price':.89,'validFrom':TODAY,'validTo':TODAY}]}
  self.assertEqual(parse_response(json.dumps(data),dict(SRC,sourceType='json'))[0]['market'],'hit')
 def test_invalid_price(self):
  self.assertIsNone(parse_price('nur heute'))
  self.assertIsNone(parse_price(-1))
 def test_no_copied_market(self):
  data={'offers':[{'name':'Gurke','market':'lidl','price':.89,'validFrom':TODAY,'validTo':TODAY}]}
  self.assertEqual(parse_response(json.dumps(data),dict(SRC,sourceType='json'))[0]['market'],'hit')

if __name__=='__main__':unittest.main()
