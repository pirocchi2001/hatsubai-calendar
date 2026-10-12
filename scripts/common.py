"""バンダイ公式カレンダーの取得・解析・分類（手動更新とGitHub Actionsで共用）"""
import re, html, hashlib, json, datetime, urllib.request

BASE = "https://www.bandai.co.jp/calendar/?select_year_month="
TYPE = {'baby': '玩具', 'cupsule': 'カプセルトイ', 'card': 'TCG/カード', 'candy': '食玩', 'life': '雑貨'}
MAKER = {'baby': 'バンダイ', 'cupsule': 'バンダイ ガシャポン', 'card': 'バンダイ カード事業部', 'candy': 'バンダイ キャンディ', 'life': 'バンダイ'}
BRANDS = [
    ('サンリオ', r'サンリオ|Sanrio|ハローキティ|HELLOKITTY|HELLO KITTY|クロミ|シナモロール|マイメロ|ポムポムプリン|ぐでたま|リトルツインスターズ|ポチャッコ|けろけろけろっぴ|コロコロクリリン|ウィッシュミーメル|マロンクリーム|ぼんぼんりぼん|タキシードサム|ハンギョドン|チャーミーキティ|キキ&ララ|ミルクキャップシアー|ボンボンドロップ|さんりおきゃらくたぁず|SANRIO CHARACTERS|サンリオキャラクターズ|シュガーバニーズ'),
    ('すとぷり', r'すとぷり|STPR'),
    ('いれいす', r'いれいす'),
    ('にじさんじ', r'にじさんじ|NIJISANJI'),
    ('ホロライブ', r'ホロライブ|hololive'),
    ('サンエックス', r'リラックマ|すみっコ|サンエックス|たれぱんだ'),
    ('たまごっち', r'たまごっち|Tamagotchi'),
    ('ガンダム', r'ガンダム|GUNDAM|ガンプラ|ガンダムクロス'),
    ('仮面ライダー', r'仮面ライダー|ライダーエグズ|エグズ|ガシャット|ガッチャード|ライダー(?!ズ?く?じ)|ネオディケイド|ゼクター|プログライズ'),
    ('ウルトラマン', r'ウルトラ|ゴジラ|ガタノゾーア'),
    ('スーパー戦隊', r'戦隊'),
    ('ポケモン', r'ポケモン|ポケットモンスター|Pokémon|Pokemon'),
    ('ワンピース', r'ONE PIECE|ワンピース'),
    ('ドラゴンボール', r'ドラゴンボール'),
    ('ちいかわ', r'ちいかわ'),
    ('アンパンマン', r'アンパンマン'),
    ('アイカツ', r'アイカツ'),
    ('プリキュア', r'プリキュア'),
    ('アイプリ', r'アイプリ'),
    ('ガンバレジェンズ', r'ガンバレジェンズ'),
    ('鬼滅の刃', r'鬼滅'),
    ('ディズニー', r'ディズニー|ピクサー|トイ・ストーリー|ズートピア|くまのプーさん|Winnie|リメンバー・ミー|モンスターズ・インク'),
    ('カービィ', r'カービィ|KIRBY'),
    ('すみっコぐらし', r'すみっコ'),
    ('ユニオンアリーナ', r'UNION ARENA'),
    ('シルバニア', r'シルバニア'),
    ('リカちゃん', r'リカちゃん'),
    ('トミカ', r'トミカ|tomica'),
    ('クレヨンしんちゃん', r'クレヨンしんちゃん'),
    ('名探偵コナン', r'コナン'),
    ('遊戯王', r'遊戯王|遊☆戯☆王|Yu-Gi-Oh'),
    ('デュエル・マスターズ', r'デュエル・マスターズ|デュエマ|DM\d\d-'),
    ('mofusand', r'mofusand'),
    ('ジュエルペット', r'ジュエルペット|ジュエルポッド'),
    ('おジャ魔女どれみ', r'おジャ魔女'),
    ('きらりん☆レボリューション', r'きらりん'),
    ('ミルモでポン', r'ミルモ'),
    ('めちゃモテ委員長', r'めちゃモテ'),
    ('ぺたもりしーる', r'ぺたもりしーる|たまもりしーる|たまもりアクセ'),
    ('ウィッシュキャット', r'ウィッシュキャット'),
    ('ナルミヤキャラクターズ', r'ナルミヤ|メゾピアノ'),
    ('Lil ala mode', r'Lil ala mode'),
    ('ほっぺちゃん', r'ほっぺちゃん'),
    ('ケアベア', r'ケアベア'),
    ('ミッフィー', r'miffy|ミッフィー'),
    ('パワーパフ ガールズ', r'パワーパフ'),
    ('カードキャプターさくら', r'カードキャプターさくら'),
    ('ムーミン', r'MOOMIN|ムーミン'),
    ('コジコジ', r'コジコジ|COJI-COJI'),
    ('お茶犬', r'お茶犬'),
    ('モンチッチ', r'モンチッチ'),
    ('魔法少女・魔法騎士', r'魔法少女|魔法騎士'),
    ('スヌーピー', r'SNOOPY|スヌーピー|PEANUTS'),
    ('どうぶつの森', r'どうぶつの森'),
    ('アイドルマスター', r'アイドルマスター|アイドリッシュセブン'),
    ('初音ミク', r'初音ミク'),
    ('エンジェルポケット', r'エンジェルポケット'),
    ('rom&nd', r'rom＆nd|rom&nd'),
    ('ねこあつめ', r'ねこあつめ'),
    ('ギャルネコ', r'ギャルネコ'),
    ('刀剣乱舞', r'刀剣乱舞'),
    ('K-POP', r'SKZOO|aespa|RIIZE|PLAVE|NCT WISH|KPOP|BT21'),
]

