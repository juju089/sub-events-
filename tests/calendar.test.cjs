const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const C = require('../site/calendar.js');
const events = [
  {id:'a',date:'2026-11-05',title:'Schach im Sub',description:'Gemeinsam spielen',category:'Im Zentrum',start:'21:00',source:'https://kalender.subonline.org/events-im-zentrum/'},
  {id:'b',date:'2026-11-10',title:'Mittendrin',description:'Begegnung',category:'Mittendrin',start:'19:30',source:'https://kalender.subonline.org/events-im-zentrum/'},
  {id:'c',date:'2026-11-04',title:'Treffen',description:'Community',category:'Im Zentrum',source:'https://kalender.subonline.org/events-im-zentrum/'}
];
test('search, category, dates and reset ranges', () => {
  assert.equal(C.filtered(events,'','Alle','all','2026-11-05').length,2);
  assert.equal(C.filtered(events,'GEMEINSAM','Alle','all','2026-11-05')[0].id,'a');
  assert.equal(C.filtered(events,'','Mittendrin','week','2026-11-05')[0].id,'b');
  assert.equal(C.filtered(events,'','Alle','today','2026-11-05').length,1);
  assert.equal(C.filtered(events,'','Alle','past','2026-11-05')[0].id,'c');
  assert.equal(C.filtered(events,'absent','Alle','all','2026-11-05').length,0);
  assert.equal(C.filtered(events,'','Alle','month','2026-10-01').length,0);
});
test('Berlin date works independently of device timezone', () => assert.equal(C.today(new Date('2026-11-04T23:30:00Z')), '2026-11-05'));
test('single download uses authoritative UTC, real end, all-day dates and escaping', () => {
  const fixture = JSON.parse(fs.readFileSync('tests/fixtures/events.json','utf8')).events;
  const e = fixture.find(e=>e.title==='Queeramnesty');
  const result = C.single({...e,title:'Ä'.repeat(100)+',;\\'});
  assert.match(result,/DTSTART:20261105T181500Z/);
  assert.match(result,/DTEND:20261105T200000Z/);
  assert.ok(result.includes(`UID:${e.id}`));
  assert.ok(result.split('\r\n').every(line=>Buffer.byteLength(line)<=75));
  assert.ok(result.replace(/\r\n /g,'').includes('\\,\\;\\\\'));
  assert.match(C.single(fixture.find(e=>e.allDay)),/DTSTART;VALUE=DATE:/);
});
test('manifest scope and all shell assets exist under project path', () => {
  const manifest = JSON.parse(fs.readFileSync('site/manifest.webmanifest'));
  assert.equal(manifest.start_url,'./'); assert.equal(manifest.scope,'./');
  for(const icon of manifest.icons) assert.ok(fs.existsSync('site/'+icon.src));
  const html = fs.readFileSync('site/index.html','utf8');
  for(const match of html.matchAll(/(?:href|src)="\.\/([^"#]+)"/g)) assert.ok(fs.existsSync('site/'+match[1]),match[1]);
});
test('service worker retains project scope, caches fallback and bypasses ICS', async () => {
  const handlers = {}, stored = new Map(); let offline = false;
  const cache = {addAll:async paths=>{for(const p of paths) stored.set(new URL(p,'https://example.test/sub-events/').href,new Response('shell'));},put:async(req,res)=>stored.set(typeof req==='string'?req:req.url,res),match:async req=>stored.get(typeof req==='string'?req:req.href||req.url)};
  const context = {URL,Response,Error,caches:{open:async()=>cache,keys:async()=>[],delete:async()=>true},fetch:async()=>{if(offline)throw Error();return new Response('network');},self:{location:new URL('https://example.test/sub-events/sw.js'),addEventListener:(name,fn)=>handlers[name]=fn,skipWaiting(){},clients:{claim:async()=>{}}}};
  vm.runInNewContext(fs.readFileSync('site/sw.js','utf8'),context);
  await new Promise(resolve=>handlers.install({waitUntil:p=>p.then(resolve)}));
  async function request(path,mode='cors') { let promise; handlers.fetch({request:{method:'GET',url:'https://example.test/sub-events/'+path,mode},respondWith:p=>promise=p}); return promise; }
  assert.equal(await (await request('data/events.json')).text(),'network');
  offline=true;
  assert.equal(await (await request('data/events.json')).text(),'network');
  assert.equal(await (await request('unknown','navigate')).text(),'shell');
  assert.equal(await request('events.ics'),undefined);
});
