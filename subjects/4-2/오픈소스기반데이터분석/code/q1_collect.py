# 문 1-2. 공공데이터포털 Open API로 2015~2024년 서울 가락도매시장 배추(봄/여름/가을/월동) 가격 수집
import json
import os
import time
from pathlib import Path

import requests

# 발급받은 키는 환경변수에 따로 넣어 둔다
SERVICE_KEY = os.environ.get("DATA_GO_KR_KEY")
if not SERVICE_KEY:
    raise SystemExit("환경변수 DATA_GO_KR_KEY에 인증키를 설정한 뒤 실행하세요.")

URL = "https://apis.data.go.kr/B552845/perDay/price"
YEARS = range(2015, 2025)
VARIETIES = {"01": "봄배추", "02": "여름배추(고랭지)", "03": "가을배추", "06": "월동배추"}
NUM_OF_ROWS = 200

# 조회 조건의 코드는 앞쪽 0이 없어지지 않게 문자로 적는다
BASE_COND = {
    "cond[se_cd::EQ]": "02",         # 중도매(도매)
    "cond[ctgry_cd::EQ]": "200",     # 채소류
    "cond[item_cd::EQ]": "211",      # 배추
    "cond[grd_cd::EQ]": "04",        # 상품
    "cond[sgg_cd::EQ]": "1101",      # 서울
    "cond[mrkt_cd::EQ]": "0110211",  # 가락도매
}

OUT_PATH = Path(__file__).parent / "data" / "raw_cabbage.json"


def extract_items(body):
    """body.items 가 리스트 / {"item": [...]} / {"item": {...}} / 빈 값 어느 형태여도 리스트로 반환"""
    items = body.get("items")
    if not items:
        return []
    if isinstance(items, dict):
        items = items.get("item", [])
    if isinstance(items, dict):
        items = [items]
    return list(items)


def fetch_page(year, vrty_cd, page_no):
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": page_no,
        "numOfRows": NUM_OF_ROWS,
        "returnType": "JSON",
        "cond[exmn_ymd::GTE]": f"{year}0101",
        "cond[exmn_ymd::LTE]": f"{year}1231",
        **BASE_COND,
        "cond[vrty_cd::EQ]": vrty_cd,
    }
    res = requests.get(URL, params=params, timeout=30)
    res.raise_for_status()
    data = res.json()

    # HTTP 응답이 정상이어도 본문에 인증 오류가 있는지 확인한다
    if "OpenAPI_ServiceResponse" in data:
        err = data["OpenAPI_ServiceResponse"]["cmmMsgHeader"]
        raise RuntimeError(f"인증/호출 오류 {err.get('returnReasonCode')}: {err.get('errMsg')}")

    header = data["response"].get("header", {})
    body = data["response"].get("body")
    if body is None:
        raise RuntimeError(f"API 오류 {header.get('resultCode')}: {header.get('resultMsg')}")
    return int(body.get("totalCount", 0)), extract_items(body), header


all_rows = []
summary = []

for year in YEARS:
    for vrty_cd, vrty_name in VARIETIES.items():
        page_no = 1
        total, items, header = fetch_page(year, vrty_cd, page_no)
        rows = list(items)
        # 아직 덜 받은 자료가 있으면 다음 쪽도 가져온다
        while len(rows) < total:
            page_no += 1
            _, items, _ = fetch_page(year, vrty_cd, page_no)
            if not items:
                break
            rows.extend(items)
            time.sleep(0.2)

        for r in rows:
            r["query_year"] = year
            r["query_vrty_cd"] = vrty_cd
        all_rows.extend(rows)

        ok = "OK" if len(rows) == total else "MISMATCH"
        summary.append((year, vrty_cd, vrty_name, total, len(rows), page_no, ok))
        print(f"[{header.get('resultCode')} {header.get('resultMsg')}] {year}년 {vrty_cd} {vrty_name:<10} "
              f"totalCount={total:>3}  수집={len(rows):>3}  pages={page_no}  {ok}")
        time.sleep(0.2)

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUT_PATH.write_text(json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8")

print("\n===== 수집 요약 =====")
print(f"호출 조합 수: {len(summary)}개 (10년 x 4품종)")
print(f"검증 기준(2015년 봄배추 01) totalCount: {summary[0][3]} (기대값 66)")
print(f"totalCount 불일치 조합: {sum(1 for s in summary if s[-1] != 'OK')}개")
print(f"0건 조합: {[(s[0], s[2]) for s in summary if s[3] == 0]}")
print(f"총 수집 건수: {len(all_rows)}건 -> {OUT_PATH.name} 저장")
