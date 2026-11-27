"""Rebuilds the lists the website reads from the one-file-per-item folders, and refreshes the
Area / Organiser / Planner / Controller dropdown choices in .pages.yml. Run by the GitHub Action
in .github/workflows/build-areas.yml whenever something in data/areas, data/members, data/clubs or data/events changes."""
import glob, json, os, re

def load(folder):
    items = []
    for f in sorted(glob.glob('data/%s/*.json' % folder)):
        a = json.load(open(f, encoding='utf-8'))
        a['id'] = os.path.basename(f)[:-5]
        items.append(a)
    return items

lists = {}
for folder in ('areas', 'members', 'events', 'levels', 'series', 'permanent', 'clubs', 'towns', 'terrain', 'roles'):
    lists[folder] = load(folder)
    if folder in ('levels', 'terrain'): continue  # only used for the form dropdown
    with open('data/%s.json' % folder, 'w', encoding='utf-8') as out:
        json.dump({folder: lists[folder]}, out, indent=2, ensure_ascii=False)
        out.write('\n')

# dropdown choices in the CMS form: between "# BEGIN x" and "# END x" markers
yml = open('.pages.yml', encoding='utf-8').read()
for name in ('areas', 'members', 'levels', 'series', 'clubs', 'towns', 'terrain', 'roles'):
    def key(i):
        try: o = float(i.get('order'))
        except (TypeError, ValueError): o = 1e9
        return (o, str(i.get('name', '')).lower())
    names = []
    for i in sorted(lists[name], key=key):
        n = str(i.get('name', '')).strip()
        if n and n not in names: names.append(n)
    def fill(m, names=names, name=name):
        ind = m.group(1)
        body = ''.join('%s- %s\n' % (ind, json.dumps(n, ensure_ascii=False)) for n in names)
        return '%s# BEGIN %s\n%s%s# END %s\n' % (ind, name, body, ind, name)
    yml = re.sub(r'( *)# BEGIN %s\n.*?\1# END %s\n' % (name, name), fill, yml, flags=re.S)
open('.pages.yml', 'w', encoding='utf-8').write(yml)
