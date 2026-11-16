"""Static teaching atlas: coordinate-linked maps, illustrated routes and source notes."""
import json
from html import escape as E
from urllib.parse import urlencode


def map_svg(route, geo):
    west, south, east, north = route['bounds']
    width, height = 720, 400
    # Region-local equirectangular projection. Modern geography, approximate points.
    def xy(lon, lat):
        return (lon-west)/(east-west)*width, (north-lat)/(north-south)*height

    land = []
    for feature in geo['features']:
        shape = feature['geometry']
        for polygon in shape['coordinates'] if shape['type']=='MultiPolygon' else [shape['coordinates']]:
            ring = polygon[0]
            xs, ys = zip(*[(v[0],v[1]) for v in ring])
            if min(xs)>east or max(xs)<west or min(ys)>north or max(ys)<south:
                continue
            land.append('<path d="M'+'L'.join(f'{x:.1f},{y:.1f}' for x,y in (xy(*pt[:2]) for pt in ring))+'Z"/>')
    coords = [xy(p[2],p[1]) for p in route['places']]
    pins = []
    for i, ((x,y),p) in enumerate(zip(coords,route['places']),1):
        # The two Bosporus sites are geographically close at regional scale.
        dy = -19 if route['id']=='creeds' and i==3 else 19 if route['id']=='creeds' and i==4 else 0
        pins.append(f'<g class="atlas-pin" data-atlas-pin="{i}" tabindex="0" role="button" aria-label="{E(p[0])}" aria-pressed="{str(i==1).lower()}"><line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y+dy:.1f}"/><circle cx="{x:.1f}" cy="{y+dy:.1f}" r="13"/><text x="{x:.1f}" y="{y+dy:.1f}" dy=".34em">{i}</text><title>{E(p[0])}</title></g>')
    rid=route['id']
    grid=''.join(f'M{x},0V400' for x in range(60,720,60))+''.join(f'M0,{y}H720' for y in range(50,400,50))
    route_line=' '.join(f'{x:.1f},{y:.1f}' for x,y in coords)
    line='' if rid=='creeds' else f'<polyline class="atlas-route-line" points="{route_line}"/>'
    return f'''<svg class="atlas-map" viewBox="0 0 720 400" role="group" aria-label="{E(route['title'])}：地图编号与地点卡对应">
      <defs><clipPath id="clip-{rid}"><rect width="720" height="400" rx="16"/></clipPath></defs>
      <g clip-path="url(#clip-{rid})"><rect class="atlas-water" width="720" height="400"/><g class="atlas-land">{''.join(land)}</g><path class="atlas-grid" d="{grid}"/>{line}{''.join(pins)}</g>
      <g class="atlas-north" transform="translate(677 37)"><path d="M0 -8L-7 11L0 7L7 11Z"/><text y="-14">北</text></g>
    </svg>'''


def maps_links(lat,lon):
    return [
        ('OpenStreetMap','https://www.openstreetmap.org/?'+urlencode({'mlat':lat,'mlon':lon})+f'#map=12/{lat}/{lon}'),
        ('Google Maps','https://www.google.com/maps/search/?'+urlencode({'api':1,'query':f'{lat},{lon}'})),
        ('Bing Maps','https://www.bing.com/maps/default.aspx?'+urlencode({'cp':f'{lat}~{lon}','lvl':12,'style':'a'})),
    ]


