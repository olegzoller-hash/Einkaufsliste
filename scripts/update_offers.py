"""Daily offers ingestion; expressly permitted sources only.
All seven adapters are wired. No source is enabled without source-specific permission.
No Firebase access; outputs only verified active offers to docs/offers.json.
"""
import json,sys,os,urllib.request,urllib.error,hashlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from adapters import parse_response
ROOT=Path(__file__).resolve().parents[1]
NOW=lambda:datetime.now(ZoneInfo('UTC')).isoformat(timespec='seconds').replace('+00:00','Z')
MAX_BYTES=2_000_000

def fetch(source):
    url=source.get('feedUrl') if source['sourceType']=='json' else source['sourceUrl']
    if not isinstance(url,str) or not url.startswith('https://'):raise ValueError('HTTPS-Quelle erforderlich')
    headers={'User-Agent':'NaturOffers/2.0 (+operator-configured-feed)','Accept':'application/json' if source['sourceType']=='json' else 'text/html,application/xhtml+xml'}
    env=source.get('feedAuthEnv')
    if env:
        if not env.startswith('NATUR_FEED_TOKEN_'):raise ValueError('Nur dedizierte FEED-TOKEN-Namen erlaubt')
        secret=os.environ.get(env)
        if not secret:raise ValueError('Fehlendes GitHub-Secret '+env)
        headers['Authorization']='Bearer '+secret
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=20) as reply:
        if reply.status!=200:raise RuntimeError('HTTP '+str(reply.status))
        if int(reply.headers.get('Content-Length','0'))>MAX_BYTES:raise ValueError('Antwort zu groß')
        body=reply.read(MAX_BYTES+1)
        if len(body)>MAX_BYTES:raise ValueError('Antwort zu groß')
        content_type=reply.headers.get('Content-Type','').lower()
        if source['sourceType']=='json' and 'json' not in content_type:raise ValueError('Unerwarteter Content-Type für JSON')
        if source['sourceType']=='html' and 'html' not in content_type:raise ValueError('Unerwarteter Content-Type für HTML')
        return body

def check(raw, source):
    if not isinstance(raw,dict): raise ValueError('JSON-Objekt erforderlich')
    source = dict({'id':'hit','sourceUrl':'https://example.org/'},**source)
    return parse_response(json.dumps(raw),dict(source,sourceType='json'))

def run():
    config=json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))
    approved=[x for x in config['sources'] if x.get('enabled')]
    results=[];errors=[];report=[]
    for source in config['sources']:
        sid=source['id']
        if not source.get('enabled'):
            report.append({'market':sid,'status':'disabled','offers':0})
            print(f'SKIP {sid}: nicht aktiviert / Zugang unbestätigt');continue
        if not source.get('permissionConfirmed') or not source.get('regionalConfirmed'):
            errors.append(sid+': erforderliche Rechte oder regionale Zuordnung fehlen')
            report.append({'market':sid,'status':'unapproved','offers':0});continue
        try:
            rows=parse_response(fetch(source),source)
            # Zero valid offers can mean empty period / parser drift; it is NOT success.
            if not rows:raise ValueError('Keine nachweislich gültigen Angebote: Parser oder Quelle prüfen')
            results.extend(rows)
            report.append({'market':sid,'status':'ok','offers':len(rows)})
            print(f'OK {sid}: {len(rows)} gültige Angebote')
        except (urllib.error.HTTPError,urllib.error.URLError,OSError,TimeoutError,ValueError,RuntimeError,KeyError,UnicodeError) as exc:
            reason=f'HTTP {exc.code}' if isinstance(exc,urllib.error.HTTPError) else type(exc).__name__
            errors.append(f'{sid}: {reason}');report.append({'market':sid,'status':'error','reason':reason,'offers':0})
            print(f'FEHLER {sid}: {reason}',file=sys.stderr)
    (ROOT/'docs/source-status.json').write_text(json.dumps({'checkedAt':NOW(),'sources':report,'errors':errors},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if errors:
        # Preserve previous offers; don't publish partial/incomplete results as exhaustive.
        print('FAIL: docs/offers.json unverändert; teilweise/defekte Abrufe nicht veröffentlicht.',file=sys.stderr)
        return 1
    if not approved:
        print('Keine freigegebene Quelle aktiv: bisherige Angebotsdatei unverändert.')
        return 0
    unique={ (v['market'],v['name'].casefold(),v['price'],v['validFrom'],v['validTo']):v for v in results }
    existing_path=ROOT/'docs/offers.json'; new_offers=sorted(unique.values(),key=lambda a:(a['market'],a['name'],a['price']))
    old=json.loads(existing_path.read_text(encoding='utf-8')) if existing_path.exists() else {}
    if old.get('offers')==new_offers:
        print('Keine Änderung an den Angebotsdaten');return 0
    existing_path.write_text(json.dumps({'updatedAt':NOW(),'offers':new_offers,'note':'Nur geprüfte, genehmigte und für die Region bestätigte Feeds.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Veröffentlicht: {len(new_offers)} valide Angebote')
    return 0
if __name__=='__main__':sys.exit(run())
