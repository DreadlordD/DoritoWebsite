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
  - Import a whole folder from your computer: press "Import folder" (or drag the folder onto the window). On the
    folder list it becomes a NEW gallery folder with the same name; inside a gallery folder it adds to that one.
    Sub-folders are included. Afterwards the pictures are selected so you can rename them right away.
  - Add pictures: press "Add pictures" or just drag pictures from your computer onto the window.
  - Click pictures to select them (click again to deselect), then Rename, Move or Delete.
  - "Rename files" changes the FILE names on disk: it numbers the selected pictures (or all of them if none are
    selected) as image_00, image_01... in the order shown. You choose the prefix, start number and digits.
  - Rename shows one box per selected picture, so you can name a whole batch at once.
    This changes only the text shown in the gallery, never the file name.
  - Drag a picture onto another one to change the order.
  - "Sizes": makes resized copies (2048, 1024, 512, 256, 128, 64, 32 px) of the selected pictures (or all), saved in
    a "size-copies" folder next to them. On your website each picture then has a size chooser next to its link,
    so you can copy a link for the exact size you want (VRChat only loads up to 2048). "auto-make sizes" does this
    for every picture you add or import.
  - "File names" button: shows each picture's file name under its shown name (it remembers your choice).
  - "Console" (top right) shows what the manager is doing, line by line.
  - "Preview my site" opens your real website from your computer so you can check it.

WHEN YOU ARE DONE
  Open GitHub Desktop, commit and push. Changes only go live after that.
  (Before you commit you can undo anything in GitHub Desktop: right click a changed file > Discard changes.)

It uses the same data as add_to_gallery.py (the AUTO-GALLERY part of script.js), so you can use both.
"""
import hashlib, json, os, re, secrets, shutil, sys, tempfile, threading, time, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import add_to_gallery as g

HERE = g.HERE
SCRIPT_PATH = g.SCRIPT
TOKEN = secrets.token_hex(16)
LOCK = threading.Lock()
MIME = {'.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.png': 'image/png',
        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml',
        '.bmp': 'image/bmp', '.avif': 'image/avif', '.mp4': 'video/mp4', '.txt': 'text/plain; charset=utf-8'}


LOGS = []  # lines shown in the console window of the page (and printed in the black window)


_LOGN = [0]


def log(msg, kind='info', quiet=False):
    _LOGN[0] += 1
    LOGS.append({'n': _LOGN[0], 't': time.strftime('%H:%M:%S'), 'm': msg, 'k': kind})
    del LOGS[:-500]
    if not quiet:  # printing in a Windows console window is slow, so the many "made copy" lines only go to the page
        try:
            print(f'[{time.strftime("%H:%M:%S")}] {msg}')
        except Exception:
            pass


def fname(data, path):
    try:
        return '"' + find(data, path)['name'] + '"'
    except Exception:
        return path or '?'


def describe(route, a, before, res, data):
    """One-line plain-English description of what an action just did (before = data as it was before)."""
    try:
        if route == 'upload':
            return f'Added {res.get("added")} to {fname(data, a.get("folder"))}'
        if route == 'replace':
            return f'  shrank {a.get("file")} (saved {human(res.get("saved", 0))})'
        if route == 'uploadsize':
            return f'  made {a.get("size")} px copy of {a.get("file")}'
        if route == 'folder/new':
            return (f'Folder {fname(data, res.get("path"))} ready' if a.get('ensure') else f'Created folder {fname(data, res.get("path"))}')
        if route == 'folder/rename':
            return f'Renamed folder {fname(before, a["folder"])} to "{a["name"]}"'
        if route == 'folder/delete':
            return f'Deleted folder {fname(before, a["folder"])}' + (' and its pictures' if a.get('deleteFiles') else ' (files kept on disk)')
        if route == 'folder/pixel':
            return f'Pixel art {"on" if a["value"] else "off"} for {fname(data, a["folder"])}'
        if route == 'pic/retitle':
            return f'Renamed {len([t for t in a["titles"].values() if t.strip()])} picture name(s) in {fname(data, a["folder"])}'
        if route == 'pic/move':
            return f'Moved {len(a["files"])} picture(s) from {fname(before, a["from"])} to {fname(data, a["to"])}'
        if route == 'pic/delete':
            return f'Deleted {len(a["files"])} picture(s) from {fname(before, a["folder"])}'
        if route == 'pic/removesizes':
            return f'Removed {", ".join(map(str, a["sizes"]))} px copies of {len(a["files"])} picture(s)'
        if route == 'pic/reorder':
            return f'Re-ordered pictures in {fname(data, a["folder"])}'
        if route == 'pic/sort':
            return f'Sorted {fname(data, a["folder"])} by {"shown name" if a["by"] == "title" else "file name"}'
        if route == 'pic/renamefiles':
            return f'Renamed {len(a["map"])} file(s) in {fname(data, a["folder"])} (first: {a["map"][0][0]} -> {a["map"][0][1]})'
        if route == 'sync':
            return 'Sync: ' + res.get('message', '')
    except Exception:
        pass
    return route


class Err(Exception):
    pass


def walk(nodes):
    for n in nodes:
        yield n
        yield from walk(n.get('folders', []))


def find_parent(data, path):
    """(list holding the folder, the folder) for a folder path, searching sub-folders too."""
    def rec(lst):
        for n in lst:
            if n['folder'] == path:
                return lst, n
            r = rec(n.get('folders', []))
            if r:
                return r
    r = rec(data)
    if not r:
        raise Err('That folder no longer exists. Reload the page.')
    return r


def find(data, path):
    return find_parent(data, path)[1]


def plain(name):
    if not name or name != os.path.basename(name) or name.startswith('.'):
        raise Err('Bad file name.')
    return name


SIZES_DIR = 'size-copies'     # resized copies live in  <gallery folder>/size-copies/<N>/<file>  (no leading underscore: GitHub's Jekyll would hide those)
UNITY_SIZES = [2048, 1024, 512, 256, 128, 64, 32]


def size_name(fn):
    """File name of a resized copy: png/jpg/webp keep their name, anything else gets .png added."""
    return fn if os.path.splitext(fn)[1].lower() in ('.png', '.jpg', '.jpeg', '.webp') else fn + '.png'


def size_path(fold, n, fn):
    return os.path.join(g.fdir(fold), SIZES_DIR, str(int(n)), size_name(fn))


def move_size_files(src, dst, sizes, old, new):
    """Move/rename the resized copies of one picture (src folder/old name -> dst folder/new name)."""
    for n in sizes or []:
        a = size_path(src, n, old)
        if os.path.exists(a):
            b = size_path(dst, n, new)
            os.makedirs(os.path.dirname(b), exist_ok=True)
            shutil.move(a, b)


def human(n):
    return f'{n / 1073741824:.2f} GB' if n >= 1073741824 else f'{n / 1048576:.1f} MB'


SIZE_TXT = os.path.join(HERE, 'gallery-size.txt')


def dir_bytes(path):
    t = 0
    for r, _d, fs in os.walk(path):
        for f in fs:
            try:
                t += os.path.getsize(os.path.join(r, f))
            except OSError:
                pass
    return t


def inventory(data):
    """Every picture with its size on disk, plus the total size of the whole gallery (pictures + resized copies + anything else in the folders)."""
    items, total = [], 0
    for node in walk(data):
        d = g.fdir(node)
        if not os.path.isdir(d):
            continue
        listed = {x['file']: x for x in node['images']}
        for e in os.scandir(d):
            if e.is_file():
                b = e.stat().st_size
                total += b
                if e.name in listed:
                    items.append({'p': node['folder'], 'f': e.name, 'b': b, 'px': bool(node.get('pixelated')), 'max': listed[e.name].get('max', 0)})
        sd = os.path.join(d, SIZES_DIR)
        if os.path.isdir(sd):
            total += dir_bytes(sd)
    return {'items': items, 'total': total}


def write_size_txt(total):
    """gallery-size.txt: one line your website shows on the gallery page."""
    line = f'Gallery size: {human(total)}'
    try:
        if not os.path.isfile(SIZE_TXT) or open(SIZE_TXT, encoding='utf-8').read().strip() != line:
            open(SIZE_TXT, 'w', encoding='utf-8').write(line + '\n')
    except OSError:
        pass
    return line


def a_replace(data, q, body):
    """Swap a picture's file for a smaller version of itself (same name). Refuses if the new one is not smaller."""
    fold = find(data, q['folder'])
    fn = plain(q['file'])
    it = next((x for x in fold['images'] if x['file'] == fn), None)
    if not it:
        raise Err(f'{fn} is not in this folder.')
    p = os.path.join(g.fdir(fold), fn)
    old = os.path.getsize(p)
    if not body or len(body) >= old:
        return {'saved': 0}
    tmp = p + '.tmp-resize'
    open(tmp, 'wb').write(body)
    os.replace(tmp, p)
    if q.get('max', '').isdigit():
        it['max'] = int(q['max'])
    return {'saved': old - len(body)}


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


def a_upload_size(data, q, body):
    fold = find(data, q['folder'])
    fn = plain(q['file'])
    n = int(q['size'])
    if n not in UNITY_SIZES:
        raise Err('Not a size I know.')
    it = next((x for x in fold['images'] if x['file'] == fn), None)
    if not it:
        raise Err(f'{fn} is not in this folder.')
    p = size_path(fold, n, fn)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb').write(body)
    it['sizes'] = sorted(set(it.get('sizes', [])) | {n}, reverse=True)
    if q.get('max', '').isdigit():
        it['max'] = int(q['max'])   # longest side of the original, so we know which sizes can never be made
    return {}


def a_meta(data, a):
    fold = find(data, a['folder'])
    it = next((x for x in fold['images'] if x['file'] == plain(a['file'])), None)
    if it and int(a.get('max', 0)) > 0:
        it['max'] = int(a['max'])
    return {}


