import {MARKETS,assign,parseItem} from './normalize.js';
import {initializeApp} from 'https://www.gstatic.com/firebasejs/11.10.0/firebase-app.js';
import {getAuth,signInAnonymously,onAuthStateChanged} from 'https://www.gstatic.com/firebasejs/11.10.0/firebase-auth.js';
import {getDatabase,ref,onValue,set,push,remove,get} from 'https://www.gstatic.com/firebasejs/11.10.0/firebase-database.js';
const $=id=>document.getElementById(id);const cfg=window.NATUR_FIREBASE_CONFIG;
const ready=cfg&&cfg.apiKey&&!cfg.apiKey.startsWith('HIER_')&&cfg.databaseURL&&!cfg.databaseURL.includes('HIER_');
let db,auth,listId=null,items=[],offers=[],unsubscribe=null,undoItem=null,undoTimer,locked=false;
function status(s){$('status').textContent=s}function error(e){status('Fehler: '+(e?.code||e?.message||String(e)));console.error(e)}
const STORAGE_KEY='natur.activeList.v2';
function validId(id){return typeof id==='string'&&/^[a-f0-9]{64}$/.test(id)?id:null}
function cleanId(){let m=location.hash.match(/^#list=([a-f0-9]{64})$/);return validId(m?.[1])}
function rememberedId(){try{return validId(localStorage.getItem(STORAGE_KEY))}catch{return null}}
function rememberId(id){try{localStorage.setItem(STORAGE_KEY,id)}catch(e){console.warn('Lokaler Speicher nicht verfügbar',e)}}
function restoreList(){const id=cleanId()||rememberedId();if(!cleanId()&&id)location.replace(`${location.pathname}${location.search}#list=${id}`);return id}
function idFromInvitation(value){try{const url=new URL(value.trim(),location.href);if(url.origin!==location.origin||url.pathname!==location.pathname)return null;const m=url.hash.match(/^#list=([a-f0-9]{64})$/);return validId(m?.[1])}catch{return validId(value.trim())}}

function randomId(){let bytes=crypto.getRandomValues(new Uint8Array(32));return [...bytes].map(b=>b.toString(16).padStart(2,'0')).join('')}
function link(){return `${location.origin}${location.pathname}#list=${listId}`}
function show(){listId=restoreList();if(listId)rememberId(listId);$('setup').hidden=!!listId;$('workspace').hidden=!listId;$('share').hidden=!listId;if(unsubscribe){unsubscribe();unsubscribe=null}if(!listId)return;status('Verbinde ...');unsubscribe=onValue(ref(db,`lists/${listId}/items`),snapshot=>{items=Object.entries(snapshot.val()||{}).map(([id,v])=>({id,...v}));render();status('Liste synchronisiert')},error)}
async function loadOffers(){try{let r=await fetch('./offers.json?ts='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);let j=await r.json();offers=Array.isArray(j.offers)?j.offers:[];render();let time=j.updatedAt?new Date(j.updatedAt).toLocaleString('de-DE',{timeZone:'Europe/Berlin'}):'noch nie';status(`Angebotsdaten: ${time} · ${offers.length} Einträge (kein Live-Prospektabruf)`)}catch(e){offers=[];render();error(e)}}
function render(){let mapped=assign(items,offers),wrap=$('groups');wrap.replaceChildren();for(let [marketId,marketName] of [...MARKETS,[null,'Allgemein']]){let arr=mapped.filter(i=>i.displayMarket===marketId);if(!arr.length)continue;let sec=document.createElement('section');sec.className='group';let h=document.createElement('div');h.className='group-title';let name=document.createElement('span');name.textContent=marketName;let count=document.createElement('span');count.className='count';count.textContent=arr.length+' Produkte';h.append(name,count);sec.append(h);for(let i of arr){let row=document.createElement('div');row.className='item';row.draggable=true;row.dataset.id=i.id;let tile=document.createElement('span');tile.className='letter';tile.textContent=i.name[0]?.toUpperCase()||'?';let body=document.createElement('div');body.className='item-body';let label=document.createElement('div');label.className='item-name';label.textContent=i.name;body.append(label);if(i.deal){let deal=document.createElement('span');deal.className='deal';deal.textContent=`${i.deal.price.toLocaleString('de-DE',{style:'currency',currency:'EUR'})} · Angebot bis ${new Date(i.deal.validTo+'T12:00:00').toLocaleDateString('de-DE')}`;body.append(deal)}let edit=document.createElement('button');edit.className='edit';edit.textContent='⋯';edit.setAttribute('aria-label','Markt ändern für '+i.name);edit.onclick=e=>{e.stopPropagation();selectMarket(i)};row.append(tile,body,edit);row.addEventListener('click',e=>{if(!locked&&!e.target.closest('button'))deleteItem(i)});row.addEventListener('dragstart',e=>{e.dataTransfer.setData('text/plain',i.id)});let hold;row.addEventListener('touchstart',e=>{hold=setTimeout(()=>{locked=true;selectMarket(i);setTimeout(()=>locked=false,500)},650)},{passive:true});for(let ev of ['touchmove','touchend','touchcancel'])row.addEventListener(ev,()=>clearTimeout(hold),{passive:true});sec.append(row)}sec.addEventListener('dragover',e=>e.preventDefault());sec.addEventListener('drop',async e=>{e.preventDefault();let id=e.dataTransfer.getData('text/plain');if(items.some(i=>i.id===id))await patchMarket(id,marketId)});wrap.append(sec)}}
async function patchMarket(id,market){let base=ref(db,`lists/${listId}/items/${id}`),snapshot=await get(base);if(!snapshot.exists())return;await set(base,{...snapshot.val(),market:market||null,manual:!!market})}
function selectMarket(i){let d=$('marketDialog'),buttons=$('marketButtons');buttons.replaceChildren();for(let [id,name] of [[null,'Allgemein'],...MARKETS]){let b=document.createElement('button');b.type='button';b.textContent=name;b.onclick=async()=>{d.close();try{await patchMarket(i.id,id)}catch(e){error(e)}};buttons.append(b)}d.showModal()}
async function deleteItem(i){try{await remove(ref(db,`lists/${listId}/items/${i.id}`));undoItem={...i};$('toastText').textContent=i.name+' entfernt';$('toast').hidden=false;clearTimeout(undoTimer);undoTimer=setTimeout(()=>{$('toast').hidden=true;undoItem=null},5500)}catch(e){error(e)}}
$('undo').onclick=async()=>{if(!undoItem)return;let i=undoItem;undoItem=null;$('toast').hidden=true;try{let r=ref(db,`lists/${listId}/items/${i.id}`);if(!(await get(r)).exists()){let {id,displayMarket,deal,...rest}=i;await set(r,rest)}}catch(e){error(e)}};
$('addForm').onsubmit=async e=>{e.preventDefault();let s=$('product').value.trim();if(!s)return;let i=parseItem(s);if(!i.name)return;try{await set(push(ref(db,`lists/${listId}/items`)),{name:i.name,market:i.market,manual:i.manual,createdAt:Date.now()});$('product').value=''}catch(e){error(e)}};
// Bei geöffnetem Fenster alle 60 Minuten und bei Rückkehr zur App aktualisieren.
// Der Firebase-onValue-Listener ruft render() zusätzlich bei jeder Listenänderung auf.
let refreshInFlight=null;
function refreshOffers(){
  if(refreshInFlight)return refreshInFlight;
  refreshInFlight=loadOffers().finally(()=>{refreshInFlight=null});
  return refreshInFlight;
}
$('refresh').onclick=refreshOffers;
window.addEventListener('focus',()=>{if(listId)refreshOffers()});
document.addEventListener('visibilitychange',()=>{if(!document.hidden&&listId)refreshOffers()});
window.addEventListener('online',()=>{if(listId)refreshOffers()});
setInterval(()=>{if(!document.hidden&&listId)refreshOffers();else if(listId)render()},60*60*1000);

$('joinForm').onsubmit=e=>{e.preventDefault();const id=idFromInvitation($('joinLink').value);if(!id){$('setupHint').textContent='Bitte den vollständigen Einladungslink dieser App einfügen.';return}rememberId(id);location.hash='list='+id;if(auth?.currentUser)show()};
$('share').onclick=async()=>{let u=link();try{if(navigator.share)await navigator.share({title:'Natur Einkaufsliste',url:u});else{await navigator.clipboard.writeText(u);status('Einladungslink kopiert')}}catch(e){if(e.name!=='AbortError'){window.prompt('Diesen Link kopieren:',u)}}};
$('create').onclick=async()=>{if(!ready)return $('setupHint').textContent='Zuerst docs/config.js einrichten.';if(!auth.currentUser)return $('setupHint').textContent='Verbindung wird aufgebaut ...';let id=randomId();try{await set(ref(db,`lists/${id}`),{createdAt:Date.now()});rememberId(id);location.hash='list='+id}catch(e){$('setupHint').textContent='Fehler: '+(e.code||e.message)}};
window.addEventListener('hashchange',()=>{if(auth.currentUser)show()});
if(!ready){$('setupHint').textContent='Firebase ist noch nicht eingerichtet. Bitte docs/config.js nach Anleitung erstellen.'}else{try{let app=initializeApp(cfg);auth=getAuth(app);db=getDatabase(app);onAuthStateChanged(auth,u=>{if(u){show();refreshOffers()}else signInAnonymously(auth).catch(error)});signInAnonymously(auth).catch(error)}catch(e){$('setupHint').textContent=e.message}}
if('serviceWorker' in navigator)navigator.serviceWorker.register('./service-worker.js').catch(console.warn);
