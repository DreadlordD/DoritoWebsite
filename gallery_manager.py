#!/usr/bin/env python3
"""
gallery_manager.py  -  the Dorito gallery manager, with a window that looks like your gallery.

SET UP
  Put this file next to script.js and add_to_gallery.py (top of your repo folder).
  You need Python installed. Nothing else to install.

RUN IT
  python gallery_manager.py          (Mac/Linux: python3 gallery_manager.py)
  Your web browser opens a page that looks like your gallery. It only runs on YOUR computer
  (nothing is uploaded anywhere). Close the black window, or press Ctrl+C in it, when you're done.

WHAT YOU CAN DO IN THE PAGE
  - Click a folder to open it. Make, rename and delete folders.
  - Add pictures: press "Add pictures" or just drag pictures from your computer onto the window.
  - Click pictures to select them (click again to deselect), then Rename, Move or Delete.
  - "Rename files" changes the FILE names on disk: it numbers the selected pictures (or all of them if none are
    selected) as image_00, image_01... in the order shown. You choose the prefix, start number and digits.
  - Rename shows one box per selected picture, so you can name a whole batch at once.
    This changes only the text shown in the gallery, never the file name.
  - Drag a picture onto another one to change the order.
  - "File names" button: shows each picture's file name under its shown name (it remembers your choice).
  - "Preview my site" opens your real website from your computer so you can check it.

WHEN YOU ARE DONE
  Open GitHub Desktop, commit and push. Changes only go live after that.
  (Before you commit you can undo anything in GitHub Desktop: right click a changed file > Discard changes.)

It uses the same data as add_to_gallery.py (the AUTO-GALLERY part of script.js), so you can use both.
"""
import json, os, re, secrets, shutil, sys, threading, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import add_to_gallery as g

HERE = g.HERE
TOKEN = secrets.token_hex(16)
LOCK = threading.Lock()
MIME = {'.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.png': 'image/png',
        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml',
        '.bmp': 'image/bmp', '.avif': 'image/avif', '.mp4': 'video/mp4', '.txt': 'text/plain; charset=utf-8'}


class Err(Exception):
    pass


def find(data, path):
    for f in data:
        if f['folder'] == path:
            return f
    raise Err('That folder no longer exists. Reload the page.')


def plain(name):
    if not name or name != os.path.basename(name) or name.startswith('.'):
        raise Err('Bad file name.')
    return name


# ---------- actions: each takes (data, args) and changes data / files ----------
def a_upload(data, q, body):
    fold = find(data, q['folder'])
    raw = plain(q['name'])
    if os.path.splitext(raw)[1].lower() not in g.EXTS:
        raise Err(f'{raw} is not a picture type I know.')
    os.makedirs(g.fdir(fold), exist_ok=True)
    taken = {x['file'].lower() for x in fold['images']} | {x.lower() for x in os.listdir(g.fdir(fold))}
    target = g.safe_file(raw)
    if q.get('auto') == '1':
        target = f'image_{g.next_number(fold):02d}' + os.path.splitext(target)[1]
    target = g.unique(target, taken)
    open(os.path.join(g.fdir(fold), target), 'wb').write(body)
    title = (q.get('title') or '').strip() or (os.path.splitext(target)[0] if q.get('auto') == '1' else g.nice_title(raw))
    fold['images'].append({'file': target, 'title': title})
    return {'added': target}


def a_new_folder(data, a):
    f = g.new_folder_web(data, a['name'], bool(a.get('pixelated')))
    return {}


def a_rename_folder(data, a):
    fold = find(data, a['folder'])
    n = a['name'].strip()
    if not n:
        raise Err('A folder needs a name.')
    if any(f is not fold and f['name'].lower() == n.lower() for f in data):
        raise Err('A folder with that name already exists.')
    fold['name'] = n
    return {}


def a_delete_folder(data, a):
    fold = find(data, a['folder'])
    d = g.fdir(fold)
    root = os.path.abspath(os.path.join(HERE, *g.GAL_DIR.split('/'))) + os.sep
    if a.get('deleteFiles') and os.path.isdir(d) and os.path.abspath(d).startswith(root):
        shutil.rmtree(d)
    data.remove(fold)
    return {}


def a_pixel(data, a):
    fold = find(data, a['folder'])
    if a['value']:
        fold['pixelated'] = True
    else:
        fold.pop('pixelated', None)
    return {}


