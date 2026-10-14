"""Build index.html from the extracted Nightreign game data.

Inputs (produced by the extraction scripts in the scratchpad):
  data2.json  - loot tables / custom weapons / skill tables / names
  fmg.json    - in-game text (engus / jpnjp / zhotw)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
work = Path(sys.argv[1])
data = json.load(open(work / 'data2.json', encoding='utf-8'))
F = json.load(open(work / 'msg' / 'fmg.json', encoding='utf-8'))

CLASS_EN = {1: 'Wylder', 2: 'Guardian', 3: 'Ironeye', 4: 'Duchess', 5: 'Raider',
            6: 'Revenant', 7: 'Recluse', 8: 'Executor', 9: 'Scholar', 10: 'Undertaker'}
classes = {}
for cid, en in CLASS_EN.items():
    found = None
    for n in ('NpcName.fmg', 'NpcName_dlc01.fmg'):
        for k, v in F['engus'][n].items():
            if v == en and 100000 <= int(k) < 120000:
                found = {'en': en, 'ja': F['jpnjp'][n].get(k), 'zh': F['zhotw'][n].get(k)}
                break
        if found:
            break
    classes[cid] = found or {'en': en, 'ja': en, 'zh': en}
data['classes'] = classes

tpl = (HERE / 'template.html').read_text(encoding='utf-8')
blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
HEAD = ('<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n')
body = tpl.replace('/*__DATA__*/', blob)
# the template starts with <title>/<link>/<style>; everything from the first <div> on is page body
split = body.index('<div class="wrap">')
out = HEAD + body[:split] + '</head>\n<body>\n' + body[split:] + '\n</body>\n</html>\n'
(HERE.parent / 'index.html').write_text(out, encoding='utf-8')
print('classes', {k: v['en'] for k, v in classes.items()}, all(v['zh'] for v in classes.values()))
print('wrote', len(out), 'bytes')
