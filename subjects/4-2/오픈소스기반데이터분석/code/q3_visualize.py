# 문 3. 연도별 평균 가격 선 그래프(3-1), 계절별 평균 가격 막대 그래프(3-2)
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

STUDENT_ID_LAST4 = "3257"  # 그래프 제목과 파일명에 붙일 학번 끝 네 자리
DATA_DIR = Path(__file__).parent / "data"
FIG_DIR = Path(__file__).parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

plt.rcParams["font.family"] = "Malgun Gothic"  # 그래프의 한글은 맑은 고딕으로 표시한다
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv(DATA_DIR / "cabbage_preprocessed.csv", encoding="utf-8-sig",
                 dtype={"query_vrty_cd": str, "vrty_cd": str})  # 품종코드는 숫자로 바꾸지 않고 읽는다
SEASONS = ["봄", "여름", "가을", "겨울"]

# ---------------- 문 3-1. 연도별 평균 가격 선 그래프 ----------------
yearly = df.groupby("year")["exmn_dd_prc"].mean().reindex(range(2015, 2025))
print("연도별 평균 가격(원)")
print(yearly.round(0))

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(yearly.index, yearly.values, marker="o", linewidth=2)
for x, y in zip(yearly.index, yearly.values):
    ax.annotate(f"{y:,.0f}", (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
ax.set_title(f"연도별 배추 평균 가격 변화 - {STUDENT_ID_LAST4}")
ax.set_xlabel("연도")
ax.set_ylabel("평균 가격(원 / 10kg 그물망 3포기)")
ax.set_xticks(yearly.index)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG_DIR / f"yearly_price_{STUDENT_ID_LAST4}.png", dpi=150)
plt.show()

# ---------------- 문 3-2. 계절별 평균 가격 막대 그래프 ----------------
seasonal = df.groupby("season")["exmn_dd_prc"].mean().reindex(SEASONS)
print("\n계절별 평균 가격(원)")
print(seasonal.round(0))

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(seasonal.index, seasonal.values, color=["#8BC34A", "#F44336", "#FF9800", "#2196F3"])
ax.bar_label(bars, labels=[f"{v:,.0f}원" for v in seasonal.values], padding=3)
ax.set_title(f"계절별 배추 평균 가격 - {STUDENT_ID_LAST4}")
ax.set_xlabel("계절")
ax.set_ylabel("평균 가격(원 / 10kg 그물망 3포기)")
ax.set_ylim(0, seasonal.max() * 1.15)
fig.tight_layout()
fig.savefig(FIG_DIR / f"seasonal_price_{STUDENT_ID_LAST4}.png", dpi=150)
plt.show()
