"""Nur genehmigte JSON-Angebotsfeeds. Kein Scraping und kein Firebase-Zugriff."""
import json, os, re, sys, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
BASE=Path(__file__).resolve().parents[1]
MARKETS={m['id'] for m in json.loads((BASE/'markets.json').read_text())}
TODAY=datetime.now(ZoneInfo('Europe/Berlin')).date()
def check(raw, source):
    if not isinstance(raw,dict): raise ValueError('Quelle muss JSON-Objekt sein')
    clean=[]
    for o in raw.get('offers',[]):
        try:
            if not isinstance(o,dict):continue
            name=o['name']; market=o['market']; price=o['price']; start=o['validFrom']; end=o['validTo']; link=o['sourceUrl']
            if (not isinstance(name,str) or not name.strip() or len(name)>150 or market not in MARKETS
                or isinstance(price,bool) or not isinstance(price,(int,float)) or not 0<float(price)<100000
                or not isinstance(link,str) or not link.startswith('https://')):continue
            d1=datetime.strptime(start,'%Y-%m-%d').date();d2=datetime.strptime(end,'%Y-%m-%d').date()
            if not d1<=TODAY<=d2:continue
            clean.append({'name':name.strip(),'market':market,'price':round(float(price),2),'validFrom':start,'validTo':end,'sourceUrl':link,'retrievedAt':datetime.now(ZoneInfo('UTC')).isoformat().replace('+00:00','Z')})
        except (KeyError,TypeError,ValueError):continue
    return clean
def main():
    src=json.loads((BASE/'sources.json').read_text())['sources'];found=[];errors=[];active=0
    for s in src:
        url=s.get('feedUrl')
        if not url:print(f"SKIP {s['id']}: keine genehmigte maschinenlesbare Quelle");continue
        if not url.startswith('https://'):errors.append(s['id']+': feedUrl muss HTTPS sein');continue
        active+=1
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NaturOffers/1.0'}),timeout=20) as resp:
                if resp.status!=200:raise RuntimeError('HTTP '+str(resp.status))
                if int(resp.headers.get('Content-Length','0'))>2_000_000:raise ValueError('Feed zu groß')
                data=resp.read(2_000_001)
                if len(data)>2_000_000:raise ValueError('Feed zu groß')
            raw=json.loads(data);valid=check(raw,s);valid=[o for o in valid if o['market']==s['id']];found.extend(valid)
            print(f"OK {s['id']}: {len(valid)} gültige Angebote")
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError,RuntimeError,KeyError) as e:
            errors.append(f"{s['id']}: {type(e).__name__} ({getattr(e,'code','')})")
    unique={ (o['market'],o['name'].casefold(),o['price'],o['validFrom'],o['validTo']):o for o in found }
    out=BASE/'docs/offers.json'
    # Bei Fehler nicht versehentlich bisher gültige Daten wegwerfen.
    if errors:
        print('FEHLER: '+'; '.join(errors),file=sys.stderr)
        return 1
    new={'updatedAt':datetime.now(ZoneInfo('UTC')).isoformat().replace('+00:00','Z') if active else None,'offers':list(unique.values()),'note':'Nur Daten aus explizit konfigurierten, genehmigten JSON-Feeds; kein Live-Scraping.'}
    content=json.dumps(new,ensure_ascii=False,indent=2)+'\n'
    if out.exists() and json.loads(out.read_text()).get('offers')==new['offers']:
        print('Unveränderte Angebote – keine neue Datei geschrieben')
    else:out.write_text(content);print(f"Gespeichert: {len(unique)} Angebote")
    return 0
if __name__=='__main__':sys.exit(main())
