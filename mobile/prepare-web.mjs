import { cp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = resolve(fileURLToPath(new URL('.', import.meta.url)));
const source = resolve(here, '..', 'dist');
const target = resolve(here, 'www');

await rm(target, { recursive: true, force: true });
await mkdir(target, { recursive: true });
await cp(source, target, { recursive: true });

async function walk(dir){
  const out=[];
  for(const ent of await readdir(dir,{withFileTypes:true})){
    const p=join(dir,ent.name);
    if(ent.isDirectory()) out.push(...await walk(p)); else out.push(p);
  }
  return out;
}

for(const file of await walk(target)){
  if(!file.endsWith('.html')) continue;
  let html=await readFile(file,'utf8');
  html=html
    .replace(/\s*<link\b[^>]*href=["']https?:\/\/[^>]*>\s*/gi,'\n')
    .replace(/\s*<script\b[^>]*src=["']https?:\/\/[^>]*><\/script>\s*/gi,'\n')
    .replace('</head>','  <meta name="recit-mobile-shell" content="offline-first">\n</head>');
  await writeFile(file,html);
}
console.log(`Prepared self-contained mobile Web payload from ${source} -> ${target}`);