def a_remove_sizes(data, a):
    fold = find(data, a['folder'])
    for it in fold['images']:
        if it['file'] in a['files']:
            for n in a['sizes']:
                p = size_path(fold, n, it['file'])
                if os.path.exists(p):
                    os.remove(p)
            it['sizes'] = [n for n in it.get('sizes', []) if n not in a['sizes']]
            if not it['sizes']:
                it.pop('sizes')
    return {}


def a_new_folder(data, a):
    name = (a.get('name') or '').strip()
    if not name:
        raise Err('A folder needs a name.')
    parent = find(data, a['parent']) if a.get('parent') else None
    sibs = parent.setdefault('folders', []) if parent else data
    same = next((f for f in sibs if f['name'].lower() == name.lower()), None)
    if same:
        if a.get('ensure'):
            return {'path': same['folder']}
        raise Err('A folder with that name already exists here.')
    taken = {f['folder'] for f in walk(data)}
    base = parent['folder'] if parent else g.GAL_DIR + '/'
    path, k = f'{base}{g.slug(name)}/', 2
    while path in taken:
        path = f'{base}{g.slug(name)}-{k}/'
        k += 1
    fold = {'name': name, 'folder': path, 'images': []}
    if a.get('pixelated'):
        fold['pixelated'] = True
    sibs.append(fold)
    os.makedirs(g.fdir(fold), exist_ok=True)
    return {'path': path}


def a_rename_folder(data, a):
    sibs, fold = find_parent(data, a['folder'])
    n = a['name'].strip()
    if not n:
        raise Err('A folder needs a name.')
    if any(f is not fold and f['name'].lower() == n.lower() for f in sibs):
        raise Err('A folder with that name already exists.')
    fold['name'] = n
    return {}


def a_delete_folder(data, a):
    sibs, fold = find_parent(data, a['folder'])
    d = g.fdir(fold)
    root = os.path.abspath(os.path.join(HERE, *g.GAL_DIR.split('/'))) + os.sep
    if a.get('deleteFiles') and os.path.isdir(d) and os.path.abspath(d).startswith(root):
        shutil.rmtree(d)  # includes its sub-folders
    sibs.remove(fold)
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
        move_size_files(src, dst, it.get('sizes'), fn, new)
        src['images'].remove(it)
        moved = dict(it)
        moved['file'] = new
        dst['images'].append(moved)
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
        for n in it.get('sizes', []):
            sp = size_path(fold, n, fn)
            if os.path.exists(sp):
                os.remove(sp)
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
    sizemoves = []
    for it, old, new in pairs:  # resized copies follow the new name (also in two steps)
        for n in it.get('sizes', []):
            a_, b_ = size_path(fold, n, old), size_path(fold, n, new)
            if os.path.exists(a_):
                sizemoves.append((a_, b_))
    for a_, b_ in sizemoves:
        os.rename(a_, a_ + '.renaming')
    for a_, b_ in sizemoves:
        os.rename(a_ + '.renaming', b_)
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
    changed_sizes = [0]

    def sync(fold, top):
        d = g.fdir(fold)
        if os.path.isdir(d):
            listed = {x['file'].lower() for x in fold['images']}
            for fn in sorted(os.listdir(d), key=g.natural):
                if os.path.splitext(fn)[1].lower() in g.EXTS and fn.lower() not in listed:
                    fold['images'].append({'file': fn, 'title': g.nice_title(fn)})
                    msgs.append(f'Found {fn} in {fold["name"]}')
            for x in [x for x in fold['images'] if not os.path.exists(os.path.join(d, x['file']))]:
                fold['images'].remove(x)
                msgs.append(f'{x["file"]} was missing in {fold["name"]}, removed from the list')
            for it in fold['images']:  # which resized copies really exist on disk?
                have = [n for n in UNITY_SIZES if os.path.isfile(size_path(fold, n, it['file']))]
                if have != it.get('sizes', []):
                    if have:
                        it['sizes'] = have
                    else:
                        it.pop('sizes', None)
                    changed_sizes[0] += 1
            known = {os.path.basename(c['folder'].rstrip('/')).lower() for c in fold.get('folders', [])}
            for sd in sorted(os.listdir(d), key=g.natural):
                if os.path.isdir(os.path.join(d, sd)) and sd.lower() not in known and not sd.startswith('.') and sd != SIZES_DIR:
                    fold.setdefault('folders', []).append({'name': sd, 'folder': fold['folder'] + sd + '/', 'images': []})
                    msgs.append(f'Found sub-folder {sd} in {fold["name"]}')
        for c in fold.get('folders', []):
            sync(c, False)

    # folders that exist on disk but the manager doesn't know yet: media/gallery/* and media/* (only if they hold pictures)
    src = open(SCRIPT_PATH, encoding='utf-8').read()
    i, j = src.index(g.START), src.index(g.END)
    outside = (src[:i] + src[j:]).lower()  # hand-written gallery folders in script.js are left alone
    known = {f['folder'].lower() for f in walk(data)}
    media = os.path.join(HERE, 'media')
    for base in (g.GAL_DIR, 'media'):
        bd = os.path.join(HERE, *base.split('/'))
        if not os.path.isdir(bd):
            continue
        for name in sorted(os.listdir(bd), key=g.natural):
            full = os.path.join(bd, name)
            path = f'{base}/{name}/'
            if (not os.path.isdir(full) or name.startswith('.') or name == SIZES_DIR or path.lower() in known
                    or path.lower() in outside or (base == 'media' and name == 'gallery')):
                continue
            has_pics = any(os.path.splitext(f)[1].lower() in g.EXTS for _, _, fs in os.walk(full) for f in fs)
            if base == 'media' and not has_pics:
                continue
            data.append({'name': name, 'folder': path, 'images': []})
            msgs.append(f'Found folder {name} ({path})')
    for fold in data:
        sync(fold, True)
    if changed_sizes[0]:
        msgs.append(f'Updated the list of resized copies for {changed_sizes[0]} picture(s)')
    return {'message': '; '.join(msgs) or 'Everything already matches.'}


ACTIONS = {'folder/new': a_new_folder, 'folder/rename': a_rename_folder, 'folder/delete': a_delete_folder,
           'folder/pixel': a_pixel, 'pic/retitle': a_retitle, 'pic/move': a_move, 'pic/delete': a_delete_pics, 'pic/removesizes': a_remove_sizes, 'pic/meta': a_meta,
           'pic/reorder': a_reorder, 'pic/renamefiles': a_renamefiles, 'pic/sort': a_sort, 'sync': a_sync}


THUMB_DIR = os.path.join(tempfile.gettempdir(), 'dorito-gallery-thumbs')   # small previews, kept OUTSIDE your repo
SLIM = ('upload', 'uploadsize', 'replace')          # these don't send the whole gallery list back (much faster for big imports)
NEEDS_BEFORE = ('folder/rename', 'folder/delete', 'pic/move', 'pic/delete')  # only these need a copy of the old list for the log


def thumb_key(rel):
    full = os.path.join(HERE, *rel.split('/'))
    st = os.stat(full)
    return hashlib.sha1(f'{rel}|{st.st_mtime_ns}|{st.st_size}'.encode()).hexdigest()


def safe_rel(rel):
    """A picture path inside media/ as a clean relative path, or None."""
    rel = (rel or '').replace('\\', '/').lstrip('/')
    full = os.path.abspath(os.path.join(HERE, *rel.split('/')))
    if (not rel.startswith('media/') or not full.startswith(os.path.join(HERE, 'media') + os.sep)
            or any(p.startswith('.') or p == '..' for p in rel.split('/')) or not os.path.isfile(full)):
        return None
    return rel


