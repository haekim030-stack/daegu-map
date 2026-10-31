#!/usr/bin/env python3
"""대구 행정구역 경계(GeoJSON) -> 일러스트용 SVG 경로(daegu-shape.json).

사용법:
  curl -o skorea.json https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_municipalities_geo.json
  python3 tools/build_shape.py skorea.json daegu-shape.json

원본: southkorea-maps (KOSTAT 2013 행정구역). 2013년 자료라 2023년에 편입된 군위군은 없음.
"""
import json, math, sys

K = 2500.0          # 위도 1도 = K 단위. 지도 좌표(x, y)의 크기를 정함
TOL = 2.0           # 선 단순화 허용 오차(단위). 클수록 매끈하고 가벼움
NAMES = {           # 코드: (id, 한국어, 일본어)
    "22010": ("jung", "중구", "中区"), "22020": ("dong", "동구", "東区"),
    "22030": ("seo", "서구", "西区"), "22040": ("nam", "남구", "南区"),
    "22050": ("buk", "북구", "北区"), "22060": ("suseong", "수성구", "寿城区"),
    "22070": ("dalseo", "달서구", "達西区"), "22310": ("dalseong", "달성군", "達城郡"),
}

def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    norm = math.hypot(dx, dy)
    best, idx = -1.0, 0
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        d = math.hypot(x - x1, y - y1) if norm == 0 else abs(dy * x - dx * y + x2 * y1 - y2 * x1) / norm
        if d > best:
            best, idx = d, i
    if best <= eps:
        return [pts[0], pts[-1]]
    return rdp(pts[:idx + 1], eps)[:-1] + rdp(pts[idx:], eps)

def area_centroid(ring):
    a = cx = cy = 0.0
    for i in range(len(ring) - 1):
        x0, y0 = ring[i]; x1, y1 = ring[i + 1]
        c = x0 * y1 - x1 * y0
        a += c; cx += (x0 + x1) * c; cy += (y0 + y1) * c
    if a == 0:
        return ring[0], 0
    return (cx / (3 * a), cy / (3 * a)), abs(a / 2)

def main(src, dst):
    feats = [f for f in json.load(open(src))["features"] if str(f["properties"]["code"]) in NAMES]
    lons = [p[0] for f in feats for poly in (f["geometry"]["coordinates"] if f["geometry"]["type"] == "MultiPolygon" else [f["geometry"]["coordinates"]]) for r in poly for p in r]
    lats = [p[1] for f in feats for poly in (f["geometry"]["coordinates"] if f["geometry"]["type"] == "MultiPolygon" else [f["geometry"]["coordinates"]]) for r in poly for p in r]
    lon0, lat0 = min(lons), max(lats)
    cosl = math.cos(math.radians((min(lats) + max(lats)) / 2))
    proj = lambda lon, lat: ((lon - lon0) * cosl * K, (lat0 - lat) * K)

    out, minx, miny, maxx, maxy = [], 1e9, 1e9, -1e9, -1e9
    for f in sorted(feats, key=lambda f: f["properties"]["code"]):
        i, ko, ja = NAMES[str(f["properties"]["code"])]
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        d, best = "", (None, -1)
        for poly in polys:
            ring = [proj(*p) for p in poly[0]]          # 바깥 테두리만 사용(구멍 무시)
            s = rdp(ring, TOL)
            if len(s) < 4:
                continue
            c, a = area_centroid(s)
            if a > best[1]:
                best = (c, a)
            for x, y in s:
                minx, miny, maxx, maxy = min(minx, x), min(miny, y), max(maxx, x), max(maxy, y)
            d += "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in s[:-1]) + "Z"
        out.append({"id": i, "name_ko": ko, "name_ja": ja, "d": d, "label": [round(best[0][0], 1), round(best[0][1], 1)]})

    json.dump({
        "source": "southkorea-maps (KOSTAT 2013). 군위군은 포함되어 있지 않음",
        "projection": {"lon0": round(lon0, 5), "lat0": round(lat0, 5), "cos": round(cosl, 5), "k": K},
        "bounds": [round(minx, 1), round(miny, 1), round(maxx, 1), round(maxy, 1)],
        "districts": out,
    }, open(dst, "w"), ensure_ascii=False, separators=(",", ":"))
    print("districts:", len(out), "bounds:", [round(v) for v in (minx, miny, maxx, maxy)])

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
