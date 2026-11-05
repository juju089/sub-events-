"""Public Sub e.V. calendar -> validated JSON and ICS. Python standard library only."""
from __future__ import annotations
import argparse
from datetime import datetime, date, timedelta, timezone
from html import unescape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

SOURCE = 'https://kalender.subonline.org/events-im-zentrum/'
API = 'https://kalender.subonline.org/wp-json/tribe/events/v1/events'
BERLIN = ZoneInfo('Europe/Berlin')
CATEGORIES = {'events-im-zentrum': 'Im Zentrum', 'mittendrin': 'Mittendrin'}
CATEGORY_IDS = '16,14'
MAX_PAGES = 30

class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.hidden = [], 0
    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'}: self.hidden += 1
        if tag in {'br','p','div','li'}: self.parts.append(' ')
    def handle_endtag(self, tag):
        if tag in {'script', 'style'}: self.hidden = max(0,self.hidden-1)
        if tag in {'p','div','li'}: self.parts.append(' ')
    def handle_data(self, text):
        if not self.hidden: self.parts.append(text)

def plain(value):
    if not isinstance(value, str): raise ValueError('Textfeld hat unerwarteten Typ')
    parser = Text(); parser.feed(value)
    return re.sub(r'\s+', ' ', ''.join(parser.parts)).strip()

def safe_url(value, source=False):
    if not isinstance(value, str): return None
    url = urlparse(unescape(value))
    if url.scheme != 'https' or not url.netloc or url.username or url.password: return None
    if source and (url.hostname != 'kalender.subonline.org' or not url.path.startswith('/event/')): return None
    return unescape(value)

def request_json(url):
    last = None
    for attempt in range(3):
        try:
            req = Request(url,headers={'User-Agent':'sub-events/1.0 (+https://github.com/juju089/sub-events)', 'Accept':'application/json'})
            with urlopen(req,timeout=30) as response:
                if urlparse(response.url).hostname != 'kalender.subonline.org': raise ValueError('Unerwartete Weiterleitung')
                if 'application/json' not in response.headers.get('Content-Type',''): raise ValueError('Keine JSON-Antwort')
                raw = response.read(8_000_001)
                if len(raw)>8_000_000: raise ValueError('Antwort zu groß')
                return json.loads(raw.decode('utf-8'))
        except Exception as error:
            last = error
            if attempt<2: time.sleep(2**attempt)
    raise RuntimeError('Offizieller Kalender nach drei Versuchen nicht abrufbar') from last

def fetch_pages(today, days=180, requester=request_json):
    # One day padding compensates source-side timezone conversion at query boundaries.
    params = {'per_page':50,'categories':CATEGORY_IDS,'start_date':str(today-timedelta(days=1))+' 00:00:00',
              'end_date':str(today+timedelta(days=days+1))+' 23:59:59','status':'publish'}
    pages, total, count = [], None, None
    page = 1
    while True:
        # Reconstruct every query: next_rest_url currently drops the category filter.
        payload = requester(API+'?'+urlencode(dict(params,page=page)))
        if not isinstance(payload,dict) or not isinstance(payload.get('events'),list): raise ValueError('Ungültige Kalenderstruktur')
        if type(payload.get('total')) is not int or type(payload.get('total_pages')) is not int: raise ValueError('Seitennavigation fehlt')
        if not 0 <= payload['total_pages'] <= MAX_PAGES or payload['total'] < 0: raise ValueError('Unplausible Seitenzahl')
        if total is None: total,count=payload['total'],payload['total_pages']
        if (total,count)!=(payload['total'],payload['total_pages']): raise ValueError('Kalender änderte sich während des Abrufs; später erneut versuchen')
        pages.append(payload)
        if page>=max(1,count): break
        if not payload['events']: raise ValueError('Leere Zwischenseite')
        page+=1
    all_events=[e for p in pages for e in p['events']]
    if len(all_events)!=total: raise ValueError('Unvollständiger Abruf: Gesamtzahl stimmt nicht')
    return pages