class H(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'   # keeps connections open: far fewer connections for lots of thumbnails

    def log_message(self, *a):
        pass

    def send(self, code, body, ctype='application/json', cache=None, etag=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        elif isinstance(body, str):
            body = body.encode()
        try:
            self.send_response(code)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', cache or 'no-store')
            if etag:
                self.send_header('ETag', etag)
            self.end_headers()
            if self.command != 'HEAD':
                self.wfile.write(body)
        except (BrokenPipeError, ConnectionError, OSError):
            pass  # the page stopped waiting (e.g. scrolled past a thumbnail): nothing to do

    def host_ok(self):
        return (self.headers.get('Host') or '').split(':')[0] in ('127.0.0.1', 'localhost')

    def do_GET(self):
        if not self.host_ok():
            return self.send(403, 'no', 'text/plain')
        u = urlparse(self.path)
        p = unquote(u.path)
        if p in ('/', '/manager'):
            return self.send(200, PAGE.replace('__TOKEN__', TOKEN), 'text/html; charset=utf-8')
        if p == '/api/log':
            since = int((parse_qs(u.query).get('since') or ['0'])[0])
            return self.send(200, [x for x in LOGS if x['n'] > since])
        if p == '/api/state':
            with LOCK:
                return self.send(200, g.load())
        if p == '/api/inventory':
            with LOCK:
                inv = inventory(g.load())
                inv['line'] = write_size_txt(inv['total'])
                inv['human'] = human(inv['total'])
                return self.send(200, inv)
        if p == '/thumb':  # small preview of a picture for the grid
            rel = safe_rel((parse_qs(u.query).get('p') or [''])[0])
            if not rel:
                return self.send(404, 'no', 'text/plain')
            d, fn = os.path.split(rel)
            for n in (256, 512):  # a resized copy made by the Sizes button is already a perfect thumbnail
                cp = os.path.join(HERE, *d.split('/'), SIZES_DIR, str(n), size_name(fn))
                if os.path.isfile(cp):
                    return self.send(200, open(cp, 'rb').read(), MIME.get(os.path.splitext(cp)[1].lower(), 'image/png'),
                                     cache='no-cache', etag=f'"{os.stat(cp).st_mtime_ns}"')
            tp = os.path.join(THUMB_DIR, thumb_key(rel))
            if os.path.isfile(tp):
                raw = open(tp, 'rb').read()
                return self.send(200, raw, 'image/jpeg' if raw[:2] == b'\xff\xd8' else 'image/png', cache='max-age=3600')
            return self.send(404, 'no thumbnail yet', 'text/plain')
        # static files from the repo folder (preview of your real site + pictures)
        rel = p.lstrip('/') or 'index.html'
        full = os.path.abspath(os.path.join(HERE, rel))
        ext = os.path.splitext(full)[1].lower()
        if (not full.startswith(HERE + os.sep) or any(part.startswith('.') for part in rel.split('/'))
                or ext in ('.py', '.yml', '.zip') or not os.path.isfile(full)):
            return self.send(404, 'not found', 'text/plain')
        st = os.stat(full)
        etag = f'"{st.st_mtime_ns}-{st.st_size}"'
        if self.headers.get('If-None-Match') == etag:   # unchanged: don't send the file again
            return self.send(304, b'', MIME.get(ext, 'application/octet-stream'), cache='no-cache', etag=etag)
        return self.send(200, open(full, 'rb').read(), MIME.get(ext, 'application/octet-stream'), cache='no-cache', etag=etag)

    def do_POST(self):
        if not self.host_ok() or self.headers.get('X-Token') != TOKEN:
            return self.send(403, {'error': 'Not allowed. Reload the page.'})
        u = urlparse(self.path)
        n = int(self.headers.get('Content-Length') or 0)
        body = self.rfile.read(n) if n else b''
        route = u.path[len('/api/'):]
        if route == 'thumb':  # the page made a small preview: keep it (outside your repo) so it only happens once
            try:
                rel = safe_rel((parse_qs(u.query).get('p') or [''])[0])
                if not rel or len(body) > 2_000_000:
                    return self.send(400, {'error': 'bad thumbnail'})
                os.makedirs(THUMB_DIR, exist_ok=True)
                open(os.path.join(THUMB_DIR, thumb_key(rel)), 'wb').write(body)
                return self.send(200, {})
            except Exception as e:
                return self.send(500, {'error': str(e)})
        try:
            with LOCK:
                data = g.load()
                before = json.loads(json.dumps(data)) if route in NEEDS_BEFORE else None
                args = {}
                if route == 'upload':
                    q = args = {k: v[0] for k, v in parse_qs(u.query).items()}
                    res = a_upload(data, q, body)
                elif route == 'uploadsize':
                    q = args = {k: v[0] for k, v in parse_qs(u.query).items()}
                    res = a_upload_size(data, q, body)
                elif route == 'replace':
                    q = args = {k: v[0] for k, v in parse_qs(u.query).items()}
                    res = a_replace(data, q, body)
                elif route in ACTIONS:
                    args = json.loads(body or b'{}')
                    res = ACTIONS[route](data, args)
                else:
                    return self.send(404, {'error': 'unknown action'})
                g.save(data)
                res = dict(res or {})
                log(describe(route, args, before, res, data), quiet=(route in ('uploadsize', 'replace')))
                if route not in SLIM:
                    res['data'] = data
                    write_size_txt(inventory(data)['total'])
            return self.send(200, res)
        except Err as e:
            log(f'Problem: {e}', 'err')
            return self.send(400, {'error': str(e)})
        except Exception as e:  # keep the window alive, show the problem
            log(f'Error: {type(e).__name__}: {e}', 'err')
            return self.send(500, {'error': f'{type(e).__name__}: {e}'})


PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dorito Gallery Manager</title>
<link rel="icon" type="image/gif" href="/media/SpinningDorito_pixel.gif">
<link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
<style>
body{overflow:auto;user-select:none;background:radial-gradient(ellipse at 50% 0%,#1b0a5c 0,#0a0630 55%,#05031a 100%) fixed}
body.anim{background:var(--void) url("/media/background.gif") center/cover no-repeat fixed}
.mgr{position:relative;display:flex;flex-direction:column;width:min(1280px,calc(100vw - 24px));height:calc(100vh - 24px);margin:12px auto;
  background:#26008fa6;border:3px solid;border-color:#0157c9 #0017e785 #0017e785;box-shadow:0 0 30px #0003cf55}
.mtb{display:flex;align-items:center;gap:8px;padding:2px 6px;background:#0003cf70;color:blueviolet;border-bottom:1px solid #0017e77a}
.mtb img{width:18px;height:18px}.mtb b{font-weight:400;flex:none}
.ctl{display:flex;gap:10px;align-items:center;margin-left:12px;color:blueviolet;font-size:16px;flex-wrap:nowrap;white-space:nowrap}
.mtb{flex-wrap:wrap;gap:6px}.mtb a{white-space:nowrap;padding:0 7px;font-size:17px}.mtb b{font-size:20px}
.mtb img,.mtb b{white-space:nowrap}
.ctl label{display:flex;align-items:center;gap:4px}
.ctl input{width:54px;font:inherit;font-size:16px;color:#ffa600;background:#07051acc;border:2px solid;border-color:#0017e785 #0157c9 #0157c9;padding:0 3px;outline:0;text-align:center}
.ctl input:focus{border-color:#3d8bff}
.status{flex-wrap:wrap;align-items:center;row-gap:2px;column-gap:14px}#st{flex:1 1 240px!important;min-width:200px}#note{flex:none!important}.status .bud{flex:none;display:flex;gap:6px;align-items:center;color:blueviolet}
.bud input{width:96px;font:inherit;font-size:16px;color:#ffa600;background:#07051acc;border:2px solid;border-color:#0017e785 #0157c9 #0157c9;padding:0 4px;outline:0}
.bud .b{font-size:16px;padding:0 9px}.bud .b[hidden]{display:none}
#gs{flex:none!important;color:#7df9ff;white-space:nowrap}
.mtb a{color:blueviolet;text-decoration:none;border:2px solid;border-color:#0157c9 #0017e785 #0017e785;background:#0003cf40;padding:0 10px;font-size:18px}
.mtb a{cursor:pointer}
.mtb a:hover{background:#4200ac99;color:#d9c2ff;border-color:#3d8bff #0157c9 #0157c9}
.mbar{display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:8px 10px 4px}
.sep{width:2px;align-self:stretch;background:#0017e785;margin:0 4px}
.b{font:inherit;font-size:18px;line-height:1.1;padding:1px 12px;color:blueviolet;background:#0003cf40;border:2px solid;border-color:#0157c9 #0017e785 #0017e785;cursor:pointer}
.b:hover:not(:disabled),.b:focus-visible{background:#4200ac99;color:#d9c2ff;border-color:#3d8bff #0157c9 #0157c9;outline:0}
.b:active:not(:disabled){background:#26008fe0}
.b:disabled{opacity:.35;cursor:default}
.b.go{color:#7df9ff;background:#0a3fb066;border-color:#3d8bff #0157c9 #0157c9}
.b.go:hover:not(:disabled),.b.go:focus-visible{color:#fff;background:#1766ff99;border-color:#7df9ff}
.tile .bd{position:absolute;left:3px;bottom:3px;background:#04123acc;color:#7df9ff;font-size:14px;line-height:1;padding:1px 4px;border:1px solid #3d8bff}
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
.tile .cp{font-size:14px;line-height:1.1;color:#7df9ff;opacity:.9}
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
.con{border-top:1px solid #0017e77a;background:#07051acc;height:130px;display:none;flex-direction:column}
.con.on{display:flex}
.conh{display:flex;align-items:center;gap:8px;padding:0 8px;color:blueviolet;font-size:16px;background:#0003cf40}
.conh b{font-weight:400;flex:1}
.conh button{font:inherit;font-size:15px;color:blueviolet;background:none;border:1px solid #0157c9;cursor:pointer;padding:0 8px}
.conh button:hover{color:#d9c2ff;background:#4200ac99}
.cl{flex:1;overflow:auto;padding:3px 8px;font-family:'Courier New',monospace;font-size:13px;line-height:1.35;user-select:text;color:#b9a3ff}
.cl div{white-space:pre-wrap;word-break:break-all}.cl .t{color:#6a58c8}.cl .err{color:#ff8a8a}.cl .ok{color:#7df9ff}.cl .ui{color:#ffa600}
.toast{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);background:#1c0a6ef2;border:2px solid #ffa600;color:#ffa600;padding:4px 16px;font-size:20px;z-index:30}
.toast.err{border-color:#ff6a6a;color:#ff9a9a}
</style></head>
<body>
<div class="mgr" id="mgr">
  <div class="mtb"><img src="/media/SpinningDorito_pixel.gif" alt=""><b>Dorito Gallery Manager</b><span class="ctl" title="How the grid loads previews of your pictures"><label title="How many previews are made at the same moment (1 to 8)">Image load batch <input type="number" id="atonce" min="1" max="8" step="1" value="2"></label><label title="Seconds to wait after each preview before starting the next one (0 = no wait). Decimals work, like 0.25">Delay <input type="text" inputmode="decimal" id="delay" value="0" title="Decimals work, like 0.25"> s</label></span><span style="flex:1"></span><a href="#" id="bgtog" title="Your animated space background uses a lot of graphics power. Off keeps the manager light.">Background: still</a><a href="#" id="contog" title="Show or hide the console that shows what the manager is doing">Console</a><a href="/index.html" target="_blank" title="Opens your real website from this computer">Preview my site</a></div>
  <div class="mbar" id="bar"></div>
  <div class="area" id="area"></div>
  <div class="con" id="con"><div class="conh"><b>Console:</b><button type="button" id="conclear">Clear</button><button type="button" id="conhide">Hide</button></div><div class="cl" id="cl"></div></div>
  <div class="status"><span id="gs" title="Everything inside your gallery folders: originals + resized copies"></span><div class="bud"><label title="Biggest total size you want the gallery to have. Examples: 900 MB, 1.5 GB">Max size <input id="budget" placeholder="900 MB" spellcheck="false"></label><button class="b go" type="button" id="fit" title="Shrinks every picture by the same percentage until everything fits">Compress to fit</button><button class="b danger" type="button" id="stop" hidden>Stop</button></div><span id="st"></span><span style="flex:none;text-align:right" id="note">Push in GitHub Desktop to publish.</span></div>
  <div class="drop" id="drop">Drop pictures here to add them<br>to this folder</div>
</div>
<input type="file" id="file" accept="image/*" multiple hidden>
<input type="file" id="dir" webkitdirectory multiple hidden>
<script>
const TOKEN='__TOKEN__';
let data=[],cur=null,sel=new Set(),deep=false,autoConv=true,stopFlag=false,inv=null,auto=false,showFiles=false,keepSub=true,autoSizes=true,sizesSel=[2048,1024,512,256];
try{showFiles=localStorage.getItem('dorito-showfiles')==='1';keepSub=localStorage.getItem('dorito-keepsub')!=='0';autoSizes=localStorage.getItem('dorito-autosizes')!=='0';autoConv=localStorage.getItem('dorito-autoconv')!=='0';$('budget').value=localStorage.getItem('dorito-budget')||'';const ss=JSON.parse(localStorage.getItem('dorito-sizes')||'null');if(Array.isArray(ss))sizesSel=ss}catch(e){}
const $=id=>document.getElementById(id);
const h=(t,a,...k)=>{const e=document.createElement(t);for(const[n,v]of Object.entries(a||{})){if(n==='class')e.className=v;else if(n.startsWith('on'))e.addEventListener(n.slice(2),v);else if(v!==false&&v!=null)e.setAttribute(n,v===true?'':v)}k.flat().forEach(c=>e.append(c));return e};
const kids=f=>f.folders||[];
const findNode=(p,l=data)=>{for(const f of l){if(f.folder===p)return f;const r=findNode(p,kids(f));if(r)return r}return null};
const parentOf=(p,l=data,par=null)=>{for(const f of l){if(f.folder===p)return par;const r=parentOf(p,kids(f),f.folder);if(r!==undefined)return r}};
const flat=(l=data,pre='')=>l.flatMap(f=>[{f,label:pre+f.name},...flat(kids(f),pre+f.name+' / ')]);
const total=f=>f.images.length+kids(f).reduce((a,c)=>a+total(c),0);
const folder=()=>findNode(cur);
const clrSel=()=>{sel.clear();deep=false};
const underAll=l=>l.flatMap(f=>[...f.images.map(it=>({p:f.folder,it})),...underAll(kids(f))]);
const under=p=>p?underAll([findNode(p)]):underAll(data);
const targets=()=>deep?under(cur):(cur?folder().images.filter(x=>sel.has(x.file)).map(it=>({p:cur,it})):[]);
const fmtB=n=>n>=1073741824?(n/1073741824).toFixed(2)+' GB':(n/1048576).toFixed(1)+' MB';
const mimeOf=n=>/\.jpe?g$/i.test(n)?'image/jpeg':/\.webp$/i.test(n)?'image/webp':'image/png';
const FITRE=/\.(jpe?g|png|webp)$/i;
let szT=0;async function updSize(){try{inv=await (await fetch('/api/inventory')).json();$('gs').textContent='Gallery size: '+inv.human}catch(e){}return inv}
const updSoon=()=>{clearTimeout(szT);szT=setTimeout(updSize,300)};
const trailOf=p=>{const out=[];let x=p;while(x){out.unshift(findNode(x).name);x=parentOf(x)}return out.join(' / ')};
const niceFile=f=>f.replace(/\.[^.]+$/,'');
/* ---------- console window ---------- */
let logLast=0,conOn=false;try{conOn=localStorage.getItem('dorito-console')==='1'}catch(e){}
function conLine(t,m,k){const cl=$('cl'),near=cl.scrollHeight-cl.scrollTop-cl.clientHeight<30,d=h('div',{},h('span',{class:'t'},'['+t+'] '),h('span',{class:k||''},m));cl.append(d);while(cl.children.length>400)cl.firstChild.remove();if(near)cl.scrollTop=cl.scrollHeight}
const convLabel=()=>h('label',{class:'lbl',title:'Pictures you add or import are shrunk to at most 2048 px (longest side) before they are saved in your repo. Needs a png, jpg or webp.'},h('input',{type:'checkbox',checked:autoConv,onchange:e=>{autoConv=e.target.checked;try{localStorage.setItem('dorito-autoconv',autoConv?'1':'0')}catch(x){}}}),'auto-convert to 2048');
const clock=()=>new Date().toTimeString().slice(0,8);
function clog(m,k){conLine(clock(),m,k||'ui')}
async function pollLog(){try{const r=await fetch('/api/log?since='+logLast),l=await r.json();l.forEach(x=>{conLine(x.t,x.m,x.k==='err'?'err':'ok');logLast=Math.max(logLast,x.n)})}catch(e){}}
function setCon(on){conOn=on;$('con').classList.toggle('on',on);if(on)pollLog();try{localStorage.setItem('dorito-console',on?'1':'0')}catch(e){}}
function toast(m,err){const t=h('div',{class:'toast'+(err?' err':'')},m);document.body.append(t);setTimeout(()=>t.remove(),err?5000:2600)}
async function api(route,body,q){
  const r=await fetch('/api/'+route+(q||''),{method:'POST',headers:{'X-Token':TOKEN},body:body instanceof Uint8Array||body instanceof Blob?body:JSON.stringify(body||{})});
  const j=await r.json();if(!r.ok)throw new Error(j.error||'Something went wrong');
  if(j.data){data=j.data;if(cur&&!folder()){cur=null;clrSel()}}return j}
async function refresh(){try{data=await (await fetch('/api/state')).json();if(cur&&!folder()){cur=null;clrSel()}}catch(e){}updSoon()}
/* small previews: the grid shows little copies made once (and kept outside your repo) instead of decoding every full-size picture */
/* Heavy picture work (previews, resized copies) runs in background workers, so the window itself never freezes. */
const WSRC=`
self.onmessage=async e=>{const m=e.data;
 try{
  if(m.kind==='thumb'){
    const bl=await (await fetch(m.url)).blob();
    if(bl.size<80000){postMessage({done:1,small:1});return}
    let bm;try{bm=await createImageBitmap(bl,{resizeWidth:240,resizeQuality:'medium'})}catch(_){bm=await createImageBitmap(bl)}
    const k=Math.min(1,240/Math.max(bm.width,bm.height)),w=Math.max(1,Math.round(bm.width*k)),h=Math.max(1,Math.round(bm.height*k)),c=new OffscreenCanvas(w,h);
    c.getContext('2d').drawImage(bm,0,0,w,h);bm.close();
    postMessage({done:1,blob:await c.convertToBlob({type:m.jpeg?'image/jpeg':'image/png',quality:.8})});
  }else if(m.kind==='fit'){
    const bl=m.blob||await (await fetch(m.url)).blob(),bm=await createImageBitmap(bl),w=bm.width,h=bm.height,mx=Math.max(w,h),lossy=m.type!=='image/png',tg=m.target||0;
    let k=m.limit&&mx>m.limit?m.limit/mx:1;
    if(k===1&&!tg){bm.close();postMessage({done:1,same:1,max:mx});return}
    const mk=k=>{const cw=Math.max(1,Math.round(w*k)),ch=Math.max(1,Math.round(h*k)),c=new OffscreenCanvas(cw,ch),x=c.getContext('2d');x.imageSmoothingEnabled=!m.px;x.imageSmoothingQuality='high';x.drawImage(bm,0,0,cw,ch);return c};
    const enc=(c,q)=>c.convertToBlob({type:m.type,quality:q});
    const q0=m.q||.92;let c=mk(k),out=await enc(c,q0),ow=c.width,oh=c.height;
    if(tg&&out.size>tg){
      for(let round=0;round<5;round++){
        if(lossy){const lo=.4,t=await enc(c,lo);
          if(t.size<=tg){let a=lo,b=q0;out=t;for(let i=0;i<5;i++){const mid=(a+b)/2,x=await enc(c,mid);if(x.size<=tg){out=x;a=mid}else b=mid}ow=c.width;oh=c.height;break}
          out=t;ow=c.width;oh=c.height}
        else if(out.size<=tg)break;
        k*=Math.max(.1,Math.min(.95,Math.sqrt(tg/out.size)*.96));c=mk(k);
        if(!lossy){out=await enc(c,q0);ow=c.width;oh=c.height}}}
    bm.close();postMessage({done:1,blob:out,max:Math.max(ow,oh),w:ow,h:oh});
  }else{
    const bm=await createImageBitmap(m.blob),w=bm.width,h=bm.height,mx=Math.max(w,h);let from=bm;
    for(const N of m.sizes){if(N>=mx)continue;const k=N/mx,cw=Math.max(1,Math.round(w*k)),ch=Math.max(1,Math.round(h*k)),c=new OffscreenCanvas(cw,ch),g=c.getContext('2d');
      g.imageSmoothingEnabled=!m.px;g.imageSmoothingQuality='high';g.drawImage(from,0,0,cw,ch);
      postMessage({N,max:mx,blob:await c.convertToBlob({type:m.type,quality:.92})});from=c}
    bm.close();postMessage({done:1,max:mx});
  }
 }catch(err){postMessage({done:1,error:String((err&&err.message)||err)})}};`;
let pool=null;
function getPool(){if(pool!==null)return pool;
  try{const url=URL.createObjectURL(new Blob([WSRC],{type:'text/javascript'}));
    pool={url,ws:[],q:[],timer:0};ensureWorkers(pool,2);
    if(typeof OffscreenCanvas==='undefined')pool=false}catch(e){pool=false}
  return pool}
function ensureWorkers(P,n){while(P.ws.length<Math.min(8,n)){const o={w:new Worker(P.url),busy:null,cool:0};
  o.w.onmessage=e=>{const m=e.data,t=o.busy;if(!t)return;if(m.done){o.busy=null;if(t.msg.kind==='thumb')o.cool=Date.now()+delayMs();t.res(m);pump()}else t.part(m)};
  o.w.onerror=()=>{const t=o.busy;o.busy=null;if(t)t.res({done:1,error:'worker error'});pump()};P.ws.push(o)}}
const atOnce=()=>Math.max(1,Math.min(8,parseInt($('atonce').value)||1)),delayMs=()=>{const d=parseFloat(String($('delay').value).replace(',','.'));return isNaN(d)||d<0?0:Math.min(d,60)*1000};
function pump(){const P=pool;if(!P)return;const L=atOnce();ensureWorkers(P,Math.max(2,L));let again=true,wait=1e9;
  while(again&&P.q.length){again=false;const now=Date.now();
    for(const o of P.ws){if(o.busy)continue;
      const run=P.ws.filter(x=>x.busy&&x.busy.msg.kind==='thumb').length,cool=o.cool-now,okThumb=run<L&&cool<=0;
      const idx=P.q.findIndex(t=>t.msg.kind!=='thumb'||okThumb);
      if(idx<0){if(run<L&&cool>0&&P.q.some(t=>t.msg.kind==='thumb'))wait=Math.min(wait,cool);continue}
      const t=P.q.splice(idx,1)[0];again=true;
      if(t.skip&&t.skip()){t.res({done:1,skipped:1});continue}o.busy=t;o.w.postMessage(t.msg)}}
  if(wait<1e9&&!P.timer)P.timer=setTimeout(()=>{P.timer=0;pump()},wait+5)}
function runTask(msg,opt={}){const P=getPool();if(!P)return Promise.resolve({done:1,error:'noworker'});
  return new Promise(res=>{const t={msg,res,part:opt.part||(()=>{}),skip:opt.skip};opt.lifo?P.q.unshift(t):P.q.push(t);pump()})}
/* small previews: the grid shows little copies made once (and kept outside your repo) instead of decoding every full-size picture */
const encPath=rel=>rel.split('/').map(encodeURIComponent).join('/');
let thumbsLeft=0;
const noteDefault=()=>'Push in GitHub Desktop to publish.';
function thumbFor(img,rel){img.onerror=null;thumbsLeft++;$('note').textContent='Making previews: '+thumbsLeft+' left';
  makeThumb(img,rel).finally(()=>{thumbsLeft--;$('note').textContent=thumbsLeft>0?'Making previews: '+thumbsLeft+' left':noteDefault()})}
async function makeThumb(img,rel){
  const gone=()=>!img.isConnected||!img._vis;                 /* scrolled away or folder closed: skip it, it comes back when you scroll to it */
  const orig=()=>{img.src='/'+encPath(rel)};
  const r=await runTask({kind:'thumb',url:location.origin+'/'+encPath(rel),jpeg:/\.jpe?g$/i.test(rel)},{lifo:true,skip:gone});
  if(r.skipped){delete img.dataset.req;return}
  if(r.small||r.error){orig();return}
  try{await fetch('/api/thumb?p='+encodeURIComponent(rel),{method:'POST',headers:{'X-Token':TOKEN},body:r.blob});
    if(img.isConnected)img.src='/thumb?p='+encodeURIComponent(rel)+'&v='+Date.now()}catch(e){orig()}}
async function act(route,body,msg){updSoon();try{const j=await api(route,body);if(msg)toast(msg);if(j.message)toast(j.message);render();return j}catch(e){toast(e.message,1);render()}}

/* ---------- dialogs ---------- */
function dialog(title,body,buttons,onOpen){return new Promise(res=>{
  const done=v=>{o.remove();res(v)};
  const foot=h('div',{class:'dfoot'},buttons.map(b=>h('button',{class:'b'+(b.danger?' danger':'')+(b.go?' go':''),type:'button',onclick:()=>done(b.value)},b.label)));
  const o=h('div',{class:'ovl',onmousedown:e=>{if(e.target===o)done(null)}},h('div',{class:'dlg'},h('h3',{},title),h('div',{class:'dbody'},body),foot));
  o.addEventListener('keydown',e=>{if(e.key==='Escape')done(null)});
  document.body.append(o);if(onOpen)onOpen(o,done)})}
async function askText(title,label,val='',ok='OK'){
  const i=h('input',{class:'inp',value:val,spellcheck:'false'});
  const r=await dialog(title,[label?h('p',{},label):'',i],[{label:'Cancel',value:null},{label:ok,value:true}],(o,done)=>{setTimeout(()=>{i.focus();i.select()},30);i.addEventListener('keydown',e=>{if(e.key==='Enter')done(true)})});
  return r?i.value:null}
async function confirmBox(title,text,ok,danger){return !!await dialog(title,[h('p',{},text)],[{label:'Cancel',value:null},{label:ok,value:true,danger}])}
async function pickFolder(title,list){
  return dialog(title,[h('div',{class:'pick'},list.map(x=>h('button',{class:'b',type:'button',onclick:e=>e.target.closest('.ovl').dispatchEvent(new CustomEvent('pick',{detail:x.f.folder}))},x.label+'  ('+x.f.images.length+')')))],[{label:'Cancel',value:null}],(o,done)=>o.addEventListener('pick',e=>done(e.detail)))}

/* ---------- actions ---------- */
async function newFolder(){const n=await askText(cur?'New folder inside "'+folder().name+'"':'New folder','Name shown in the gallery:','','Create');if(n===null)return;
  const px=cur?false:await confirmBox('Pixel art?','Is this folder pixel art? (keeps pictures crisp when enlarged)','Yes, pixel art');
  await act('folder/new',{name:n,parent:cur,pixelated:px},'Folder created')}
async function renameFolder(){const f=folder();const n=await askText('Rename folder','Text shown in the gallery:',f.name,'Save');if(n!==null)await act('folder/rename',{folder:cur,name:n},'Renamed')}
async function deleteFolder(){const f=folder();
  const par=parentOf(cur),subs=flat(kids(f)).length;
  const r=await dialog('Delete folder','"'+f.name+'" has '+total(f)+' picture(s)'+(subs?' and '+subs+' sub-folder(s)':'')+' in total.',[{label:'Cancel',value:null},{label:'Hide folder, keep files',value:'keep'},{label:'Delete folder AND pictures',value:'del',danger:1}]);
  if(!r)return;await act('folder/delete',{folder:cur,deleteFiles:r==='del'},'Folder removed');cur=par||null;clrSel();render()}
async function pixelToggle(){const f=folder();await act('folder/pixel',{folder:cur,value:!f.pixelated},f.pixelated?'Pixel art off':'Pixel art on')}
async function renamePics(){const f=folder(),files=f.images.filter(x=>sel.has(x.file));if(!files.length)return;
  const ins=files.map(x=>h('input',{class:'inp',value:x.title,spellcheck:'false','data-f':x.file}));
  const rows=files.map((x,i)=>h('div',{class:'rrow'},h('img',{src:'/'+f.folder+x.file}),ins[i]));
  const r=await dialog('Rename ('+files.length+')',[h('p',{},'This is the text shown in the gallery, not the file name.'),...rows],[{label:'Cancel',value:null},{label:'Save',value:true}],(o,done)=>{setTimeout(()=>{ins[0].focus();ins[0].select()},30);ins.forEach(i=>i.addEventListener('keydown',e=>{if(e.key==='Enter')done(true)}))});
  if(!r)return;const titles={};ins.forEach(i=>titles[i.dataset.f]=i.value);await act('pic/retitle',{folder:cur,titles},'Saved')}
async function movePics(){const others=flat().filter(x=>x.f.folder!==cur);if(!others.length){toast('Make another folder first',1);return}
  const to=await pickFolder('Move '+sel.size+' picture(s) to...',others);if(!to)return;
  const n=sel.size;await act('pic/move',{from:cur,to,files:[...sel]},'Moved '+n);clrSel();render()}
async function deletePics(){const t=targets(),n=t.length;if(!n)return;if(!await confirmBox('Delete pictures','Delete '+n+' picture(s)'+(deep?' (including sub-folders)':'')+'? The files (and their resized copies) are deleted from your repo folder too (you can undo in GitHub Desktop before committing).','Delete',1))return;
  const by={};t.forEach(x=>(by[x.p]=by[x.p]||[]).push(x.it.file));for(const p in by)await api('pic/delete',{folder:p,files:by[p]});
  toast('Deleted '+n);clrSel();await refresh();render()}
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
  await act('pic/renamefiles',{folder:cur,map:list.map((x,i)=>[x.file,n[i]]),retitle:retitle.checked},'File names changed');clrSel();render()}
async function sortPics(){const r=await dialog('Sort pictures',[h('div',{class:'pick'},[h('button',{class:'b',type:'button',onclick:e=>e.target.closest('.ovl').dispatchEvent(new CustomEvent('pick',{detail:'title'}))},'By shown name (A to Z)'),h('button',{class:'b',type:'button',onclick:e=>e.target.closest('.ovl').dispatchEvent(new CustomEvent('pick',{detail:'file'}))},'By file name (numbers in order)')])],[{label:'Cancel',value:null}],(o,done)=>o.addEventListener('pick',e=>done(e.detail)));
  if(r)await act('pic/sort',{folder:cur,by:r},'Sorted')}
/* ---------- resized copies (Unity-style max sizes), made in the browser and saved next to the picture ---------- */
const ALLSIZES=[2048,1024,512,256,128,64,32];
const isPx=p=>{let x=p;while(x){const f=findNode(x);if(f&&f.pixelated)return true;x=parentOf(x)}return false};
const loadImg=blob=>new Promise((res,rej)=>{const u=URL.createObjectURL(blob),i=new Image();i.onload=()=>{res(i);setTimeout(()=>URL.revokeObjectURL(u),1500)};i.onerror=()=>{URL.revokeObjectURL(u);rej(new Error('unreadable'))};i.src=u});
async function makeSizes(path,file,blob,sizes){
  const ext=(file.match(/\.([^.]+)$/)||[0,''])[1].toLowerCase(),type=(ext==='jpg'||ext==='jpeg')?'image/jpeg':ext==='webp'?'image/webp':'image/png';
  let n=0,chain=Promise.resolve();
  const r=await runTask({kind:'sizes',blob,sizes:[...sizes].sort((a,b)=>b-a),type,px:isPx(path)},{part:m=>{
    chain=chain.then(async()=>{await api('uploadsize',new Uint8Array(await m.blob.arrayBuffer()),'?folder='+encodeURIComponent(path)+'&file='+encodeURIComponent(file)+'&size='+m.N+'&max='+m.max);n++}).catch(e=>clog(file+': '+e.message,'err'))}});
  await chain;
  if(r.error&&!n)return makeSizesMain(path,file,blob,sizes);   /* worker couldn't read it (e.g. SVG): do it the slower way */
  if(!n&&r.max)await api('pic/meta',{folder:path,file,max:r.max});
  return n}
async function makeSizesMain(path,file,blob,sizes){
  let bm;try{bm=await createImageBitmap(blob)}catch(e){try{bm=await loadImg(blob)}catch(e2){clog('Could not read '+file+' to resize it (skipped)','err');return 0}}
  const w=bm.width||bm.naturalWidth,h=bm.height||bm.naturalHeight;if(!w||!h)return 0;
  const m=Math.max(w,h),px=isPx(path),ext=(file.match(/\.([^.]+)$/)||[0,''])[1].toLowerCase(),type=(ext==='jpg'||ext==='jpeg')?'image/jpeg':ext==='webp'?'image/webp':'image/png';
  let n=0,from=bm,prev=null;
  for(const N of [...sizes].sort((a,b)=>b-a)){if(N>=m)continue;  /* biggest first: each copy is made from the one before (far less work than from the full picture every time) */
    const k=N/m,c=document.createElement('canvas');c.width=Math.max(1,Math.round(w*k));c.height=Math.max(1,Math.round(h*k));
    const g=c.getContext('2d');g.imageSmoothingEnabled=!px;g.imageSmoothingQuality='high';g.drawImage(from,0,0,c.width,c.height);
    if(prev){prev.width=prev.height=0}else if(bm.close){bm.close()}
    prev=c;from=c;
    const bl=await new Promise(r=>c.toBlob(r,type,.92));if(!bl)continue;
    await api('uploadsize',new Uint8Array(await bl.arrayBuffer()),'?folder='+encodeURIComponent(path)+'&file='+encodeURIComponent(file)+'&size='+N+(n?'':'&max='+m));n++}
  if(!n)await api('pic/meta',{folder:path,file,max:m});   /* remember the size, so we never try the bigger sizes again */
  if(prev)prev.width=prev.height=0;else if(bm.close)bm.close();
  return n}
const needs=(it,N)=>!(it.sizes||[]).includes(N)&&(!it.max||N<it.max);
async function prep(file,path){
  if(!autoConv||!FITRE.test(file.name))return file;
  const r=await runTask({kind:'fit',blob:file,type:mimeOf(file.name),limit:2048,px:isPx(path)});
  if(r.blob&&r.blob.size<file.size){clog(file.name+': converted to '+r.w+' x '+r.h+' ('+fmtB(file.size)+' -> '+fmtB(r.blob.size)+')');return r.blob}
  return file}
function busy(on,t){$('stop').hidden=!on;$('fit').disabled=on;if(on)stopFlag=false;if(t)$('st').textContent=t}
$('stop').onclick=()=>{stopFlag=true;$('stop').textContent='Stopping...'};
async function fitJobs(list,o){
  /* o: {limit, ratio}. Re-makes each picture (same name) smaller; originals are replaced only when the new file is smaller. */
  busy(true);let i=0,k=0,saved=0,changed=0,same=0,bad=0;const total=list.length;
  const one=async()=>{while(!stopFlag){const j=list[i++];if(!j)return;const it=j.it;
    $('st').textContent=(o.label||'Working')+' '+(++k)+' of '+total+' ... saved so far '+fmtB(saved);
    try{
      const r=await runTask({kind:'fit',url:location.origin+'/'+encPath(j.p+it.file)+'?v='+Date.now(),type:mimeOf(it.file),limit:o.limit||0,target:o.ratio?Math.floor(j.b*o.ratio):0,px:j.px});
      if(r.error){bad++;clog(it.file+': could not read it ('+r.error+')','err');continue}
      if(r.same){same++;await api('pic/meta',{folder:j.p,file:it.file,max:r.max});continue}
      if(!r.blob||r.blob.size>=j.b){same++;continue}
      const x=await api('replace',new Uint8Array(await r.blob.arrayBuffer()),'?folder='+encodeURIComponent(j.p)+'&file='+encodeURIComponent(it.file)+'&max='+r.max);
      saved+=x.saved||0;changed++;clog(it.file+': '+fmtB(j.b)+' -> '+fmtB(r.blob.size)+' ('+r.w+' x '+r.h+')','ok')
    }catch(e){bad++;clog(it.file+': '+e.message,'err')}}};
  await Promise.all([one(),one()]);
  const stopped=stopFlag;busy(false);$('stop').textContent='Stop';
  await refresh();await updSize();render();
  const msg=(stopped?'Stopped. ':'Done. ')+changed+' picture(s) made smaller, saved '+fmtB(saved)+(same?', '+same+' left as they were':'')+(bad?', '+bad+' failed':'')+'.';
  clog(msg,'ok');toast(msg);return{changed,saved}}
const fitable=(l,o)=>l.filter(x=>FITRE.test(x.it.file)&&(o.ratio?!x.px:true));
let convN=2048;
async function convertDlg(){
  const t=targets(),sc0=t.length?t:under(cur);if(!sc0.length){toast('No pictures here');return}
  const pick=h('select',{style:'font:inherit;font-size:20px;color:#ffa600;background:#07051acc;border:2px solid #0157c9;padding:2px 6px'},...ALLSIZES.map(N=>h('option',{value:N,selected:N===convN},N+' px')));
  const r0=await dialog('Replace originals with a smaller size',[h('p',{},'Pick the biggest size (longest side) the ORIGINAL files should keep. Every picture bigger than that is replaced, under the same name, by a resized version of itself. Pictures already that small are left alone. Do this BEFORE "Compress to fit" so the compression has less to do.'),h('label',{class:'lbl'},'Size: ',pick)],[{label:'Cancel',value:null},{label:'Next',value:'ok',go:1}]);
  if(!r0)return;convN=+pick.value;const N=convN;
  const sc=t.length?t:under(cur),what=t.length?t.length+' selected picture(s)':'ALL '+sc.length+' pictures'+(cur?' in this folder and its sub-folders':' in the whole gallery');
  const inv0=await updSize(),bytes=new Map((inv0?inv0.items:[]).map(x=>[x.p+x.f,x]));
  const list=fitable(sc,{}).filter(x=>!(x.it.max&&x.it.max<=N)).map(x=>{const e=bytes.get(x.p+x.it.file);return{p:x.p,it:x.it,b:e?e.b:0,px:e?e.px:false}}).filter(x=>x.b>0);
  if(!list.length){toast('Nothing to replace: those pictures are already '+N+' px or smaller (or not png/jpg/webp).');return}
  if(!await confirmBox('Replace originals ('+N+' px)','Make '+what+' at most '+N+' px on the longest side? Pictures already small enough are left alone, nothing is ever enlarged. This REPLACES the original files in your repo folder (same names) - keep a backup of anything you cannot lose. gif, svg, bmp and avif are not touched.','Replace originals',1))return;
  await fitJobs(list,{limit:N,label:'Shrinking'})}
function parseBudget(t){const m=String(t||'').trim().replace(',','.').match(/^([\d.]+)\s*(gb|g|mb|m)?/i);if(!m)return 0;const v=parseFloat(m[1]);if(!(v>0))return 0;
  const u=(m[2]||'').toLowerCase();return Math.round(v*((u==='gb'||u==='g')||(!u&&v<=20)?1073741824:1048576))}
async function fitToBudget(){
  const bud=parseBudget($('budget').value);if(!bud){toast('Type the biggest size you want first, for example 900 MB or 1.5 GB',1);$('budget').focus();return}
  try{localStorage.setItem('dorito-budget',$('budget').value)}catch(e){}
  const v=await updSize();if(!v){toast('Could not measure the gallery',1);return}
  if(v.total<=bud){toast('The gallery is already '+fmtB(v.total)+', under your limit of '+fmtB(bud)+'. Nothing to do.');return}
  const comp=v.items.filter(x=>FITRE.test(x.f)&&!x.px),O=comp.reduce((a,x)=>a+x.b,0),fixed=v.total-O,room=bud*.97-fixed;
  if(room<O*.03){await dialog('Cannot fit',[h('p',{},'Your limit is '+fmtB(bud)+', but '+fmtB(fixed)+' of the gallery cannot be shrunk here (resized copies, gif/svg files, pixel-art folders). Remove resized copies with "Sizes" > "Remove checked sizes", or raise the limit.')],[{label:'OK',value:1,go:1}]);return}
  const ratio=room/O,pct=Math.round(ratio*100);
  if(!await confirmBox('Compress to fit '+fmtB(bud),'Gallery now: '+fmtB(v.total)+'. Every one of the '+comp.length+' pictures will be compressed the same amount, down to about '+pct+'% of its current file size, aiming for about '+fmtB(bud*.97)+' in total.'+(ratio<.35?' That is a LOT: pictures will look noticeably softer.':'')+' This REPLACES the original files in your repo folder, so keep a backup of anything you cannot lose. Resized copies ('+fmtB(fixed)+' of other files) are not touched. You can press Stop at any time; finished pictures stay finished.','Compress',1))return;
  const list=comp.map(x=>{const it=findNode(x.p).images.find(i=>i.file===x.f);return it&&{p:x.p,it,b:x.b,px:false}}).filter(Boolean);
  await fitJobs(list,{ratio,label:'Compressing'});
  if(inv&&inv.total>bud)toast('Now '+fmtB(inv.total)+' - still a little over '+fmtB(bud)+'. Press "Compress to fit" again to squeeze the rest.',1)}
$('fit').onclick=fitToBudget;$('budget').addEventListener('change',()=>{try{localStorage.setItem('dorito-budget',$('budget').value)}catch(e){}});
async function sizesDialog(){const t=targets(),list=t.length?t:under(cur);if(!list.length)return;
  const boxes=ALLSIZES.map(N=>h('input',{type:'checkbox',checked:sizesSel.includes(N),'data-n':N}));
  const rows=ALLSIZES.map((N,i)=>{const have=list.filter(x=>(x.it.sizes||[]).includes(N)).length,todo=list.filter(x=>needs(x.it,N)).length;
    return h('label',{class:'lbl'},boxes[i],N+' px   ',h('span',{style:'color:#7df9ff'},have+' already made'+(todo?', '+todo+' to make':', nothing to make')))});
  const force=h('input',{type:'checkbox'});
  const r=await dialog('Resized copies',[h('p',{},(t.length?'For the '+list.length+' selected picture(s).':'Nothing selected, so this is for ALL '+list.length+' pictures here'+(cur?' (including sub-folders)':'')+'.')+' Each copy gets its own direct link, and you pick the size next to the link on your website (like the Max Size box in Unity).'),
    h('p',{style:'color:#ffa600'},'VRChat can only load images up to 2048 px. A picture is never enlarged: sizes at or above its own size are skipped. Resized copies add to the gallery size.'),...rows,
    h('p',{},'Copies that already exist are skipped, so nothing gets made twice.'),h('label',{class:'lbl'},force,'make them again anyway (replaces existing copies)')],
    [{label:'Cancel',value:null},{label:'Remove checked sizes',value:'rm',danger:1},{label:'Make copies',value:'make',go:1}]);
  if(!r)return;const chosen=boxes.filter(b=>b.checked).map(b=>+b.dataset.n);
  if(!chosen.length){toast('Tick at least one size',1);return}
  sizesSel=chosen;try{localStorage.setItem('dorito-sizes',JSON.stringify(chosen))}catch(e){}
  if(r==='rm'){const by={};list.forEach(x=>(by[x.p]=by[x.p]||[]).push(x.it.file));for(const p in by)await api('pic/removesizes',{folder:p,files:by[p],sizes:chosen});await refresh();render();toast('Removed those copies');return}
  let made=0,k=0,skipped=0;for(const x of list){const it=x.it;$('st').textContent='Making copies '+(++k)+' of '+list.length+'...';
    const need=chosen.filter(N=>force.checked?(!it.max||N<it.max):needs(it,N));
    if(!need.length){skipped++;continue}
    clog('Making resized copies of '+it.file+' ('+need.join(', ')+')...');
    try{const bl=await (await fetch('/'+x.p+it.file)).blob();made+=await makeSizes(x.p,it.file,bl,need)}catch(e){toast(it.file+': '+e.message,1)}}
  await refresh();render();clog('Done: made '+made+' cop'+(made===1?'y':'ies')+(skipped?', skipped '+skipped+' picture(s) that already had all of them':''),'ok');
  toast('Made '+made+' resized cop'+(made===1?'y':'ies')+(skipped?' ('+skipped+' picture(s) already had them)':'')+'. Pick a size next to the link on your website after you push.')}
async function upload(files){const f=folder();if(!f)return;files=[...files].filter(x=>/\.(png|jpe?g|gif|webp|bmp|svg|avif)$/i.test(x.name));
  if(!files.length){toast('No pictures found (png, jpg, gif, webp, bmp, svg, avif)',1);return}
  const before=new Set(f.images.map(x=>x.file));let ok=0;
  for(const[i,x]of files.entries()){$('st').textContent='Adding '+(i+1)+' of '+files.length+'...';clog('Reading '+x.name+' ('+Math.round(x.size/1024)+' KB), sending it to the manager...');
    try{const bl=await prep(x,cur),j=await api('upload',new Uint8Array(await bl.arrayBuffer()),'?folder='+encodeURIComponent(cur)+'&name='+encodeURIComponent(x.name)+(auto?'&auto=1':''));ok++;if(autoSizes)await makeSizes(cur,j.added,bl,sizesSel)}catch(e){toast(x.name+': '+e.message,1)}
    await new Promise(r=>setTimeout(r,0))}
  await refresh();
  deep=false;sel=new Set(folder().images.filter(x=>!before.has(x.file)).map(x=>x.file));render();
  toast('Added '+ok+'. They are selected: "Rename" changes the shown names, "Rename files" the file names.')}
const IMGRE=/\.(png|jpe?g|gif|webp|bmp|svg|avif)$/i,byPath=(a,b)=>(a.webkitRelativePath||a.name).localeCompare(b.webkitRelativePath||b.name,undefined,{numeric:true,sensitivity:'base'});
async function importItems(items){
  /* items: [{file, dirs:['Trip','day2']}]  (dirs = the sub-folders it was inside, starting with the folder you chose) */
  if(!keepSub)items=items.map(i=>({file:i.file,dirs:cur||!i.dirs.length?[]:[i.dirs[0]]}));  /* toggle off: no sub-folders, everything goes into one folder */
  items=items.filter(i=>IMGRE.test(i.file.name)).sort((a,b)=>(a.dirs.join('/')+'/'+a.file.name).localeCompare(b.dirs.join('/')+'/'+b.file.name,undefined,{numeric:true,sensitivity:'base'}));
  if(!items.length){toast('No pictures found in there (png, jpg, gif, webp, bmp, svg, avif)',1);return}
  const roots=[...new Set(items.filter(i=>i.dirs.length).map(i=>i.dirs[0]))],loose=items.filter(i=>!i.dirs.length),rn={};
  let px=false,looseName=null;
  if(!cur){
    if(roots.length===1&&!loose.length){const n=await askText('Import folder',items.length+' picture(s) found. Name for the new gallery folder:',roots[0],'Import');if(n===null)return;rn[roots[0]]=n}
    else if(loose.length){looseName=await askText('Import pictures',items.length+' picture(s) found. Put them in a new gallery folder called:','New folder','Import');if(looseName===null)return}
    px=await confirmBox('Pixel art?','Is this pixel art? (keeps pictures crisp when enlarged)','Yes, pixel art');
  }
  const cache={};
  const ensure=async(parent,name,pix)=>{const k=(parent||'')+'|'+name.toLowerCase();if(cache[k])return cache[k];const j=await api('folder/new',{name,parent,pixelated:pix,ensure:true});return cache[k]=j.path};
  let done=0,ok=0,made=new Set();
  for(const it of items){
    $('st').textContent='Importing '+(++done)+' of '+items.length+'...';clog('Importing '+(it.dirs.concat(it.file.name)).join(' / ')+'  ('+done+'/'+items.length+')');
    try{
      let p=cur;
      if(it.dirs.length){for(let k=0;k<it.dirs.length;k++){p=await ensure(p,k===0&&rn[it.dirs[0]]?rn[it.dirs[0]]:it.dirs[k],px&&!p);if(k===0&&!cur)made.add(p)}}
      else if(!cur){p=await ensure(null,looseName,px);made.add(p)}
      const bl=await prep(it.file,p),j=await api('upload',new Uint8Array(await bl.arrayBuffer()),'?folder='+encodeURIComponent(p)+'&name='+encodeURIComponent(it.file.name));ok++;if(autoSizes)await makeSizes(p,j.added,bl,sizesSel)
    }catch(e){toast(it.file.name+': '+e.message,1)}
    await new Promise(r=>setTimeout(r,0));
  }
  await refresh();
  clrSel();if(!cur&&made.size===1)cur=[...made][0];render();
  toast('Imported '+ok+' picture(s) with their folders. Open a folder and use Rename / Rename files to name them.')}
/* collect pictures from dropped folders (goes through sub-folders too), remembering which folder each was in */
function walkEntry(en,out,dirs){return new Promise(res=>{
  if(en.isFile)en.file(f=>{out.push({file:f,dirs});res()},()=>res());
  else if(en.isDirectory){const r=en.createReader(),all=[],d=[...dirs,en.name];const next=()=>r.readEntries(async es=>{if(!es.length){await Promise.all(all.map(x=>walkEntry(x,out,d)));res()}else{all.push(...es);next()}},()=>res());next()}
  else res()})}

/* ---------- drawing ---------- */
function render(){
  const bar=$('bar'),area=$('area');bar.innerHTML='';area.innerHTML='';area.className='area';
  const B=(t,fn,o={})=>h('button',{class:'b'+(o.danger?' danger':'')+(o.go?' go':''),type:'button',onclick:fn,disabled:o.off},t);
  if(!cur){
    bar.append(h('span',{class:'crumb'},'Gallery'),B('New folder',newFolder),B('Import folder',()=>$('dir').click()),h('label',{class:'lbl',title:'On: sub-folders of the folder you import are recreated. Off: every picture goes into one folder.'},h('input',{type:'checkbox',checked:keepSub,onchange:e=>{keepSub=e.target.checked;try{localStorage.setItem('dorito-keepsub',keepSub?'1':'0')}catch(x){}}}),'keep sub-folders'),convLabel(),B('Replace originals...',convertDlg,{go:1}),B('Sync with disk',()=>act('sync',{})));
    $('st').textContent=data.length+' folder(s). Click a folder to open it.';
    if(!data.length)area.append(h('p',{class:'mempty'},'No folders yet. Press "New folder".'));
    const g=h('div',{class:'grid'});
    data.forEach(f=>g.append(h('button',{class:'tile fd',type:'button',onclick:()=>{cur=f.folder;clrSel();render()}},h('div',{class:'im'},h('img',{src:'/media/Dorito_folder_icon.png',alt:''})),h('div',{class:'cap'},f.name+' ('+total(f)+')'))));
    area.append(g);return}
  const f=folder();if(f.pixelated)area.classList.add('px');
  let rebar=()=>{};
  const buildBar=()=>{bar.innerHTML='';const n=deep?under(cur).length:sel.size,none=!n;
  bar.append(B('Back',()=>{cur=parentOf(cur)||null;clrSel();render()}),h('span',{class:'crumb'},'Gallery / '+trailOf(cur)),B('New folder',newFolder),
    B('Add pictures',()=>$('file').click()),B('Import folder',()=>$('dir').click()),h('label',{class:'lbl',title:'On: sub-folders of the folder you import are recreated. Off: every picture goes into one folder.'},h('input',{type:'checkbox',checked:keepSub,onchange:e=>{keepSub=e.target.checked;try{localStorage.setItem('dorito-keepsub',keepSub?'1':'0')}catch(x){}}}),'keep sub-folders'),
    h('label',{class:'lbl',title:'Names new pictures image_00, image_01, ...'},h('input',{type:'checkbox',checked:auto,onchange:e=>{auto=e.target.checked}}),'auto-name image_00...'),
    B('Sizes'+(n?' ('+n+')':''),sizesDialog,{off:!total(f),go:1}),B('Replace originals...'+(n?' ('+n+')':''),convertDlg,{off:!total(f),go:1}),convLabel(),
    h('label',{class:'lbl',title:'Make the resized copies (see Sizes) automatically for every picture you add or import'},h('input',{type:'checkbox',checked:autoSizes,onchange:e=>{autoSizes=e.target.checked;try{localStorage.setItem('dorito-autosizes',autoSizes?'1':'0')}catch(x){}}}),'auto-make sizes'),
    h('span',{class:'sep'}),
    B('Rename'+(n?' ('+n+')':''),renamePics,{off:none||deep}),B('Move',movePics,{off:none||deep}),B('Delete',deletePics,{off:none,danger:1}),
    B(!deep&&n===f.images.length&&n?'Select none':'Select all',()=>{const all=!deep&&sel.size===f.images.length&&sel.size;deep=false;sel=all?new Set():new Set(f.images.map(x=>x.file));render()},{off:!f.images.length}),B(deep?'Select none (all levels)':'Select all + sub-folders ('+under(cur).length+')',()=>{deep=!deep;sel=deep?new Set(f.images.map(x=>x.file)):new Set();render()},{off:!total(f)}),
    h('span',{class:'sep'}),B(showFiles?'File names: ON':'File names: off',()=>{showFiles=!showFiles;try{localStorage.setItem('dorito-showfiles',showFiles?'1':'0')}catch(e){}render()}),B('Sort',sortPics,{off:f.images.length<2}),B('Rename files'+(n?' ('+n+')':''),renameFiles,{off:!f.images.length||deep}),B('Rename folder',renameFolder),B(f.pixelated?'Pixel art: ON':'Pixel art: off',pixelToggle),B('Delete folder',deleteFolder,{danger:1}));
  $('st').textContent=f.images.length+' picture(s)'+(kids(f).length?', '+kids(f).length+' folder(s)':'')+(n?', '+n+' selected':'')+'. Click to select. Drag to re-order.';};
  rebar=buildBar;buildBar();
  const gr=h('div',{class:'grid'});let dragging=null;
  kids(f).forEach(c=>gr.append(h('button',{class:'tile fd',type:'button',onclick:()=>{cur=c.folder;clrSel();render()}},h('div',{class:'im'},h('img',{src:'/media/Dorito_folder_icon.png',alt:''})),h('div',{class:'cap'},c.name+' ('+total(c)+')'))));
  if(!f.images.length&&!kids(f).length){area.append(h('p',{class:'mempty'},'Empty :(  Press "Add pictures" or "Import folder", or drag pictures here.'));return}
  if(window._io)window._io.disconnect();
  const io=window._io=new IntersectionObserver(es=>es.forEach(en=>{const im=en.target.querySelector('img');if(!im||!im._rel)return;im._vis=en.isIntersecting;
    if(en.isIntersecting&&!im.dataset.req){im.dataset.req=1;im.src='/thumb?p='+encodeURIComponent(im._rel)}}),{root:area,rootMargin:'150px'});
  f.images.forEach(it=>{
    const t=h('button',{class:'tile'+(sel.has(it.file)?' sel':''),type:'button',draggable:'true',title:it.title+'  ['+it.file+']'},
      h('div',{class:'im'},(it.sizes&&it.sizes.length)?h('span',{class:'bd',title:'Resized copies already made: '+it.sizes.join(', ')+' px'},'\u29c9 '+it.sizes.length):'',(()=>{const rel=f.folder+it.file,im=h('img',{alt:it.title,decoding:'async'});im._rel=rel;im.onerror=()=>thumbFor(im,rel);return im})()),h('div',{class:'cap'},it.title),(it.sizes&&it.sizes.length)?h('div',{class:'cp',title:'Resized copies already made'},'\u29c9 '+it.sizes.join(' \u00b7 ')):'',showFiles?h('div',{class:'fn'},it.file):'');
    t.addEventListener('click',()=>{deep=false;sel.has(it.file)?sel.delete(it.file):sel.add(it.file);t.classList.toggle('sel',sel.has(it.file));rebar()});
    t.addEventListener('dblclick',()=>{deep=false;sel=new Set([it.file]);renamePics()});
    t.addEventListener('dragstart',e=>{dragging=it.file;t.classList.add('drag');e.dataTransfer.setData('text/x-dorito',it.file);e.dataTransfer.effectAllowed='move'});
    t.addEventListener('dragend',()=>t.classList.remove('drag'));
    t.addEventListener('dragover',e=>{if(dragging&&dragging!==it.file){e.preventDefault();t.classList.add('over')}});
    t.addEventListener('dragleave',()=>t.classList.remove('over'));
    t.addEventListener('drop',async e=>{if(!dragging)return;e.preventDefault();e.stopPropagation();t.classList.remove('over');
      const order=f.images.map(x=>x.file).filter(x=>x!==dragging);order.splice(order.indexOf(it.file),0,dragging);dragging=null;await act('pic/reorder',{folder:cur,order})});
    gr.append(t);io.observe(t.querySelector('.im'))});
  area.append(gr)}

/* drag pictures from the computer onto the window */
const mgr=$('mgr');let dc=0;
const hasFiles=e=>[...(e.dataTransfer?.types||[])].includes('Files');
mgr.addEventListener('dragenter',e=>{if(hasFiles(e)){dc++;$('drop').innerHTML=cur?'Drop pictures or a whole folder here<br>to add them to this folder':'Drop a folder here to import it<br>as a new gallery folder';mgr.classList.add('dragging')}});
mgr.addEventListener('dragleave',e=>{if(hasFiles(e)){dc=Math.max(0,dc-1);if(!dc)mgr.classList.remove('dragging')}});
mgr.addEventListener('dragover',e=>{if(hasFiles(e))e.preventDefault()});
mgr.addEventListener('drop',async e=>{if(!hasFiles(e))return;e.preventDefault();dc=0;mgr.classList.remove('dragging');
  const ents=[...(e.dataTransfer.items||[])].map(i=>i.webkitGetAsEntry&&i.webkitGetAsEntry()).filter(Boolean),plain=[...e.dataTransfer.files];
  if(ents.some(x=>x.isDirectory)){const out=[];await Promise.all(ents.map(x=>walkEntry(x,out,[])));await importItems(out)}
  else if(cur)upload(plain);else importItems(plain.map(file=>({file,dirs:[]})))});
$('dir').addEventListener('change',e=>{const fl=[...e.target.files].map(file=>({file,dirs:(file.webkitRelativePath||'').split('/').slice(0,-1)}));e.target.value='';importItems(fl)});
$('file').addEventListener('change',e=>{upload(e.target.files);e.target.value=''});
for(const[id,key,def]of[['atonce','dorito-atonce','2'],['delay','dorito-delay','0']]){let v=def;try{v=localStorage.getItem(key)||def}catch(e){}$(id).value=v;
  $(id).addEventListener('change',()=>{try{localStorage.setItem(key,$(id).value)}catch(e){}pump()})}
$('contog').onclick=e=>{e.preventDefault();setCon(!conOn)};
let anim=false;try{anim=localStorage.getItem('dorito-anim')==='1'}catch(e){}
const setAnim=on=>{anim=on;document.body.classList.toggle('anim',on);$('bgtog').textContent='Background: '+(on?'animated':'still');try{localStorage.setItem('dorito-anim',on?'1':'0')}catch(e){}};
$('bgtog').onclick=e=>{e.preventDefault();setAnim(!anim)};setAnim(anim);$('conhide').onclick=()=>setCon(false);$('conclear').onclick=()=>{$('cl').innerHTML=''};
setCon(conOn);setInterval(()=>{if(conOn&&!document.hidden)pollLog()},1000);
fetch('/api/state').then(r=>r.json()).then(d=>{data=d;render();updSize()}).catch(()=>toast('Could not load. Is the black window still open?',1));
</script></body></html>'''


def main():
    g.load()  # fail early with a clear message if script.js is missing / has no markers
    data = g.load()  # pick up folders / pictures that are on disk but not in the list yet
    res = a_sync(data, {})
    if res['message'] != 'Everything already matches.':
        g.save(data)
        print('Found things that were not in the gallery list yet, added them:')
        for m in res['message'].split('; '):
            print('  -', m)
            log('Found on disk: ' + m, quiet=True)
    write_size_txt(inventory(g.load())['total'])
    log(f'Manager started. {sum(1 for _ in walk(g.load()))} folder(s) in the gallery list.')
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
