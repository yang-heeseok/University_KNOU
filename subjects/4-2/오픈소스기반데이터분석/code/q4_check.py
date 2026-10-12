# 문 4 해석용 보조 집계 (제출 필수 아님 — 500자 서술의 근거 수치 확인용)
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
pd.set_option("display.width", 200)
df = pd.read_csv(DATA_DIR / "cabbage_preprocessed.csv", encoding="utf-8-sig",
                 dtype={"query_vrty_cd": str, "vrty_cd": str})  # 품종코드 앞자리 0 유지
SEASONS = ["봄", "여름", "가을", "겨울"]

# 1) 연도 x 계절 평균 — 어느 해 어느 계절이 튀었는가
pivot = df.pivot_table(index="year", columns="season", values="exmn_dd_prc", aggfunc="mean")
print("연도 x 계절 평균 가격(원)\n", pivot.reindex(columns=SEASONS).round(0))

# 2) 연도 x 계절 관측 건수 — 평균이 몇 건에 기반하는가
counts = df.pivot_table(index="year", columns="season", values="exmn_dd_prc", aggfunc="count")
print("\n연도 x 계절 관측 건수\n", counts.reindex(columns=SEASONS))

# 3) 전년 대비 증감률 — '급등/급락' 표현의 근거
yearly = df.groupby("year")["exmn_dd_prc"].mean()
print("\n연도별 평균과 전년 대비 증감률(%)")
print(pd.DataFrame({"평균": yearly.round(0), "증감률": (yearly.pct_change() * 100).round(1)}))

# 4) 품종별 평균 — 계절 차이가 품종(고랭지 등) 차이와 겹치는지
print("\n품종별 평균 가격·건수")
print(df.groupby("query_vrty_cd")["exmn_dd_prc"].agg(["mean", "count"]).round(0))

# 5) 연도별 최고가 시점
top = df.loc[df.groupby("year")["exmn_dd_prc"].idxmax(), ["year", "exmn_ymd", "season", "query_vrty_cd", "exmn_dd_prc"]]
print("\n연도별 최고가 일자\n", top.to_string(index=False))

# 6) 거래 단위 — 가격 단위가 연도·품종별로 같은지 (컬럼명은 2-1의 컬럼 목록에서 확인 후 수정)
unit_cols = [c for c in df.columns if "unit" in c.lower()]
if unit_cols:
    print("\n연도별 거래 단위\n", df.groupby("year")[unit_cols].agg(lambda s: sorted(s.astype(str).unique())))
