# 문 2. 수집한 JSON을 DataFrame으로 변환(2-1)하고 year·season 컬럼을 추가(2-2)
import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

# ---------------- 문 2-1. JSON -> DataFrame, 기본 정보 ----------------
raw = json.loads((DATA_DIR / "raw_cabbage.json").read_text(encoding="utf-8"))
df = pd.DataFrame(raw)

print("1) 데이터 크기(행, 열):", df.shape)
print("\n2) 컬럼 목록:", list(df.columns))
print("\n3) 상위 5행 (주요 컬럼)")
print(df[["exmn_ymd", "vrty_cd", "vrty_nm", "grd_nm", "mrkt_nm", "unit", "unit_sz", "exmn_dd_prc"]].head())
print("\n4) 컬럼별 자료형·결측")
df.info()
print("\n5) 품종별 건수")
print(df["query_vrty_cd"].value_counts().sort_index())

# ---------------- 문 2-2. year, season 컬럼 추가 ----------------
# 조회용으로 붙인 두 컬럼을 빼고 같은 자료인지 비교한다
before = len(df)
df = df.drop_duplicates(subset=[c for c in df.columns if c not in ("query_year", "query_vrty_cd")])
print(f"\n중복 제거: {before} -> {len(df)}건")

# 조사일자를 날짜로 읽어 연도와 월을 꺼낼 준비를 한다
df["exmn_ymd"] = pd.to_datetime(df["exmn_ymd"].astype(str), format="%Y%m%d", errors="coerce")
print("날짜 변환 실패(NaT):", df["exmn_ymd"].isna().sum(), "건")

# 가격의 쉼표를 지우고 숫자로 읽되, 읽지 못한 값은 비워 둔다
df["exmn_dd_prc"] = pd.to_numeric(df["exmn_dd_prc"].astype(str).str.replace(",", ""), errors="coerce")
print("가격 변환 실패(NaN):", df["exmn_dd_prc"].isna().sum(), "건")

df["year"] = df["exmn_ymd"].dt.year
df = df[df["year"].between(2015, 2024)].copy()  # 분석할 열 해에 해당하는 행만 남긴다
SEASON_BY_MONTH = {3: "봄", 4: "봄", 5: "봄",
                   6: "여름", 7: "여름", 8: "여름",
                   9: "가을", 10: "가을", 11: "가을",
                   12: "겨울", 1: "겨울", 2: "겨울"}
df["season"] = df["exmn_ymd"].dt.month.map(SEASON_BY_MONTH)
df["season"] = pd.Categorical(df["season"], categories=["봄", "여름", "가을", "겨울"], ordered=True)

print("\n변환 결과 확인 (월별로 1건씩 표본)")
sample = df.sort_values("exmn_ymd").groupby(df["exmn_ymd"].dt.month).head(1)
print(sample[["exmn_ymd", "year", "season", "query_vrty_cd", "exmn_dd_prc"]].to_string(index=False))

print("\n연도별 건수")
print(df["year"].value_counts().sort_index())
print("\n계절별 건수")
print(df["season"].value_counts().sort_index())

df.to_csv(DATA_DIR / "cabbage_preprocessed.csv", index=False, encoding="utf-8-sig")
print("\n저장 완료: cabbage_preprocessed.csv")