def parse_pages(pages, today, days=180):
    if not isinstance(pages,list) or not pages: raise ValueError('Keine Kalenderseiten')
    first=pages[0]
    if len(pages)!=max(1,first['total_pages']): raise ValueError('Seiten fehlen')
    raw=[e for page in pages for e in page['events']]
    if len(raw)!=first['total']: raise ValueError('Termine fehlen')
    seen, events = set(), []
    end = today+timedelta(days=days)
    for e in raw:
        if not isinstance(e,dict) or type(e.get('id')) is not int: raise ValueError('Termin-ID fehlt')
        if e['id'] in seen: raise ValueError('Doppelte Termin-ID: Navigation unzuverlässig')
        seen.add(e['id'])
        if not isinstance(e.get('categories'),list): raise ValueError('Kategorien fehlen')
        slugs={c['slug'] for c in e['categories']}
        if not slugs.intersection(CATEGORIES): continue
        if slugs.intersection({'thekendienst','cafe-manager','dienstplan','cafedienst'}): continue
        if e.get('status')!='publish' or e.get('hide_from_listings'): continue
        title=plain(e['title']); source=safe_url(e['url'],source=True)
        if not title or not source: raise ValueError('Titel oder offizieller Terminlink ungültig')
        start=datetime.strptime(e['start_date'],'%Y-%m-%d %H:%M:%S')
        finish=datetime.strptime(e['end_date'],'%Y-%m-%d %H:%M:%S')
        if finish<start: raise ValueError('Terminende liegt vor Beginn')
        if not today<=start.date()<end: continue
        all_day=e.get('all_day')
        if type(all_day) is not bool: raise ValueError('Ganztagskennzeichen fehlt')
        if e.get('timezone')!='Europe/Berlin': raise ValueError('Unerwartete Zeitzone; Quelle prüfen')
        begin_utc=datetime.strptime(e['utc_start_date'],'%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        end_utc=datetime.strptime(e['utc_end_date'],'%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        if begin_utc.astimezone(BERLIN).replace(tzinfo=None)!=start or end_utc.astimezone(BERLIN).replace(tzinfo=None)!=finish:
            raise ValueError('Lokale Zeiten und UTC widersprechen sich')
        venue=e.get('venue') or {}
        if not isinstance(venue,dict): raise ValueError('Unerwarteter Veranstaltungsort')
        # Preserve event-specific venues (Mittendrin also meets outside the Sub).
        # Trashed or inconsistent source venues are not silently replaced by an assumed address.
        if '__trashed' in venue.get('slug',''):
            location='Ort bitte im Originaltermin prüfen'
        elif venue:
            label=plain(venue.get('venue',''))
            extra=[plain(str(venue.get(k,''))) for k in ('address','zip','city')]
            location=label
            for item in extra:
                if item and item.casefold() not in location.casefold(): location+=(', ' if location else '')+item
            location=location or 'Ort siehe Originaltermin'
        else: location='Ort siehe Originaltermin'
        cat='Mittendrin' if 'mittendrin' in slugs else 'Im Zentrum'
        end_date=finish.date()+timedelta(days=1) if all_day else finish.date()
        events.append(dict(id=f'sub-{e["id"]}@sub-events', date=start.date().isoformat(), title=title,
           description=plain(e.get('description','')), start=None if all_day else start.strftime('%H:%M'),
           end=None if all_day else finish.strftime('%H:%M'), endDate=end_date.isoformat(), allDay=all_day,
           startUtc=begin_utc.isoformat().replace('+00:00','Z'),endUtc=end_utc.isoformat().replace('+00:00','Z'),
           location=location,category=cat,ticket=safe_url(e.get('website','')),source=source))
    if not events: raise ValueError('Keine kommenden öffentlichen Veranstaltungen; bisherige Daten bleiben erhalten')
    return sorted(events,key=lambda e:(e['date'],e['start'] or '00:00',e['title'],e['id']))

def escape_ics(value):
    return value.replace('\\','\\\\').replace('\r','').replace('\n',r'\n').replace(';',r'\;').replace(',',r'\,')

def fold_line(line):
    chunks,current=[],''
    for char in line:
        if len((current+char).encode('utf-8'))>75: chunks.append(current); current=' '
        current+=char
    return '\r\n'.join(chunks+[current])

def make_ics(events,timestamp):
    stamp=datetime.fromisoformat(timestamp.replace('Z','+00:00')).astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    lines=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//sub-events//DE','CALSCALE:GREGORIAN','METHOD:PUBLISH','X-WR-CALNAME:Sub e. V. München','X-WR-TIMEZONE:Europe/Berlin']
    for e in events:
        desc=e['description']+'\nOriginaltermin: '+e['source']
        if e['ticket']: desc+='\nWeitere Informationen / Anmeldung: '+e['ticket']
        lines+=['BEGIN:VEVENT','UID:'+e['id'],'DTSTAMP:'+stamp]
        if e['allDay']:
            lines+=['DTSTART;VALUE=DATE:'+e['date'].replace('-',''),'DTEND;VALUE=DATE:'+e['endDate'].replace('-','')]
        else:
            for key,field in [('DTSTART','startUtc'),('DTEND','endUtc')]:
                lines+=[key+':'+datetime.fromisoformat(e[field].replace('Z','+00:00')).strftime('%Y%m%dT%H%M%SZ')]
        lines+=['SUMMARY:'+escape_ics(e['title']),'DESCRIPTION:'+escape_ics(desc),'LOCATION:'+escape_ics(e['location']),'URL:'+e['source'],'END:VEVENT']
    return ('\r\n'.join(fold_line(s) for s in lines+['END:VCALENDAR'])+'\r\n').encode('utf-8')

def validate_change(events,old,today,days):
    last=(today+timedelta(days=days)).isoformat()
    before=[e for e in old.get('events',[]) if today.isoformat()<=e['date']<last]
    if len(before)>=6 and len(events)<len(before)*0.5: raise ValueError('Mehr als 50 Prozent der Termine fehlen; Quelle manuell prüfen')

def write_json(path,payload):
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def update(site,loader=None,now=None,allow_stale=False,days=180,snapshot=None):
    now=now or datetime.now(timezone.utc)
    today=now.astimezone(BERLIN).date()
    timestamp=now.isoformat(timespec='seconds').replace('+00:00','Z')
    data=site/'data'; data.mkdir(parents=True,exist_ok=True)
    target,calendar=data/'events.json',site/'events.ics'
    old=json.loads(target.read_text(encoding='utf-8')) if target.exists() else {}
    try:
        pages=loader() if loader else fetch_pages(today,days)
        events=parse_pages(pages,today,days)
        validate_change(events,old,today,days)
        payload=dict(source=SOURCE,updatedAt=timestamp,fromDate=today.isoformat(),throughDate=(today+timedelta(days=days-1)).isoformat(),events=events)
        ics=make_ics(events,timestamp)
    except Exception as error:
        write_json(data/'status.json',dict(ok=False,checkedAt=timestamp,message='Abruf fehlgeschlagen. Bisheriger Datenstand bleibt erhalten.'))
        print(f'::warning::{type(error).__name__}: {error}',file=sys.stderr)
        if not (allow_stale and old.get('events') and calendar.exists()): raise
        return False
    # Writing errors must stop the workflow before commit/deployment.
    write_json(data/'events.json.tmp',payload)
    (site/'events.ics.tmp').write_bytes(ics)
    os.replace(site/'events.ics.tmp',calendar); os.replace(data/'events.json.tmp',target)
    write_json(data/'status.json',dict(ok=True,checkedAt=timestamp,message='Abruf erfolgreich'))
    if snapshot: write_json(snapshot,pages)
    print(f'{len(events)} öffentliche Termine, {len(pages)} vollständig geprüfte API-Seiten')
    return True

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--site',type=Path,default=Path('site')); p.add_argument('--allow-stale',action='store_true')
    p.add_argument('--snapshot',type=Path,help='Erfolgreich abgerufene Seiten für reproduzierbare Tests speichern')
    p.add_argument('--days',type=int,default=180)
    a=p.parse_args()
    if not 1<=a.days<=366: p.error('--days muss zwischen 1 und 366 liegen')
    try: update(a.site,allow_stale=a.allow_stale,days=a.days,snapshot=a.snapshot)
    except Exception as error: print(f'Abbruch: {error}',file=sys.stderr); sys.exit(1)
