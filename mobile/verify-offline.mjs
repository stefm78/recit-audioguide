import { access, readFile, readdir } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = resolve(fileURLToPath(new URL('.', import.meta.url)));
const www = resolve(here, 'www');
const slug = process.argv[2] || 'seville-discovery';
const synthetic = new URL(`https://local/recit-audioguide/data/${slug}/series.json`);
const series = JSON.parse(await readFile(join(www,'data',slug,'series.json'),'utf8'));
const errors=[];

function localFrom(ref){
  const u=new URL(ref,synthetic);
  if(u.origin!=='https://local' || !u.pathname.startsWith('/recit-audioguide/')) return null;
  return join(www, decodeURIComponent(u.pathname.slice('/recit-audioguide/'.length)));
}
async function mustExist(label,ref){
  const p=localFrom(ref); if(!p){ errors.push(`${label}: external ${ref}`); return; }
  try{ await access(p); }catch{ errors.push(`${label}: missing ${p.slice(www.length+1)}`); }
}
for(const e of series.episodes||[]){
  if(!e.audio_url) errors.push(`${e.id}: audio_url missing`); else await mustExist(`${e.id}.audio`,e.audio_url);
  if(e.transcript_url) await mustExist(`${e.id}.transcript`,e.transcript_url);
  for(const x of e.extras||[]){ if(x.audio_url) await mustExist(`${x.id||x.title}.audio`,x.audio_url); }
}
if(series.visit?.route_map_url) await mustExist('visit.route_map',series.visit.route_map_url);

async function walk(dir){
  const out=[]; for(const ent of await readdir(dir,{withFileTypes:true})){ const p=join(dir,ent.name); if(ent.isDirectory()) out.push(...await walk(p)); else out.push(p); } return out;
}
for(const p of await walk(www)){
  if(!p.endsWith('.html')) continue;
  const s=await readFile(p,'utf8');
  if(/<(script|link)\b[^>]*(src|href)=["']https?:\/\//i.test(s)) errors.push(`remote subresource in ${p.slice(www.length+1)}`);
}
if(errors.length){ console.error(errors.join('\n')); process.exit(2); }
console.log(`Offline core verified for ${slug}: all narrated assets local; no remote HTML subresources.`);
