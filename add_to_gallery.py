#!/usr/bin/env python3
"""
add_to_gallery.py  -  the Dorito gallery manager.

Add pictures, rename the text shown in the gallery, move pictures between folders,
remove pictures or whole folders, and more, without editing script.js by hand.

SET UP
  Put this file next to script.js (top of your repo folder). You need Python installed.

RUN IT
  python add_to_gallery.py            (Mac/Linux: python3 add_to_gallery.py)
  A menu appears. Type a number and press Enter. Press Enter on an empty line to go back.

  Shortcuts:
    python add_to_gallery.py "C:\\path\\to\\pictures"   go straight to "add pictures" for that folder
    python add_to_gallery.py --list                    just show everything

WHEN YOU ARE DONE
  Open GitHub Desktop, commit and push. Changes only go live after that.
  (Every change here is also easy to undo in GitHub Desktop before you commit:
   right click the changed file > Discard changes.)

WHAT IT MANAGES
  Folders it created or that are in the AUTO-GALLERY part of script.js (see "List").
  The hand-written "Dorito things" folder in script.js is not touched by this tool.
  Only text between the AUTO-GALLERY-START / AUTO-GALLERY-END markers in script.js is changed.

NAMES
  Every picture has two names: the FILE name (media/gallery/<folder>/photo.png)
  and the NAME SHOWN in the gallery (the "title"). Renaming here changes only the shown name.
  When adding, the shown name is suggested from the file name. A titles.txt inside the
  picture folder can pre-name pictures, one per line:   beach.jpg = Beach day
"""
import json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, 'script.js')
GAL_DIR = 'media/gallery'
START, END = '/*AUTO-GALLERY-START*/', '/*AUTO-GALLERY-END*/'
EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg', '.avif'}


# ---------- reading / writing script.js ----------
def load():
    if not os.path.exists(SCRIPT):
        sys.exit('Could not find script.js next to this file. Put add_to_gallery.py in the same folder as script.js.')
    src = open(SCRIPT, encoding='utf-8').read()
    if src.count(START) != 1 or src.count(END) != 1:
        sys.exit('The AUTO-GALLERY markers are missing from script.js. Use the script.js that came with this tool.')
    i, j = src.index(START) + len(START), src.index(END)
    data = json.loads(src[i:j])
    for f in data:  # make every picture a {file,title} entry
        f['images'] = [{'file': x, 'title': nice_title(x)} if isinstance(x, str) else x for x in f['images']]
    return data


def save(data):
    src = open(SCRIPT, encoding='utf-8').read()
    i, j = src.index(START) + len(START), src.index(END)
    open(SCRIPT, 'w', encoding='utf-8', newline='').write(src[:i] + json.dumps(data, ensure_ascii=False) + src[j:])


# ---------- small helpers ----------
def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-') or 'folder'


def safe_file(name):
    base, ext = os.path.splitext(name)
    return (re.sub(r'[^A-Za-z0-9._-]+', '-', base).strip('-') or 'image') + ext.lower()


def nice_title(name):
    base = re.sub(r'[_-]+', ' ', os.path.splitext(name)[0]).strip()
    return base[:1].upper() + base[1:] if base else name


def natural(s):
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r'(\d+)', s)]


def ask(prompt, default=''):
    try:
        v = input(prompt).strip()
    except EOFError:
        v = ''
    return v or default


def yes(prompt):
    return ask(prompt + ' (y/N): ', 'n').lower().startswith('y')


def clean_path(p):
    return p.strip().strip('"').strip("'")


def fdir(fold):
    return os.path.join(HERE, *fold['folder'].strip('/').split('/'))


def unique(name, taken):
    base, ext = os.path.splitext(name)
    k, out = 2, name
    while out.lower() in taken:
        out = f'{base}-{k}{ext}'
        k += 1
    return out


def next_number(fold):
    n = 0
    names = [x['file'] for x in fold['images']]
    if os.path.isdir(fdir(fold)):
        names += os.listdir(fdir(fold))
    for fn in names:
        m = re.match(r'image_(\d+)\.', fn, re.I)
        if m:
            n = max(n, int(m.group(1)) + 1)
    return n


