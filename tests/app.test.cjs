/* App-level integration tests with a small DOM double. Browser rendering is separate. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const C = require('../site/calendar.js');
const original = JSON.parse(fs.readFileSync('tests/fixtures/events.json', 'utf8'));
class Element {
  constructor(tag) { this.tag = tag; this.children = []; this.textContent = ''; this.value = ''; this.attributes = {}; this.listeners = {}; this.classes = new Set(); this.classList = {add:x=>this.classes.add(x),toggle:(x,v)=>v?this.classes.add(x):this.classes.delete(x)}; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute(k,v) { this.attributes[k]=v; }
  addEventListener(k,v) { this.listeners[k]=v; }
  focus() {} select() {} remove() {} click() {}
}
async function launch({offline=false, saved=null, errorStatus=false, blockedStorage=false}={}) {
  const nodes = new Map([...fs.readFileSync('site/index.html','utf8').matchAll(/id="([^"]+)"/g)].map(m=>['#'+m[1],new Element('div')]));
  nodes.get('#range').value='all';
  const storage = new Map(saved ? [['sub-events-v1',JSON.stringify(saved)]] : []);
  const fixedCalendar = {...C,filtered:(events,query,type,range)=>C.filtered(events,query,type,range,'2026-11-05')};
  const context = {Intl,Date,URL,Blob,TextEncoder,setTimeout,AbortSignal,Sub:fixedCalendar,
    location:{href:'https://juju089.github.io/sub-events/',origin:'https://juju089.github.io'},
    navigator:{onLine:!offline,clipboard:{writeText:async()=>{}}},
    localStorage:{getItem:k=>{if(blockedStorage)throw Error();return storage.get(k)||null;},setItem:(k,v)=>{if(blockedStorage)throw Error();storage.set(k,v);}},
    document:{querySelector:s=>nodes.get(s),createElement:tag=>new Element(tag),body:new Element('body'),addEventListener(){}},
    window:{addEventListener(){}},
    fetch:async url=>{if(offline)throw Error('offline');return {ok:true,json:async()=>url.includes('status')?{ok:!errorStatus}:original};}};
  vm.runInNewContext(fs.readFileSync('site/app.js','utf8'),context);
  await new Promise(resolve=>setImmediate(resolve));
  return nodes;
}
test('app fetches real payload, renders safely and wires filtering and reset', async()=>{
  const nodes = await launch();
  assert.equal(nodes.get('#refresh').disabled,false);
  assert.ok(nodes.get('#events').children.some(n=>n.tag==='article'));
  assert.match(nodes.get('#status').textContent,/Datenstand/);
  assert.equal(nodes.get('#feed').value,'https://juju089.github.io/sub-events/events.ics');
  assert.equal(nodes.get('#subscribe').href,'webcal://juju089.github.io/sub-events/events.ics');
  nodes.get('#query').value='xxxxxxxx-no-event'; nodes.get('#query').listeners.input();
  assert.equal(nodes.get('#count').textContent,'0 Termine');
  nodes.get('#reset').listeners.click();
  assert.notEqual(nodes.get('#count').textContent,'0 Termine');
  const quiz = nodes.get('#categories').children.find(n=>n.textContent==='Im Zentrum'); quiz.listeners.click();
  assert.equal(nodes.get('#categories').children.find(n=>n.textContent==='Im Zentrum').attributes['aria-pressed'],'true');
});
test('saved data survives offline reload, missing storage and server warnings', async()=>{
  const nodes = await launch({offline:true,saved:original});
  assert.match(nodes.get('#status').textContent,/Offline/);
  assert.ok(nodes.get('#events').children.some(n=>n.tag==='article'));
  const empty = await launch({offline:true,blockedStorage:true});
  assert.match(empty.get('#status').textContent,/konnten nicht geladen/);
  assert.equal(empty.get('#refresh').disabled,false);
  const warned = await launch({errorStatus:true,blockedStorage:true});
  assert.match(warned.get('#status').textContent,/Letzter Abruf fehlgeschlagen/);
  assert.ok(warned.get('#events').children.some(n=>n.tag==='article'));
});