def a_retitle(data, a):
    fold = find(data, a['folder'])
    for it in fold['images']:
        if it['file'] in a['titles'] and a['titles'][it['file']].strip():
            it['title'] = a['titles'][it['file']].strip()
    return {}


def a_move(data, a):
    src, dst = find(data, a['from']), find(data, a['to'])
    if src is dst:
        raise Err('Pick a different folder.')
    os.makedirs(g.fdir(dst), exist_ok=True)
    taken = {x['file'].lower() for x in dst['images']} | {x.lower() for x in os.listdir(g.fdir(dst))}
    for fn in a['files']:
        it = next((x for x in src['images'] if x['file'] == fn), None)
        if not it:
            continue
        new = g.unique(plain(fn), taken)
        taken.add(new.lower())
        p = os.path.join(g.fdir(src), fn)
        if os.path.exists(p):
            shutil.move(p, os.path.join(g.fdir(dst), new))
        src['images'].remove(it)
        dst['images'].append({'file': new, 'title': it['title']})
    return {}


def a_delete_pics(data, a):
    fold = find(data, a['folder'])
    for fn in a['files']:
        it = next((x for x in fold['images'] if x['file'] == fn), None)
        if not it:
            continue
        p = os.path.join(g.fdir(fold), plain(fn))
        if os.path.exists(p):
            os.remove(p)
        fold['images'].remove(it)
    return {}


def a_reorder(data, a):
    fold = find(data, a['folder'])
    by = {x['file']: x for x in fold['images']}
    new = [by[f] for f in a['order'] if f in by]
    new += [x for x in fold['images'] if x['file'] not in a['order']]
    fold['images'] = new
    return {}


def a_renamefiles(data, a):
    fold = find(data, a['folder'])
    d = g.fdir(fold)
    pairs = []  # (entry, old, new)
    for old, base in a['map']:
        it = next((x for x in fold['images'] if x['file'] == plain(old)), None)
        if not it:
            raise Err(f'{old} is not in this folder. Reload the page.')
        base = re.sub(r'[^A-Za-z0-9._-]+', '-', base.strip()).strip('-.')
        if not base:
            raise Err('A file name cannot be empty.')
        pairs.append((it, old, base + os.path.splitext(old)[1].lower()))
    news = [p[2].lower() for p in pairs]
    if len(set(news)) != len(news):
        raise Err('Two pictures would get the same file name.')
    olds = {p[1].lower() for p in pairs}
    others = {x.lower() for x in os.listdir(d)} - olds if os.path.isdir(d) else set()
    clash = [p[2] for p in pairs if p[2].lower() in others]
    if clash:
        raise Err(f'{clash[0]} already exists in this folder. Pick a different name or start number.')
    for it, old, new in pairs:  # two steps so swapping names can never overwrite a file
        if os.path.exists(os.path.join(d, old)):
            os.rename(os.path.join(d, old), os.path.join(d, old + '.renaming'))
    for it, old, new in pairs:
        if os.path.exists(os.path.join(d, old + '.renaming')):
            os.rename(os.path.join(d, old + '.renaming'), os.path.join(d, new))
        it['file'] = new
        if a.get('retitle'):
            it['title'] = os.path.splitext(new)[0]
    return {}


def a_sort(data, a):
    fold = find(data, a['folder'])
    key = (lambda x: g.natural(x['title'])) if a['by'] == 'title' else (lambda x: g.natural(x['file']))
    fold['images'].sort(key=key)
    return {}


def a_sync(data, a):
    msgs = []
    for fold in data:
        d = g.fdir(fold)
        if not os.path.isdir(d):
            continue
        listed = {x['file'].lower() for x in fold['images']}
        for fn in sorted(os.listdir(d), key=g.natural):
            if os.path.splitext(fn)[1].lower() in g.EXTS and fn.lower() not in listed:
                fold['images'].append({'file': fn, 'title': g.nice_title(fn)})
                msgs.append(f'Found {fn} in {fold["name"]}')
        for x in [x for x in fold['images'] if not os.path.exists(os.path.join(d, x['file']))]:
            fold['images'].remove(x)
            msgs.append(f'{x["file"]} was missing in {fold["name"]}, removed from the list')
    return {'message': '; '.join(msgs) or 'Everything already matches.'}


ACTIONS = {'folder/new': a_new_folder, 'folder/rename': a_rename_folder, 'folder/delete': a_delete_folder,
           'folder/pixel': a_pixel, 'pic/retitle': a_retitle, 'pic/move': a_move, 'pic/delete': a_delete_pics,
           'pic/reorder': a_reorder, 'pic/renamefiles': a_renamefiles, 'pic/sort': a_sort, 'sync': a_sync}