def brand_of(name):
    for b, pat in BRANDS:
        if re.search(pat, name):
            return b
    return ''

def limit_of(name):
    """商品名から販売チャネルの限定区分を判定（法人限定は赤バッジ表示）"""
    if '法人' in name: return '法人限定'
    m = re.search(r'【([^】]*限定[^】]*)】', name)
    if m: return m.group(1)
    m = re.search(r'(\S{1,8})限定', name)
    return m.group(0) if m else ''

def cat_of(t, name):
    c = TYPE.get(t, t)
    if t == 'baby':
        if re.search(r'たまごっち|Tamagotchi|フォン|ドリームレッスン|キッズ|タブレット', name): return '電子玩具'
        if re.search(r'ぷちとも|リカちゃん|シルバニア|ドール', name): return 'ドール'
        if re.search(r'仮面ライダー|DX|TAF|ウルトラ|戦隊|ムービーモンスター|SUPER BEST|変身ベルト|ライダー', name): return 'TV玩具'
        return '玩具'
    if t == 'card' and re.search(r'ポケモン|ワンピースカード|UNION|ガンダムカードゲーム|バトルスピリッツ|デジモン|ヴァイス', name): return 'TCG'
    return c

def make_id(prefix, date, name):
    return prefix + hashlib.md5(f'{date}|{name}'.encode()).hexdigest()[:10]

def fetch_month(ym):
    req = urllib.request.Request(BASE + ym, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=60).read().decode('utf-8')

def parse_month(ym, t):
    """ym='202611'。カレンダーに該当月のデータがない場合は空リスト。"""
    m = re.search(r'pg-pagerYear">\s*<span class="year">(\d+)</span>年<span class="month">(\d+)</span>', t)
    if not m or f'{m.group(1)}{int(m.group(2)):02d}' != ym:
        return []
    t = t[t.find('pg-calender__body'):]
    rows = []
    for blk in re.split(r'<div class="pg-daily">', t)[1:]:
        h = re.search(r'pg-daily__heading">(.*?)</div>', blk, re.S).group(1)
        txt = re.sub(r'\s+', '', re.sub(r'<[^>]+>', '', h))
        dm = re.match(r'(\d+)日', txt)
        date = f"{ym[:4]}-{ym[4:]}-{int(dm.group(1)):02d}" if dm else ''
        period = '' if dm else txt
        for c in re.finditer(r'data-category="(\w+)".*?<img src="[^"]*" alt="([^"]*)">.*?pg-card__name">.*?</div>\s*<div class="pg-card__detail">(.*?)</div>', blk, re.S):
            typ, name, price = c.groups()
            name = html.unescape(name.strip())
            price = html.unescape(re.sub(r'\s+', '', price)).replace('(税込)', '')
            rows.append(dict(
                id=make_id('b-', date or (ym + period), name),
                date=date, period=period if period in ('上旬', '中旬', '下旬', '未定') else ('未定' if not date else ''),
                ym=f'{ym[:4]}-{ym[4:]}', maker=MAKER.get(typ, 'バンダイ'), cat=cat_of(typ, name),
                brand=brand_of(name), limit=limit_of(name), name=name, price=price, conf='◎', note='', src=BASE + ym))
    return rows

def bandai_rows(months):
    out = []
    for ym in months:
        try:
            out += parse_month(ym, fetch_month(ym))
        except Exception as e:
            print('skip', ym, e)
    return out

def next_months(today, n=4):
    y, m = today.year, today.month
    res = []
    for _ in range(n):
        res.append(f'{y}{m:02d}')
        m += 1
        if m > 12: y, m = y + 1, 1
    return res