def pick_folder(data, prompt='Which folder?', allow_new=False):
    if not data and not allow_new:
        print('There are no folders yet. Make one first.')
        return None
    for n, f in enumerate(data, 1):
        print(f'  {n}. {f["name"]}  ({len(f["images"])} pictures)')
    if allow_new:
        print('  N. NEW folder')
    a = ask(f'{prompt} (number{", or N for new" if allow_new else ""}, Enter to cancel): ').upper()
    if allow_new and a == 'N':
        return new_folder(data)
    if a.isdigit() and 1 <= int(a) <= len(data):
        return data[int(a) - 1]
    print('Cancelled.')
    return None


def pick_pictures(fold, prompt='Which pictures?'):
    """Returns a list of image entries chosen by numbers like  1,3,5-7  or  all."""
    if not fold['images']:
        print('That folder has no pictures.')
        return []
    for n, it in enumerate(fold['images'], 1):
        print(f'  {n}. {it["title"]}    [{it["file"]}]')
    a = ask(f'{prompt} (e.g. 1,3,5-7 or all, Enter to cancel): ').lower()
    if not a:
        return []
    if a == 'all':
        return list(fold['images'])
    idx = set()
    for part in a.replace(' ', '').split(','):
        m = re.fullmatch(r'(\d+)-(\d+)', part)
        if m:
            idx.update(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.isdigit():
            idx.add(int(part))
        else:
            print(f'Did not understand "{part}". Cancelled.')
            return []
    bad = [i for i in idx if not 1 <= i <= len(fold['images'])]
    if bad:
        print(f'No picture number {bad[0]}. Cancelled.')
        return []
    return [fold['images'][i - 1] for i in sorted(idx)]


def new_folder(data, name=None):
    name = name or ask('Name for the new folder (the text shown in the gallery): ')
    if not name:
        print('Cancelled (a folder needs a name).')
        return None
    if any(f['name'].lower() == name.lower() for f in data):
        print('A folder with that name already exists.')
        return None
    taken = {f['folder'] for f in data}
    path, k = f'{GAL_DIR}/{slug(name)}/', 2
    while path in taken:
        path = f'{GAL_DIR}/{slug(name)}-{k}/'
        k += 1
    fold = {'name': name, 'folder': path, 'images': []}
    if yes('Is it pixel art (keeps pictures crisp when enlarged)?'):
        fold['pixelated'] = True
    data.append(fold)
    os.makedirs(fdir(fold), exist_ok=True)
    return fold


def read_titles(folder):
    out, p = {}, os.path.join(folder, 'titles.txt')
    if os.path.exists(p):
        for line in open(p, encoding='utf-8-sig'):
            if '=' in line:
                k, v = line.split('=', 1)
                out[k.strip().lower()] = v.strip()
    return out


# ---------- the actions ----------
def do_list(data):
    if not data:
        print('Nothing managed by this tool yet.')
    for f in data:
        px = '  [pixel art]' if f.get('pixelated') else ''
        print(f"\n{f['name']}   ({f['folder']}){px}   {len(f['images'])} picture(s)")
        for it in f['images']:
            print(f"   {it['title']}    [{it['file']}]")


def do_add(data, pic_dir=None):
    pic_dir = clean_path(pic_dir or ask('Folder with the pictures to add (you can drag the folder into this window): '))
    if not pic_dir:
        return
    if not os.path.isdir(pic_dir):
        print(f'"{pic_dir}" is not a folder.')
        return
    files = sorted((f for f in os.listdir(pic_dir) if os.path.splitext(f)[1].lower() in EXTS), key=natural)
    if not files:
        print('No pictures found there (png, jpg, gif, webp, bmp, svg, avif).')
        return
    print(f'Found {len(files)} picture(s).\n')
    fold = pick_folder(data, 'Add to which folder?', allow_new=True)
    if not fold:
        return
    number = yes('Name them automatically image_00, image_01, image_02...?')
    counter = next_number(fold) if number else 0
    titles = read_titles(pic_dir)
    dest = fdir(fold)
    os.makedirs(dest, exist_ok=True)
    taken = {x['file'].lower() for x in fold['images']} | {x.lower() for x in os.listdir(dest)}
    if not number:
        print('\nType the name to show in the gallery for each picture, or press Enter to use the suggestion.\n')
    for f in files:
        target = safe_file(f)
        if number:
            target = f'image_{counter:02d}' + os.path.splitext(target)[1]
            counter += 1
        target = unique(target, taken)
        suggestion = titles.get(f.lower()) or (os.path.splitext(target)[0] if number else nice_title(f))
        title = suggestion if (number or f.lower() in titles) else ask(f'  {f}  [{suggestion}]: ', suggestion)
        shutil.copy2(os.path.join(pic_dir, f), os.path.join(dest, target))
        taken.add(target.lower())
        fold['images'].append({'file': target, 'title': title})
    save(data)
    print(f'\nAdded {len(files)} picture(s) to "{fold["name"]}".')


def do_rename_pic(data):
    fold = pick_folder(data, 'Rename pictures in which folder?')
    if not fold:
        return
    for it in pick_pictures(fold, 'Which pictures do you want to rename?'):
        t = ask(f'  New name for "{it["title"]}" (Enter = keep): ')
        if t:
            it['title'] = t
    save(data)
    print('Saved.')


def do_move(data):
    if len(data) < 2:
        print('You need at least two folders to move pictures between.')
        return
    print('Move FROM:')
    src = pick_folder(data, 'From which folder?')
    if not src:
        return
    pics = pick_pictures(src, 'Which pictures to move?')
    if not pics:
        return
    print('Move TO:')
    dst = pick_folder([f for f in data if f is not src], 'To which folder?')
    if not dst:
        return
    os.makedirs(fdir(dst), exist_ok=True)
    taken = {x['file'].lower() for x in dst['images']} | {x.lower() for x in os.listdir(fdir(dst))}
    for it in pics:
        new = unique(it['file'], taken)
        taken.add(new.lower())
        a, b = os.path.join(fdir(src), it['file']), os.path.join(fdir(dst), new)
        if os.path.exists(a):
            shutil.move(a, b)
        else:
            print(f'  (note: {it["file"]} was not on disk in the old folder, only the gallery entry moved)')
        src['images'].remove(it)
        dst['images'].append({'file': new, 'title': it['title']})
    save(data)
    print(f'Moved {len(pics)} picture(s) to "{dst["name"]}".')


def do_remove_pics(data):
    fold = pick_folder(data, 'Remove pictures from which folder?')
    if not fold:
        return
    pics = pick_pictures(fold, 'Which pictures to REMOVE?')
    if not pics:
        return
    print('\nThis will remove:')
    for it in pics:
        print(f'   {it["title"]}  [{it["file"]}]')
    if not yes('Delete these pictures (the files are deleted from your repo folder too)?'):
        print('Cancelled.')
        return
    for it in pics:
        p = os.path.join(fdir(fold), it['file'])
        if os.path.exists(p):
            os.remove(p)
        fold['images'].remove(it)
    save(data)
    print(f'Removed {len(pics)} picture(s).')


def do_new_folder(data):
    f = new_folder(data)
    if f:
        save(data)
        print(f'Created "{f["name"]}".')


def do_rename_folder(data):
    fold = pick_folder(data, 'Rename which folder?')
    if not fold:
        return
    n = ask(f'New name for "{fold["name"]}" (this is the text shown in the gallery): ')
    if not n:
        print('Cancelled.')
        return
    if any(f is not fold and f['name'].lower() == n.lower() for f in data):
        print('A folder with that name already exists.')
        return
    fold['name'] = n
    save(data)
    print('Saved. (The folder on disk keeps its old name; that is fine, visitors never see it.)')


def do_remove_folder(data):
    fold = pick_folder(data, 'REMOVE which folder?')
    if not fold:
        return
    print(f'\n"{fold["name"]}" has {len(fold["images"])} picture(s).')
    if not yes(f'Remove the folder "{fold["name"]}" from the gallery?'):
        print('Cancelled.')
        return
    d = fdir(fold)
    inside = os.path.abspath(d).startswith(os.path.abspath(os.path.join(HERE, *GAL_DIR.split('/'))) + os.sep)
    if os.path.isdir(d) and inside and yes('Also DELETE the picture files from your repo folder? (No = keep the files, just hide the folder)'):
        shutil.rmtree(d)
        print('Files deleted.')
    data.remove(fold)
    save(data)
    print('Folder removed.')


def do_pixel(data):
    fold = pick_folder(data, 'Change pixel-art mode for which folder?')
    if not fold:
        return
    now = bool(fold.get('pixelated'))
    print(f'Pixel art is currently {"ON" if now else "OFF"} for "{fold["name"]}".')
    if yes('Switch it?'):
        if now:
            fold.pop('pixelated', None)
        else:
            fold['pixelated'] = True
        save(data)
        print('Saved.')


def do_reorder(data):
    fold = pick_folder(data, 'Re-order which folder?')
    if not fold or not fold['images']:
        return
    print('  1. Sort by shown name (A to Z)\n  2. Sort by file name (A to Z, numbers in order)\n  3. Move one picture to a new position\n  4. Reverse the order')
    c = ask('Choose (Enter to cancel): ')
    if c == '1':
        fold['images'].sort(key=lambda x: natural(x['title']))
    elif c == '2':
        fold['images'].sort(key=lambda x: natural(x['file']))
    elif c == '4':
        fold['images'].reverse()
    elif c == '3':
        pics = pick_pictures(fold, 'Which ONE picture?')
        if len(pics) != 1:
            print('Pick exactly one. Cancelled.')
            return
        pos = ask(f'New position (1 to {len(fold["images"])}): ')
        if not pos.isdigit() or not 1 <= int(pos) <= len(fold['images']):
            print('Cancelled.')
            return
        fold['images'].remove(pics[0])
        fold['images'].insert(int(pos) - 1, pics[0])
    else:
        return
    save(data)
    print('Saved.')


def do_sync(data):
    """Pick up pictures that are in a gallery folder on disk but not in the list (e.g. dropped in by hand),
    and drop list entries whose file no longer exists."""
    changed = 0
    for fold in data:
        d = fdir(fold)
        if not os.path.isdir(d):
            continue
        listed = {x['file'].lower() for x in fold['images']}
        for fn in sorted(os.listdir(d), key=natural):
            if os.path.splitext(fn)[1].lower() in EXTS and fn.lower() not in listed:
                fold['images'].append({'file': fn, 'title': nice_title(fn)})
                print(f'  + {fold["name"]}: found {fn}')
                changed += 1
        gone = [x for x in fold['images'] if not os.path.exists(os.path.join(d, x['file']))]
        for x in gone:
            fold['images'].remove(x)
            print(f'  - {fold["name"]}: {x["file"]} is missing on disk, removed from the list')
            changed += 1
    if changed:
        save(data)
    print('Everything already matches.' if not changed else f'Fixed {changed} thing(s).')


MENU = [
    ('List everything', do_list),
    ('Add pictures', do_add),
    ('Rename the text shown for a picture', do_rename_pic),
    ('Move pictures to another folder', do_move),
    ('Remove pictures', do_remove_pics),
    ('Make a new empty folder', do_new_folder),
    ('Rename a folder (text shown in the gallery)', do_rename_folder),
    ('Remove a folder', do_remove_folder),
    ('Re-order pictures in a folder', do_reorder),
    ('Pixel-art mode on/off for a folder', do_pixel),
    ('Sync (pick up files you dropped into a folder by hand)', do_sync),
]


def main():
    args = sys.argv[1:]
    data = load()
    if '--list' in args:
        return do_list(data)
    args = [a for a in args if not a.startswith('--')]
    if args:
        do_add(data, args[0])
        print('\nNow open GitHub Desktop, commit and push to publish.')
        return
    while True:
        print('\n=== Dorito gallery manager ===')
        for n, (label, _) in enumerate(MENU, 1):
            print(f'  {n}. {label}')
        print('  0. Quit')
        c = ask('\nChoose: ', '0')
        if c == '0':
            break
        if c.isdigit() and 1 <= int(c) <= len(MENU):
            print()
            MENU[int(c) - 1][1](data)
        else:
            print('Type one of the numbers above.')
    print('\nDone. If you changed anything: open GitHub Desktop, commit and push to publish.')


if __name__ == '__main__':
    main()