def new_folder_web(data, name, pixelated):
    name = (name or '').strip()
    if not name:
        raise Err('A folder needs a name.')
    if any(f['name'].lower() == name.lower() for f in data):
        raise Err('A folder with that name already exists.')
    taken = {f['folder'] for f in data}
    path, k = f'{g.GAL_DIR}/{g.slug(name)}/', 2
    while path in taken:
        path = f'{g.GAL_DIR}/{g.slug(name)}-{k}/'
        k += 1
    fold = {'name': name, 'folder': path, 'images': []}
    if pixelated:
        fold['pixelated'] = True
    data.append(fold)
    os.makedirs(g.fdir(fold), exist_ok=True)
    return fold


g.new_folder_web = new_folder_web


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype='application/json'):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def host_ok(self):
        return (self.headers.get('Host') or '').split(':')[0] in ('127.0.0.1', 'localhost')

    def do_GET(self):
        if not self.host_ok():
            return self.send(403, 'no', 'text/plain')
        u = urlparse(self.path)
        p = unquote(u.path)
        if p in ('/', '/manager'):
            return self.send(200, PAGE.replace('__TOKEN__', TOKEN), 'text/html; charset=utf-8')
        if p == '/api/state':
            with LOCK:
                return self.send(200, g.load())
        # static files from the repo folder (preview of your real site + thumbnails)
        rel = p.lstrip('/') or 'index.html'
        full = os.path.abspath(os.path.join(HERE, rel))
        ext = os.path.splitext(full)[1].lower()
        if (not full.startswith(HERE + os.sep) or any(part.startswith('.') for part in rel.split('/'))
                or ext in ('.py', '.yml', '.zip') or not os.path.isfile(full)):
            return self.send(404, 'not found', 'text/plain')
        return self.send(200, open(full, 'rb').read(), MIME.get(ext, 'application/octet-stream'))

    def do_POST(self):
        if not self.host_ok() or self.headers.get('X-Token') != TOKEN:
            return self.send(403, {'error': 'Not allowed. Reload the page.'})
        u = urlparse(self.path)
        n = int(self.headers.get('Content-Length') or 0)
        body = self.rfile.read(n) if n else b''
        route = u.path[len('/api/'):]
        try:
            with LOCK:
                data = g.load()
                if route == 'upload':
                    q = {k: v[0] for k, v in parse_qs(u.query).items()}
                    res = a_upload(data, q, body)
                elif route in ACTIONS:
                    res = ACTIONS[route](data, json.loads(body or b'{}'))
                else:
                    return self.send(404, {'error': 'unknown action'})
                g.save(data)
                res = dict(res or {})
                res['data'] = data
            return self.send(200, res)
        except Err as e:
            return self.send(400, {'error': str(e)})
        except Exception as e:  # keep the window alive, show the problem
            return self.send(500, {'error': f'{type(e).__name__}: {e}'})


PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dorito Gallery Manager</title>
<link rel="icon" type="image/gif" href="/media/SpinningDorito_pixel.gif">
<link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
<style>
body{overflow:auto;user-select:none}
.mgr{position:relative;display:flex;flex-direction:column;width:min(1040px,calc(100vw - 24px));height:calc(100vh - 24px);margin:12px auto;
  background:#26008fa6;border:3px solid;border-color:#0157c9 #0017e785 #0017e785;box-shadow:0 0 30px #0003cf55;backdrop-filter:blur(2px)}
.mtb{display:flex;align-items:center;gap:8px;padding:2px 6px;background:#0003cf70;color:blueviolet;border-bottom:1px solid #0017e77a}
.mtb img{width:18px;height:18px}.mtb b{font-weight:400;flex:1}
.mtb a{color:blueviolet;text-decoration:none;border:2px solid;border-color:#0157c9 #0017e785 #0017e785;background:#0003cf40;padding:0 10px;font-size:18px}
.mtb a:hover{background:#4200ac99;color:#d9c2ff;border-color:#3d8bff #0157c9 #0157c9}
.mbar{display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:8px 10px 4px}
.sep{width:2px;align-self:stretch;background:#0017e785;margin:0 4px}
.b{font:inherit;font-size:18px;line-height:1.1;padding:1px 12px;color:blueviolet;background:#0003cf40;border:2px solid;border-color:#0157c9 #0017e785 #0017e785;cursor:pointer}
.b:hover:not(:disabled),.b:focus-visible{background:#4200ac99;color:#d9c2ff;border-color:#3d8bff #0157c9 #0157c9;outline:0}
.b:active:not(:disabled){background:#26008fe0}
.b:disabled{opacity:.35;cursor:default}
.b.danger{color:#ff7a7a}.b.danger:hover:not(:disabled){color:#ffd0d0;background:#a0002e88}
.crumb{color:blueviolet;font-size:21px;margin-right:6px}
.lbl{color:blueviolet;font-size:18px;display:flex;align-items:center;gap:6px;cursor:pointer}
.lbl input{accent-color:#ffa600;width:16px;height:16px}
.area{position:relative;flex:1;overflow:auto;padding:10px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px}
.tile{display:flex;flex-direction:column;gap:3px;color:blueviolet;font:inherit;background:none;border:0;padding:0;cursor:pointer;text-align:center}
.tile .im{aspect-ratio:1;overflow:hidden;background:#0003cf40;border:2px solid;border-color:#0157c9 #0017e785 #0017e785;display:flex;align-items:center;justify-content:center;position:relative}
.tile .im img{width:100%;height:100%;object-fit:cover}
.px .tile .im img{image-rendering:pixelated}
.tile:hover .im{border-color:#ffa600}
.tile.sel .im{border-color:#ffa600;box-shadow:0 0 0 3px #ffa60099,0 0 14px #ffa600}
.tile.sel .im::after{content:"\2713";position:absolute;top:2px;right:4px;color:#ffa600;font-size:26px;text-shadow:1px 1px 2px #000}
.tile .cap{font-size:18px;line-height:1;word-break:break-word;text-shadow:1px 1px 2px #000;min-height:19px}
.tile .fn{font-size:15px;line-height:1;color:#7df9ff;word-break:break-all;opacity:.9}
.tile.fd .im{border:0;background:none;aspect-ratio:1.1}
.tile.fd .im img{object-fit:contain}
.tile.fd:hover .cap{color:#ffa600}
.tile.over .im{outline:3px dashed #7df9ff}
.tile.drag{opacity:.4}
.mempty{color:blueviolet;font-size:22px;padding:20px;text-align:center}
.status{display:flex;gap:10px;padding:3px 10px 5px;color:#b88cff;font-size:18px;border-top:1px solid #0017e77a;min-height:30px}
.status span{flex:1}
.drop{position:absolute;inset:0;background:#0003cfb0;border:4px dashed #ffa600;color:#ffa600;display:none;align-items:center;justify-content:center;font-size:34px;z-index:5;pointer-events:none;text-align:center}
.mgr.dragging .drop{display:flex}
.ovl{position:fixed;inset:0;background:#000a;display:flex;align-items:center;justify-content:center;z-index:20;padding:12px}
.dlg{background:#1c0a6ef2;border:3px solid;border-color:#0157c9 #0017e785 #0017e785;box-shadow:0 0 40px #0003cf99;max-width:560px;width:100%;max-height:90vh;display:flex;flex-direction:column;color:blueviolet}
.dlg h3{margin:0;font-weight:400;font-size:24px;padding:4px 10px;background:#0003cf70;border-bottom:1px solid #0017e77a}
.dbody{padding:10px;overflow:auto;font-size:20px;display:flex;flex-direction:column;gap:8px}
.dbody p{margin:0;color:#d9c2ff}
.dfoot{display:flex;justify-content:flex-end;gap:8px;padding:8px 10px;border-top:1px solid #0017e77a}
.inp{font:inherit;font-size:20px;color:#ffa600;background:#07051acc;border:2px solid;border-color:#0017e785 #0157c9 #0157c9;padding:3px 8px;width:100%;outline:0}
.inp:focus{border-color:#3d8bff}
.rrow{display:flex;gap:8px;align-items:center}.rrow img{width:44px;height:44px;object-fit:cover;border:2px solid #0157c9;flex:none}
.pick{display:flex;flex-direction:column;gap:6px}
.pick .b{text-align:left;font-size:20px}
.toast{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);background:#1c0a6ef2;border:2px solid #ffa600;color:#ffa600;padding:4px 16px;font-size:20px;z-index:30}
.toast.err{border-color:#ff6a6a;color:#ff9a9a}
</style></head>
<body>
<div class="mgr" id="mgr">
  <div class="mtb"><img src="/media/SpinningDorito_pixel.gif" alt=""><b>Dorito Gallery Manager</b><a href="/index.html" target="_blank" title="Opens your real website from this computer">Preview my site</a></div>
  <div class="mbar" id="bar"></div>
  <div class="area" id="area"></div>
  <div class="status"><span id="st"></span><span style="flex:none;text-align:right" id="note">Push in GitHub Desktop to publish.</span></div>
  <div class="drop" id="drop">Drop pictures here to add them<br>to this folder</div>
</div>
<input type="file" id="file" accept="image/*" multiple hidden>
<script>
const TOKEN='__TOKEN__';
let data=[],cur=null,sel=new Set(),auto=false,showFiles=false;
try{showFiles=localStorage.getItem('dorito-showfiles')==='1'}catch(e){}
const $=id=>document.getElementById(id);
const h=(t,a,...k)=>{const e=document.createElement(t);for(const[n,v]of Object.entries(a||{})){if(n==='class')e.className=v;else if(n.startsWith('on'))e.addEventListener(n.slice(2),v);else if(v!==false&&v!=null)e.setAttribute(n,v===true?'':v)}k.flat().forEach(c=>e.append(c));return e};
const folder=()=>data.find(f=>f.folder===cur);
const niceFile=f=>f.replace(/\.[^.]+$/,'');
function toast(m,err){const t=h('div',{class:'toast'+(err?' err':'')},m);document.body.append(t);setTimeout(()=>t.remove(),err?5000:2600)}
async function api(route,body,q){
  const r=await fetch('/api/'+route+(q||''),{method:'POST',headers:{'X-Token':TOKEN},body:body instanceof Uint8Array||body instanceof Blob?body:JSON.stringify(body||{})});
  const j=await r.json();if(!r.ok)throw new Error(j.error||'Something went wrong');
  if(j.data){data=j.data;if(cur&&!folder()){cur=null;sel.clear()}}return j}
async function act(route,body,msg){try{const j=await api(route,body);if(msg)toast(msg);if(j.message)toast(j.message);render();return j}catch(e){toast(e.message,1);render()}}

/* ---------- dialogs ---------- */
function dialog(title,body,buttons,onOpen){return new Promise(res=>{
  const done=v=>{o.remove();res(v)};
  const foot=h('div',{class:'dfoot'},buttons.map(b=>h('button',{class:'b'+(b.danger?' danger':''),type:'button',onclick:()=>done(b.value)},b.label)));
  const o=h('div',{class:'ovl',onmousedown:e=>{if(e.target===o)done(null)}},h('div',{class:'dlg'},h('h3',{},title),h('div',{class:'dbody'},body),foot));
  o.addEventListener('keydown',e=>{if(e.key==='Escape')done(null)});
  document.body.append(o);if(onOpen)onOpen(o,done)})}
async function askText(title,label,val='',ok='OK'){
  const i=h('input',{class:'inp',value:val,spellcheck:'false'});
  const r=await dialog(title,[label?h('p',{},label):'',i],[{label:'Cancel',value:null},{label:ok,value:true}],(o,done)=>{setTimeout(()=>{i.focus();i.select()},30);i.addEventListener('keydown',e=>{if(e.key==='Enter')done(true)})});
  return r?i.value:null}
async function confirmBox(title,text,ok,danger){return !!await dialog(title,[h('p',{},text)],[{label:'Cancel',value:null},{label:ok,value:true,danger}])}
async function pickFolder(title,list){
  return dialog(title,[h('div',{class:'pick'},list.map(f=>h('button',{class:'b',type:'button',onclick:e=>e.target.closest('.ovl').dispatchEvent(new CustomEvent('pick',{detail:f.folder}))},f.name+'  ('+f.images.length+')')))],[{label:'Cancel',value:null}],(o,done)=>o.addEventListener('pick',e=>done(e.detail)))}

/* ---------- actions ---------- */
async function newFolder(){const n=await askText('New folder','Name shown in the gallery:','','Create');if(n===null)return;
  const px=await confirmBox('Pixel art?','Is this folder pixel art? (keeps pictures crisp when enlarged)','Yes, pixel art');
  await act('folder/new',{name:n,pixelated:px},'Folder created')}
async function renameFolder(){const f=folder();const n=await askText('Rename folder','Text shown in the gallery:',f.name,'Save');if(n!==null)await act('folder/rename',{folder:cur,name:n},'Renamed')}
async function deleteFolder(){const f=folder();
  const r=await dialog('Delete folder','"'+f.name+'" has '+f.images.length+' picture(s).',[{label:'Cancel',value:null},{label:'Hide folder, keep files',value:'keep'},{label:'Delete folder AND pictures',value:'del',danger:1}]);
  if(!r)return;await act('folder/delete',{folder:cur,deleteFiles:r==='del'},'Folder removed')}
async function pixelToggle(){const f=folder();await act('folder/pixel',{folder:cur,value:!f.pixelated},f.pixelated?'Pixel art off':'Pixel art on')}
async function renamePics(){const f=folder(),files=f.images.filter(x=>sel.has(x.file));if(!files.length)return;
  const ins=files.map(x=>h('input',{class:'inp',value:x.title,spellcheck:'false','data-f':x.file}));
  const rows=files.map((x,i)=>h('div',{class:'rrow'},h('img',{src:'/'+f.folder+x.file}),ins[i]));
  const r=await dialog('Rename ('+files.length+')',[h('p',{},'This is the text shown in the gallery, not the file name.'),...rows],[{label:'Cancel',value:null},{label:'Save',value:true}],(o,done)=>{setTimeout(()=>{ins[0].focus();ins[0].select()},30);ins.forEach(i=>i.addEventListener('keydown',e=>{if(e.key==='Enter')done(true)}))});
  if(!r)return;const titles={};ins.forEach(i=>titles[i.dataset.f]=i.value);await act('pic/retitle',{folder:cur,titles},'Saved')}
async function movePics(){const others=data.filter(x=>x.folder!==cur);if(!others.length){toast('Make another folder first',1);return}
  const to=await pickFolder('Move '+sel.size+' picture(s) to...',others);if(!to)return;
  const n=sel.size;await act('pic/move',{from:cur,to,files:[...sel]},'Moved '+n);sel.clear();render()}
async function deletePics(){const n=sel.size;if(!await confirmBox('Delete pictures','Delete '+n+' picture(s)? The files are deleted from your repo folder too (you can undo in GitHub Desktop before committing).','Delete',true))return;
  await act('pic/delete',{folder:cur,files:[...sel]},'Deleted '+n);sel.clear();render()}
async function renameFiles(){const f=folder();if(!f)return;
  const targets=f.images.filter(x=>sel.has(x.file)),list=targets.length?targets:f.images;if(!list.length)return;
  const ext=x=>(x.match(/\.[^.]+$/)||[''])[0].toLowerCase(),base=x=>x.replace(/\.[^.]+$/,'');
  const L=h('p',{}, targets.length?('Renaming the FILE names of the '+list.length+' selected picture(s), in the order they appear.'):('Nothing selected, so this renames the FILE names of ALL '+list.length+' pictures, in the order they appear.'));
  const prev=h('p',{style:'color:#ffa600'});
  let one=list.length===1,single,prefix,start,digits,retitle=h('input',{type:'checkbox'}),touched=false;
  const body=[L];
  const others=new Set(f.images.filter(x=>!list.includes(x)).map(x=>x.file.toLowerCase()));
  const nextFree=p=>{let n=0;f.images.forEach(x=>{if(list.includes(x))return;const m=x.file.match(/^(.*?)(\d+)\.[^.]+$/);if(m&&m[1]===p)n=Math.max(n,+m[2]+1)});return n};
  if(one){single=h('input',{class:'inp',value:base(list[0].file),spellcheck:'false'});body.push(h('p',{},'New file name (the ending '+ext(list[0].file)+' is kept):'),single)}
  else{prefix=h('input',{class:'inp',value:'image_',spellcheck:'false'});start=h('input',{class:'inp',type:'number',min:'0',value:nextFree('image_')});digits=h('input',{class:'inp',type:'number',min:'1',max:'6',value:'2'});
    body.push(h('p',{},'Name them (prefix + number):'),h('div',{class:'rrow'},h('div',{style:'flex:2'},h('p',{},'Prefix'),prefix),h('div',{style:'flex:1'},h('p',{},'Start at'),start),h('div',{style:'flex:1'},h('p',{},'Digits'),digits)))}
  body.push(h('label',{class:'lbl'},retitle,'also change the shown gallery names to match'),prev);
  const names=()=>one?[single.value.trim()]:list.map((x,i)=>(prefix.value)+String(+start.value+i).padStart(Math.max(+digits.value||1,String(+start.value+list.length-1).length),'0'));
  const upd=()=>{const n=names();prev.textContent='e.g.  '+list.slice(0,3).map((x,i)=>x.file+'  ->  '+n[i]+ext(x.file)).join('   |   ')+(list.length>3?'   ...':'')};
  const r=await dialog('Rename files',body,[{label:'Cancel',value:null},{label:'Rename files',value:true}],(o,done)=>{
    const ins=[single,prefix,start,digits].filter(Boolean);ins.forEach(i=>i.addEventListener('input',()=>{if(i===start)touched=true;if(i===prefix&&!touched)start.value=nextFree(prefix.value);upd()}));upd();setTimeout(()=>{(single||prefix).focus();(single||prefix).select()},30);
    ins.forEach(i=>i.addEventListener('keydown',e=>{if(e.key==='Enter')done(true)}))});
  if(!r)return;const n=names();
  const bad=n.findIndex((b,i)=>others.has((b+ext(list[i].file)).toLowerCase()));
  await act('pic/renamefiles',{folder:cur,map:list.map((x,i)=>[x.file,n[i]]),retitle:retitle.checked},'File names changed');sel.clear();render()}
async function sortPics(){const r=await dialog('Sort pictures',[h('div',{class:'pick'},[h('button',{class:'b',type:'button',onclick:e=>e.target.closest('.ovl').dispatchEvent(new CustomEvent('pick',{detail:'title'}))},'By shown name (A to Z)'),h('button',{class:'b',type:'button',onclick:e=>e.target.closest('.ovl').dispatchEvent(new CustomEvent('pick',{detail:'file'}))},'By file name (numbers in order)')])],[{label:'Cancel',value:null}],(o,done)=>o.addEventListener('pick',e=>done(e.detail)));
  if(r)await act('pic/sort',{folder:cur,by:r},'Sorted')}
async function upload(files){const f=folder();if(!f)return;files=[...files].filter(x=>/\.(png|jpe?g|gif|webp|bmp|svg|avif)$/i.test(x.name));
  if(!files.length){toast('No pictures found (png, jpg, gif, webp, bmp, svg, avif)',1);return}
  const before=new Set(f.images.map(x=>x.file));let ok=0;
  for(const[i,x]of files.entries()){$('st').textContent='Adding '+(i+1)+' of '+files.length+'...';
    try{await api('upload',new Uint8Array(await x.arrayBuffer()),'?folder='+encodeURIComponent(cur)+'&name='+encodeURIComponent(x.name)+(auto?'&auto=1':''));ok++}catch(e){toast(x.name+': '+e.message,1)}}
  sel=new Set(folder().images.filter(x=>!before.has(x.file)).map(x=>x.file));render();
  toast('Added '+ok+'. They are selected: press Rename to name them.')}

/* ---------- drawing ---------- */
function render(){
  const bar=$('bar'),area=$('area');bar.innerHTML='';area.innerHTML='';area.className='area';
  const B=(t,fn,o={})=>h('button',{class:'b'+(o.danger?' danger':''),type:'button',onclick:fn,disabled:o.off},t);
  if(!cur){
    bar.append(h('span',{class:'crumb'},'Gallery'),B('New folder',newFolder),B('Sync with disk',()=>act('sync',{})));
    $('st').textContent=data.length+' folder(s). Click a folder to open it.';
    if(!data.length)area.append(h('p',{class:'mempty'},'No folders yet. Press "New folder".'));
    const g=h('div',{class:'grid'});
    data.forEach(f=>g.append(h('button',{class:'tile fd',type:'button',onclick:()=>{cur=f.folder;sel.clear();render()}},h('div',{class:'im'},h('img',{src:'/media/Dorito_folder_icon.png',alt:''})),h('div',{class:'cap'},f.name+' ('+f.images.length+')'))));
    area.append(g);return}
  const f=folder();if(f.pixelated)area.classList.add('px');
  const n=sel.size,none=!n;
  bar.append(B('Back',()=>{cur=null;sel.clear();render()}),h('span',{class:'crumb'},'Gallery / '+f.name),
    B('Add pictures',()=>$('file').click()),
    h('label',{class:'lbl',title:'Names new pictures image_00, image_01, ...'},h('input',{type:'checkbox',checked:auto,onchange:e=>{auto=e.target.checked}}),'auto-name image_00...'),
    h('span',{class:'sep'}),
    B('Rename'+(n?' ('+n+')':''),renamePics,{off:none}),B('Move',movePics,{off:none}),B('Delete',deletePics,{off:none,danger:1}),
    B(n===f.images.length&&n?'Select none':'Select all',()=>{sel=n===f.images.length?new Set():new Set(f.images.map(x=>x.file));render()},{off:!f.images.length}),
    h('span',{class:'sep'}),B(showFiles?'File names: ON':'File names: off',()=>{showFiles=!showFiles;try{localStorage.setItem('dorito-showfiles',showFiles?'1':'0')}catch(e){}render()}),B('Sort',sortPics,{off:f.images.length<2}),B('Rename files'+(n?' ('+n+')':''),renameFiles,{off:!f.images.length}),B('Rename folder',renameFolder),B(f.pixelated?'Pixel art: ON':'Pixel art: off',pixelToggle),B('Delete folder',deleteFolder,{danger:1}));
  $('st').textContent=f.images.length+' picture(s)'+(n?', '+n+' selected':'')+'. Click to select. Drag to re-order.';
  if(!f.images.length){area.append(h('p',{class:'mempty'},'Empty :(  Press "Add pictures" or drag pictures here.'));return}
  const gr=h('div',{class:'grid'});let dragging=null;
  f.images.forEach(it=>{
    const t=h('button',{class:'tile'+(sel.has(it.file)?' sel':''),type:'button',draggable:'true',title:it.title+'  ['+it.file+']'},
      h('div',{class:'im'},h('img',{src:'/'+f.folder+it.file+'?'+Date.now(),alt:it.title,loading:'lazy'})),h('div',{class:'cap'},it.title),showFiles?h('div',{class:'fn'},it.file):'');
    t.addEventListener('click',()=>{sel.has(it.file)?sel.delete(it.file):sel.add(it.file);render()});
    t.addEventListener('dblclick',()=>{sel=new Set([it.file]);renamePics()});
    t.addEventListener('dragstart',e=>{dragging=it.file;t.classList.add('drag');e.dataTransfer.setData('text/x-dorito',it.file);e.dataTransfer.effectAllowed='move'});
    t.addEventListener('dragend',()=>t.classList.remove('drag'));
    t.addEventListener('dragover',e=>{if(dragging&&dragging!==it.file){e.preventDefault();t.classList.add('over')}});
    t.addEventListener('dragleave',()=>t.classList.remove('over'));
    t.addEventListener('drop',async e=>{if(!dragging)return;e.preventDefault();e.stopPropagation();t.classList.remove('over');
      const order=f.images.map(x=>x.file).filter(x=>x!==dragging);order.splice(order.indexOf(it.file),0,dragging);dragging=null;await act('pic/reorder',{folder:cur,order})});
    gr.append(t)});
  area.append(gr)}

/* drag pictures from the computer onto the window */
const mgr=$('mgr');let dc=0;
const hasFiles=e=>[...(e.dataTransfer?.types||[])].includes('Files');
mgr.addEventListener('dragenter',e=>{if(hasFiles(e)&&cur){dc++;mgr.classList.add('dragging')}});
mgr.addEventListener('dragleave',e=>{if(hasFiles(e)){dc=Math.max(0,dc-1);if(!dc)mgr.classList.remove('dragging')}});
mgr.addEventListener('dragover',e=>{if(hasFiles(e))e.preventDefault()});
mgr.addEventListener('drop',e=>{if(hasFiles(e)){e.preventDefault();dc=0;mgr.classList.remove('dragging');if(cur)upload(e.dataTransfer.files);else toast('Open a folder first, then drop pictures',1)}});
$('file').addEventListener('change',e=>{upload(e.target.files);e.target.value=''});
fetch('/api/state').then(r=>r.json()).then(d=>{data=d;render()}).catch(()=>toast('Could not load. Is the black window still open?',1));
</script></body></html>'''


def main():
    g.load()  # fail early with a clear message if script.js is missing / has no markers
    srv = None
    for port in range(8765, 8785):
        try:
            srv = ThreadingHTTPServer(('127.0.0.1', port), H)
            break
        except OSError:
            continue
    if not srv:
        sys.exit('Could not open a port. Close other copies of this tool and try again.')
    url = f'http://127.0.0.1:{srv.server_address[1]}/'
    print(f'\nDorito Gallery Manager is running at {url}\nYour browser should open by itself. Leave this window open while you work.')
    print('Press Ctrl+C here (or just close this window) when you are done.\n')
    if '--no-browser' not in sys.argv:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\nBye! If you changed anything, commit and push in GitHub Desktop.')


if __name__ == '__main__':
    main()
