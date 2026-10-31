# 대구 둘러보기 지도 / 大邱おでかけマップ

폰으로 대구 구역별 장소를 둘러보고 ♡로 찜한 뒤, 찜 목록을 복사해서 LINE·카톡으로 보내는 정적 웹페이지.

```
index.html     화면 + 동작 (수정할 일 거의 없음)
areas.json     구역 목록
places.json    장소 + 메뉴 목록
images/        사진 (사진은 여기에 넣고 json에 경로 적기)
```

## 로컬에서 열기

`index.html`을 더블클릭하면 브라우저가 json 파일 읽기를 막아서 안 열려요. 간단한 로컬 서버로 열어야 합니다.

```bash
cd daegu-map
python3 -m http.server 8000
```

브라우저에서 http://localhost:8000 접속. 폰 화면으로 보려면 크롬 개발자도구(F12) → 기기 툴바(Ctrl+Shift+M).

## 데이터 고치는 법 (코드 수정 없음)

### areas.json — 구역

| 필드 | 설명 |
|---|---|
| `id` | 영문 고유 id. places.json의 `area_id`와 연결됨 |
| `name_ja`, `name_ko` | 구역 이름 |
| `desc_ja`, `desc_ko` | 한 줄 소개 (바텀시트에 표시) |
| `lat`, `lng` | 원 중심 좌표 |
| `radius` | 원 반지름 (미터) |
| `color` | 원 색상 (`#rrggbb`, 비우면 자동) |

### places.json — 장소

| 필드 | 설명 |
|---|---|
| `id` | 영문 고유 id (찜 저장에 쓰여서, 한번 정하면 바꾸지 않는 게 좋음) |
| `area_id` | 소속 구역 id (좌표가 아니라 이 값으로 구역이 정해짐) |
| `category` | `restaurant` / `cafe` / `activity` 중 하나 |
| `name_ko`, `name_ja` | 이름. 한국어 원문은 항상 같이 표시됨 |
| `desc_*`, `hours_*` | 소개, 영업시간 (`\n`으로 줄바꿈 가능) |
| `lat`, `lng` | 좌표. 비우거나 `null`이면 지도에서 빠지고 목록에만 나옴 (콘솔 경고) |
| `photos` | 사진 경로 배열. 비우면 카테고리 아이콘 표시 |
| `menu` | `{ name_ko, name_ja, price, photo, desc_ko, desc_ja, signature }` 배열. `signature: true`면 "대표" 표시. 비우면 메뉴 섹션 숨김 |
| `address_ko` | (선택) 한국어 주소. 상세 화면에 표시되고, 좌표가 없을 때 구글맵 검색에도 쓰임 |
| `naver_url` | (선택) 네이버 공유 링크(`https://naver.me/...`). 있으면 [네이버지도] 버튼이 이 링크로 바로 열림 |
| `naver_query` | (선택) 네이버지도 검색어. 체인점처럼 이름만으로 헷갈릴 때 `"OO카페 동성로점"` 식으로 |

좌표는 네이버지도/구글맵에서 장소를 우클릭(길게 누르기)하면 나오는 위도·경도를 그대로 넣으면 됩니다.
json은 쉼표 하나만 틀려도 전체가 안 열리니, 고친 뒤 로컬에서 한번 열어 확인하세요.

`lat`·`lng`가 `null`인 항목은 좌표를 채워야 지도에 나옵니다.

## GitHub Pages로 배포

1. 이 브랜치를 `main`에 머지 (또는 Pages 설정에서 이 브랜치를 직접 선택)
2. GitHub 저장소 → **Settings** → 왼쪽 **Pages**
3. **Build and deployment** → Source: **Deploy from a branch**
4. Branch: `main`, 폴더: `/ (root)` → **Save**
5. 1~2분 뒤 같은 화면 위쪽에 `https://<아이디>.github.io/daegu-map/` 링크가 뜸 → 이 링크를 친구에게 공유

- 무료 계정은 저장소가 **Public**이어야 Pages를 쓸 수 있어요.
- json을 고쳐서 push하면 1~2분 뒤 자동 반영. 폰에서 안 바뀌어 보이면 새로고침.
- 찜 목록은 각자 폰 브라우저에만 저장됩니다(서버 저장 아님). 그래서 "찜 목록 복사"로 보내 달라고 하는 구조.