def atlas_html(root,icon):
    routes=json.loads((root/'content/atlas.json').read_text(encoding='utf8'))
    geo=json.loads((root/'content/countries.json').read_text(encoding='utf8'))
    nav=''.join(f'<a href="#atlas-{r["id"]}">{icon(r["icon"])}<span>{E(r["title"])}</span></a>' for r in routes)
    sections=[]
    for n,r in enumerate(routes,1):
        cards=[]
        for i,(name,lat,lon,culture,ref,scene,meaning,day,source) in enumerate(r['places'],1):
            links=''.join(f'<a href="{E(url)}" target="_blank" rel="noopener noreferrer">{E(title)} ↗</a>' for title,url in maps_links(lat,lon))
            cards.append(f'''<details class="atlas-place" data-location="{i}" data-lat="{lat}" data-lon="{lon}"{' open' if i==1 else ''}>
              <summary><span class="atlas-number">{i}</span><span>{E(name)}<small>{E(culture)}</small></span></summary>
              <div class="atlas-place-content"><p class="atlas-reference">{E(ref)} · {lat:.3f}°N，{lon:.3f}°E</p>
              <p data-mark-key="atlas:{r['id']}:{i}:scene">{E(scene)}</p>
              <p class="atlas-meaning" data-mark-key="atlas:{r['id']}:{i}:meaning">{E(meaning)}</p>
              <p class="atlas-source"><a href="{E(source)}">核对来源 ↗</a> · <a href="day-{day:02}.html">回到主日{day}</a></p>
              <div class="atlas-links" aria-label="{E(name)}在线地图">{links}</div>
              <button type="button" class="atlas-live" data-map-open>{icon('map')} 在页内加载 OpenStreetMap</button></div>
            </details>''')
        flow=''.join(f'<li><span>{i:02}</span><b>{E(v)}</b></li>' for i,v in enumerate(r['flow'],1))
        sections.append(f'''<section class="reading-section atlas-section atlas-{r['id']}" id="atlas-{r['id']}">
        <div class="atlas-title"><span class="atlas-emblem">{icon(r['icon'])}</span><div><div class="eyebrow">路线 {n:02} · {E(r['era'])}</div><h2>{E(r['title'])}</h2></div></div>
        <div class="atlas-thesis"><strong>{E(r['question'])}</strong><p data-mark-key="atlas:{r['id']}:thesis">{E(r['answer'])}</p></div>
        <ol class="atlas-flow" aria-label="本段故事的三个步骤">{flow}</ol>
        <div class="atlas-workbench"><figure>{map_svg(r,geo)}<figcaption>教学底图 · <a href="https://www.naturalearthdata.com/about/terms-of-use/">Natural Earth 1:110m</a>。{E(r['boundary'])}</figcaption></figure>
        <div class="atlas-locations" aria-label="地点、文化与解读">{''.join(cards)}</div></div></section>''')
    transcript=''.join(f'<li><strong>{E(r["title"])}</strong>：{E(r["answer"])}</li>' for r in routes)
    return f'''<section class="atlas-hero" id="geography"><div class="eyebrow">GTSTUDY FIELD ATLAS · 历史与文化</div><h1>把信仰放回<br>真实的地点与时代</h1><p>四条线索，从福音发生的地方，到教会如何说清并传授所信。先读教学图，再按需查看现代街道与航拍。</p>
    <div class="atlas-stats"><span><b>4</b> 张区域图</span><span><b>{sum(len(r['places']) for r in routes)}</b> 个场景点</span><span><b>3</b> 在线地图服务</span><span>教学图不请求外部地图</span></div>
    <nav class="atlas-nav" aria-label="图册目录">{nav}<a href="history.html#history">{icon('clock')}总时间线</a><a href="#atlas-video">{icon('brain')}动画短片</a></nav></section>
    {''.join(sections)}
    <section class="reading-section atlas-media" id="atlas-video"><div class="eyebrow">MOTION ATLAS · 32 秒</div><h2>四个画面，记住两条历史线</h2>
    <p>短片把福音事件与教会认信放在不同轨道。路线关系图与下方文字可独立阅读。</p>
    <video controls playsinline preload="none" width="960" height="540" poster="atlas-poster.svg" aria-label="历史与文化图册导读，无声中文字幕">
      <source src="atlas-intro.mp4" type="video/mp4"><a href="atlas-intro.mp4">下载短片</a></video>
    <details><summary>阅读短片文字稿与四段结论</summary><ol>{transcript}</ol></details></section>
    <dialog id="atlas-map-dialog" class="modal atlas-dialog"><div class="modal-heading"><h2 id="atlas-online-title">在线地图</h2><button type="button" data-close-dialog aria-label="关闭在线地图">×</button></div>
    <p class="caption">现代地图，非古代复原。若下方显示空白，请切换地图源，或关闭后继续读教学图。</p>
    <div id="atlas-live-frame"></div><p id="atlas-map-status" role="status"></p><div class="atlas-links" id="atlas-live-links"></div></dialog>'''
