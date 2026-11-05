'use strict';
const $ = s => document.querySelector(s);
let payload, selected = 'Alle', failedCheck = false, localFallback = false;
const dateFormat = new Intl.DateTimeFormat('de-DE', {timeZone:'Europe/Berlin', day:'2-digit', month:'long', year:'numeric', hour:'2-digit', minute:'2-digit'});
const monthFormat = new Intl.DateTimeFormat('de-DE', {month:'long', year:'numeric', timeZone:'Europe/Berlin'});
const weekday = new Intl.DateTimeFormat('de-DE', {weekday:'short', timeZone:'Europe/Berlin'});
function element(tag, text, cls) { const node = document.createElement(tag); if (text) node.textContent = text; if (cls) node.className = cls; return node; }
function link(text, href) {
  const a = element('a', text);
  try { const url = new URL(href, location.href); if (url.protocol !== 'https:' && url.origin !== location.origin) return a; a.href = url.href; } catch { return a; }
  a.target = '_blank'; a.rel = 'noopener noreferrer'; return a;
}
function download(event) {
  const url = URL.createObjectURL(new Blob([Sub.single(event)], {type:'text/calendar;charset=utf-8'}));
  const a = element('a'); a.href = url; a.download = 'sub-' + event.date + '.ics'; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 10000);
}
function render() {
  if (!payload) return;
  const list = Sub.filtered(payload.events, $('#query').value, selected, $('#range').value);
  $('#events').replaceChildren(); $('#count').textContent = `${list.length} ${list.length === 1 ? 'Termin' : 'Termine'}`;
  let month = '';
  for (const event of list) {
    const day = new Date(event.date + 'T12:00:00Z');
    if (month !== event.date.slice(0,7)) { month = event.date.slice(0,7); $('#events').append(element('div', monthFormat.format(day), 'month')); }
    const article = element('article', '', 'event');
    const date = element('div', event.date.slice(8), 'day'); date.append(element('small', weekday.format(day))); article.append(date);
    const content = element('div'); content.append(element('span', event.category, 'tag'), element('h3', event.title));
    content.append(element('p', event.allDay ? 'Ganztägig' : `${event.start}–${event.end} Uhr${event.endDate !== event.date ? ' · Ende am ' + event.endDate.split('-').reverse().join('.') : ''}`, 'times'));
    content.append(element('p', event.location));
    if (event.description) content.append(element('p', event.description));
    const actions = element('div', '', 'event-links');
    if (event.ticket) actions.append(link('Information / Anmeldung ↗', event.ticket));
    const save = element('button', 'Termin speichern ↓'); save.type = 'button'; save.addEventListener('click', () => download(event));
    actions.append(save, link('Originaltermin ↗', event.source)); content.append(actions); article.append(content, element('div', event.allDay ? 'Ganztägig' : event.start, 'event-side')); $('#events').append(article);
  }
  if (!list.length) $('#events').append(element('p', 'Keine passenden Termine. Versuche einen anderen Zeitraum oder setze die Filter zurück.', 'empty'));
}
function categories() {
  $('#categories').replaceChildren();
  for (const name of ['Alle', ...new Set(payload.events.map(e => e.category).sort())]) {
    const b = element('button', name); b.type = 'button'; b.setAttribute('aria-pressed', String(selected === name));
    b.addEventListener('click', () => { selected = name; categories(); render(); }); $('#categories').append(b);
  }
}
function showStatus() {
  const age = Date.now() - Date.parse(payload.updatedAt);
  const warning = failedCheck || localFallback || !navigator.onLine || age > 48 * 3600000;
  $('#status').classList.toggle('warning', warning);
  $('#status').textContent = `${!navigator.onLine ? 'Offline · ' : localFallback ? 'Gespeicherte Daten · ' : ''}Datenstand: ${dateFormat.format(new Date(payload.updatedAt))} Uhr.${failedCheck ? ' Letzter Abruf fehlgeschlagen; bisherige Termine bleiben erhalten.' : age > 48 * 3600000 ? ' Seit mehr als 48 Stunden nicht aktualisiert.' : ''} Angaben beim Veranstalter prüfen.`;
}
function valid(p) { return p && !Number.isNaN(Date.parse(p.updatedAt)) && Array.isArray(p.events) && p.events.length && p.events.every(e => typeof e.title === 'string' && /^\d{4}-\d\d-\d\d$/.test(e.date) && (e.allDay || e.start && e.end) && typeof e.description === 'string' && typeof e.location === 'string'); }
async function load() {
  $('#refresh').disabled = true;
  try {
    const response = await fetch('./data/events.json', {cache:'no-store', signal:AbortSignal.timeout(12000)});
    if (!response.ok) throw Error('HTTP ' + response.status);
    const next = await response.json(); if (!valid(next)) throw Error('Ungültige Daten');
    payload = next; localFallback = false;
    try { localStorage.setItem('sub-events-v1', JSON.stringify(payload)); } catch { /* Optional storage may be disabled. */ }
  } catch {
    localFallback = true;
    if (!payload) { try { const cached = JSON.parse(localStorage.getItem('sub-events-v1')); if (valid(cached)) payload = cached; } catch {} }
  }
  if (payload) {
    try { const r = await fetch('./data/status.json', {cache:'no-store', signal:AbortSignal.timeout(5000)}); if (!r.ok) throw Error(); const s = await r.json(); failedCheck = s.ok !== true; } catch { failedCheck = true; }
    categories(); render(); showStatus();
  } else { $('#status').textContent = 'Daten konnten nicht geladen werden. Bitte Internetverbindung prüfen und erneut aktualisieren.'; $('#status').classList.add('warning'); }
  $('#refresh').disabled = false;
}
$('#query').addEventListener('input', render); $('#range').addEventListener('change', render); $('#refresh').addEventListener('click', load);
$('#reset').addEventListener('click', () => { selected = 'Alle'; $('#query').value = ''; $('#range').value = 'all'; if (payload) { categories(); render(); } });
const feed = new URL('./events.ics', location.href); $('#feed').value = feed.href;
if (feed.protocol === 'https:') $('#subscribe').href = feed.href.replace(/^https:/, 'webcal:');
$('#copy').addEventListener('click', async () => { try { await navigator.clipboard.writeText(feed.href); $('#copy-status').textContent = 'Adresse kopiert.'; } catch { $('#feed').focus(); $('#feed').select(); $('#copy-status').textContent = 'Bitte die markierte Adresse mit Strg+C kopieren.'; } });
let installPrompt;
window.addEventListener('beforeinstallprompt', e => { e.preventDefault(); installPrompt = e; $('#install').hidden = false; });
$('#install').addEventListener('click', async () => { if (installPrompt) { await installPrompt.prompt(); installPrompt = null; $('#install').hidden = true; } });
window.addEventListener('online', load); window.addEventListener('offline', () => { if (payload) showStatus(); });
document.addEventListener('visibilitychange', () => { if (!document.hidden) { if (payload) render(); load(); } });
if ('serviceWorker' in navigator) navigator.serviceWorker.register('./sw.js').catch(() => {});
load();
