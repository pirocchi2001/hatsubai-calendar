"""data.json のうち、バンダイ公式カレンダー由来の行(id=b-...)だけを最新に置き換える。
手動で調べた行(id=m-...)は残し、発売日が過ぎた行は削除する。"""
import json, datetime, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import bandai_rows, next_months

JST = datetime.timezone(datetime.timedelta(hours=9))
now = datetime.datetime.now(JST)
today = now.date().isoformat()
path = os.path.join(os.path.dirname(__file__), '..', 'data.json')
data = json.load(open(path, encoding='utf-8'))
fresh = bandai_rows(next_months(now.date()))
if len(fresh) < 50:
    sys.exit(f'バンダイ側の取得件数が少なすぎるため更新を中止します: {len(fresh)}')
keep = [r for r in data['rows'] if not r['id'].startswith('b-')]
rows = [r for r in keep + fresh if not r['date'] or r['date'] >= today]
data['rows'] = rows
data['updated'] = now.strftime('%Y-%m-%d %H:%M')
json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('bandai rows:', len(fresh), 'total:', len(rows))
