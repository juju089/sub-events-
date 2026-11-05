import copy
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, date, timezone
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlparse, parse_qs
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import update_events as u
PAGES=json.loads((Path(__file__).parent/'fixtures/api-pages.json').read_text(encoding='utf-8'))
TODAY=date(2026,11,5)
NOW=datetime(2026,11,5,13,tzinfo=timezone.utc)
TARGET=next(i for i,e in enumerate(PAGES[0]['events']) if e['start_date'].startswith('2026-11-05'))

class SourceTests(unittest.TestCase):
    def test_real_source_all_four_pages(self):
        events=u.parse_pages(PAGES,TODAY)
        self.assertEqual(len(events),187)
        self.assertEqual(len({e['id'] for e in events}),187)
        self.assertEqual(sum(e['category']=='Mittendrin' for e in events),6)
        self.assertEqual(sum(e['allDay'] for e in events),1)
        first=next(e for e in events if e['title']=='Queeramnesty')
        self.assertEqual((first['date'],first['start'],first['end']),('2026-11-05','19:15','21:00'))
        self.assertTrue(any(e['title']=='Gay & Grey' for e in events))
        self.assertTrue(any('Café Glück' in e['location'] for e in events))
        self.assertTrue(any(e['location']=='Ort siehe Originaltermin' for e in events))
    def test_pagination_rebuilds_category_and_date_query(self):
        urls=[]
        def request(url):
            urls.append(url);return PAGES[len(urls)-1]
        pages=u.fetch_pages(TODAY,requester=request)
        self.assertEqual(len(pages),4)
        for index,url in enumerate(urls,1):
            q=parse_qs(urlparse(url).query)
            self.assertEqual(q['categories'],['16,14'])
            self.assertEqual(q['page'],[str(index)])
            self.assertEqual(q['per_page'],['50'])
            self.assertIn('start_date',q);self.assertIn('end_date',q)
    def test_partial_page_failure_and_changing_total_abort(self):
        def request(url):
            page=int(parse_qs(urlparse(url).query)['page'][0])
            if page==2: raise TimeoutError()
            return PAGES[0]
        with self.assertRaises(TimeoutError): u.fetch_pages(TODAY,requester=request)
        changed=copy.deepcopy(PAGES);changed[1]['total']+=1
        with self.assertRaises(ValueError): u.fetch_pages(TODAY,requester=lambda url:changed[int(parse_qs(urlparse(url).query)['page'][0])-1])
    def test_missing_duplicate_and_invalid_events_rejected(self):
        with self.assertRaises(ValueError): u.parse_pages(PAGES[:1],TODAY)
        changed=copy.deepcopy(PAGES);changed[1]['events'][0]=changed[0]['events'][0]
        with self.assertRaises(ValueError): u.parse_pages(changed,TODAY)
        for key,value in [('start_date','invalid'),('end_date','2020-01-01 00:00:00'),('utc_start_date','2026-11-05 00:00:00'),('timezone','UTC'),('url','javascript:alert(1)')]:
            changed=copy.deepcopy(PAGES);changed[0]['events'][TARGET][key]=value
            with self.assertRaises(ValueError): u.parse_pages(changed,TODAY)
    def test_staff_entries_not_included_and_html_is_plain(self):
        changed=copy.deepcopy(PAGES);changed[0]['events'][TARGET]['categories']=[{'slug':'thekendienst'}]
        self.assertEqual(len(u.parse_pages(changed,TODAY)),186)
        self.assertEqual(u.plain('<p>Hallo &amp; willkommen<br>hier</p><script>bad()</script>'),'Hallo & willkommen hier')
        self.assertIsNone(u.safe_url('javascript:alert(1)'))
    def test_stable_ids_and_calendar_time_end_and_all_day(self):
        events=u.parse_pages(PAGES,TODAY)
        self.assertTrue(all(e['id'].startswith('sub-') for e in events))
        raw=u.make_ics(events,NOW.isoformat());unfolded=raw.decode().replace('\r\n ','')
        self.assertEqual(unfolded.count('BEGIN:VEVENT'),187)
        self.assertIn('DTSTART:20261105T181500Z',unfolded)
        self.assertIn('DTEND:20261105T200000Z',unfolded)
        self.assertIn('DTSTART;VALUE=DATE:',unfolded)
        self.assertIn('DTEND;VALUE=DATE:',unfolded)
        # Preserve the exact date range of the official per-event ICS, even though
        # the JSON all-day timestamps cross into the early morning of the next day.
        official=(Path(__file__).parent/'fixtures/original-allday.ics').read_text(encoding='utf-8')
        all_day=next(e for e in events if e['allDay'])
        self.assertIn('DTSTART;VALUE=DATE:'+all_day['date'].replace('-',''),official)
        self.assertIn('DTEND;VALUE=DATE:'+all_day['endDate'].replace('-',''),official)
        self.assertTrue(all(len(line)<=75 for line in raw.split(b'\r\n')))
        self.assertNotIn(b'\n',raw.replace(b'\r\n',b''))
        self.assertEqual(u.escape_ics('a,b;c\\d\ne'),'a\\,b\\;c\\\\d\\ne')
    def test_empty_old_source_and_mass_loss_rejected(self):
        with self.assertRaises(ValueError):u.parse_pages(PAGES,date(2029,1,1))
        events=u.parse_pages(PAGES,TODAY)
        with self.assertRaises(ValueError):u.validate_change(events[:5],{'events':events},TODAY,180)
    def test_network_three_attempts(self):
        with patch.object(u,'urlopen',side_effect=TimeoutError),patch.object(u.time,'sleep'):
            with self.assertRaises(RuntimeError):u.request_json(u.API)
            self.assertEqual(u.urlopen.call_count,3)

class PreserveTests(unittest.TestCase):
    def setUp(self):
        for c in [redirect_stderr(StringIO()),redirect_stdout(StringIO())]:
            c.__enter__();self.addCleanup(c.__exit__,None,None,None)
    def test_failed_fetch_bad_json_missing_page_keep_both_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            site=Path(tmp);u.update(site,lambda:PAGES,NOW)
            before=[(site/p).read_bytes() for p in ['data/events.json','events.ics']]
            for loader in [lambda:(_ for _ in ()).throw(TimeoutError()),lambda:[],lambda:PAGES[:1]]:
                self.assertFalse(u.update(site,loader,NOW,allow_stale=True))
                self.assertEqual(before,[(site/p).read_bytes() for p in ['data/events.json','events.ics']])
                self.assertFalse(json.loads((site/'data/status.json').read_text())['ok'])
            self.assertTrue(u.update(site,lambda:PAGES,NOW,allow_stale=True))
            self.assertTrue(json.loads((site/'data/status.json').read_text())['ok'])
    def test_no_previous_data_is_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):u.update(Path(tmp),lambda:[],NOW,allow_stale=True)
            self.assertFalse((Path(tmp)/'events.ics').exists())
    def test_disk_failure_is_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            site=Path(tmp);u.update(site,lambda:PAGES,NOW)
            with patch.object(u.os,'replace',side_effect=OSError):
                with self.assertRaises(OSError):u.update(site,lambda:PAGES,NOW,allow_stale=True)

if __name__=='__main__':unittest.main()
