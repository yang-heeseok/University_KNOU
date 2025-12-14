# 12강. 8장 기술통계(2)  - Python

## 학습 목표
1. 파이썬을 이용하여 기술통계량을 구하는 방법을 알 수 있다.
2. 파이썬을 이용하여 그룹별 기술통계량을 구하는 방법을 알 수 있다.
3. 파이썬을 이용하여 히스토그램, 줄기-잎 그림, 상자그림을 그리는 방법을 알 수 있다.
4. 파이썬을 이용하여 빈도표 및 분할표를 작성할 줄 안다.

---

## 📝 요약 (Summary)
1.  **Pandas 기술통계**: Pandas DataFrame의 `.describe()` 메서드는 기본적인 요약 통계를 한 번에 제공하는 가장 대표적인 함수입니다. 더 나아가 왜도(skewness), 첨도(kurtosis) 등 분포의 형태를 파악하기 위해서는 `.skew()`, `.kurt()` 메서드나 `scipy.stats` 모듈을 활용할 수 있습니다.
2.  **그룹별 기술통계**: 데이터 분석의 핵심인 그룹별 분석은 `.groupby()` 메서드를 통해 수행됩니다. 특정 열을 기준으로 데이터를 그룹화한 뒤, `.agg()`, `.describe()` 등 다양한 집계 함수를 적용하여 그룹 간의 특성을 비교하고 분석할 수 있습니다.
3.  **분포 시각화**: 데이터의 분포를 시각적으로 파악하기 위해 `matplotlib`이나 `seaborn` 라이브러리가 널리 사용됩니다. 히스토그램(`hist()`), 상자 그림(`boxplot()`) 등을 통해 데이터의 중심 경향, 산포도, 이상치 등을 직관적으로 확인할 수 있습니다.
4.  **빈도 분석**: 범주형 데이터의 분포는 `pd.value_counts()`로 빈도표를, 두 범주형 변수 간의 관계는 `pd.crosstab()`으로 분할표(교차표)를 작성하여 분석합니다. 분할표는 `scipy.stats.chi2_contingency` 함수와 연계하여 변수 간 독립성 검정에 활용될 수 있습니다.

---

## ✏️ 심화 학습 (Study Subject)
### 1. 파이썬 기술통계 함수, 어떻게 다른가? (R과 비교)

파이썬 데이터 분석 생태계는 다양한 기술통계 함수를 제공하며, 각 함수는 목적과 스타일에 따라 선택할 수 있습니다.

| 함수/메서드 | 라이브러리 | 주요 특징 | 장점 | 단점 | 추천 상황 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`.describe()`** | `pandas` | DataFrame의 숫자형 열에 대한 8가지 요약 통계(count, mean, std, min, 25%, 50%, 75%, max)를 제공합니다. | Pandas 기본 기능, 사용법이 매우 간단함. | 제공하는 통계량이 제한적임 (왜도, 첨도 미포함). | 데이터의 전체적인 구조를 **가장 빠르게 훑어볼 때**. |
| **`.agg()`** | `pandas` | `.agg(['sum', 'mean', 'std'])`와 같이 원하는 통계 함수 리스트를 직접 지정하여 계산합니다. | 원하는 통계량만 선택적으로 계산 가능, 사용자 정의 함수 적용 가능. | 여러 통계량을 한 번에 보려면 코드가 길어짐. | 특정 통계량(예: 합계, 평균)만 **선택적으로 계산**하고 싶을 때. |
| **`scipy.stats.describe()`** | `scipy` | `nobs`, `minmax`, `mean`, `variance`, `skewness`, `kurtosis` 등 더 풍부한 통계량을 제공합니다. | 데이터 분포의 형태(왜도, 첨도)까지 한 번에 파악 가능. | 추가 라이브러리 필요, DataFrame에 직접 적용하려면 반복문/apply 필요. | 데이터 분포의 특징까지 **심층적으로 분석**하고 보고서를 작성할 때. |
| **`researchpy.summary_cont()`** | `researchpy` | R의 `summary()`와 유사한 스타일의 결과와 함께 신뢰구간(CI) 등 더 상세한 통계 정보를 제공합니다. | 통계적으로 더 풍부한 정보를 제공. | 추가 라이브러리 설치 필요. | R 환경에 익숙하며, **학술적 보고**에 필요한 상세 통계량이 필요할 때. |

### 2. 그룹별 통계의 핵심: `groupby`의 Split-Apply-Combine 전략

Pandas의 `.groupby()`는 R의 `dplyr`과 마찬가지로 **'Split-Apply-Combine'** 전략을 구현하는 데이터 집계의 핵심 도구입니다.

#### 가. 가상 시나리오: "iris 데이터셋에서, 종(species)별로 꽃잎 길이(petal_length)의 평균과 표준편차 구하기"

```python
import seaborn as sns

iris = sns.load_dataset('iris')

# 1. 'species' 열을 기준으로 데이터를 3개의 그룹으로 나눈다. (Split)
grouped_iris = iris.groupby('species')

# 2. 각 그룹의 'petal_length' 열에 대해 평균과 표준편차를 계산한다. (Apply)
# 3. 계산된 결과를 새로운 DataFrame으로 합친다. (Combine)
summary_df = grouped_iris['petal_length'].agg(['mean', 'std'])

print(summary_df)
# 결과:
#             mean       std
# species                    
# setosa     1.462  0.173664
# versicolor 4.260  0.469911
# virginica  5.552  0.551895
```

#### 나. 오개념 분석: "`.groupby()`만 호출하면 그룹별 계산이 끝나는 것 아닌가요?"

-   **분석**: **아닙니다.** `.groupby()` 자체는 데이터를 그룹으로 나누는 **'계획'**을 세우고, 그룹 정보를 담은 `DataFrameGroupBy` 객체를 생성할 뿐, 실제 계산을 수행하지는 않습니다. 비유하자면, 재료를 종류별로 나누어 놓기만 한 상태입니다.
-   **핵심**: 반드시 `.sum()`, `.mean()`, `.agg()`, `.describe()`와 같은 **집계 함수(aggregation function)**를 뒤에 호출해야만, 각 그룹에 대한 실제 'Apply'와 'Combine' 과정이 일어나 의미 있는 결과를 얻을 수 있습니다. 이처럼 계산을 미루는 방식을 **'지연 평가(Lazy Evaluation)'**라고 하며, 여러 연산을 묶어 효율적으로 처리하는 데 도움을 줍니다.


---

## ❓ 연습 문제 및 해설

### 📝 문제

**1. [파이썬에서 자료 파일을 읽어서 새로운 변수 total = midterm + final을 만들고자 한다. (        ) 명령은?](#prob-1)**
```python
import pandas as pd
score = pd.read_csv("c:/data/rpy/score.csv")
score.head(2)

Out:
   id gender  midterm  final
0  13001      f       60     80
1  13003      m       90     72

   id gender  midterm  final
0  13001      f       60     80
1  13003      m       90     72

(  )

score.head(2)

Out:
   id gender  midterm  final  total
0  13001      f       60     80    140
1  13003      m       90     72    162
```

<br>

**2. [데이터객체 score에서 변수 total 의 평균, 표준편차를 구하는 명령 (   A   ), (   B   )는?](#prob-2)**
```python
score.head(2)

Out:
   id gender  midterm  final  total
0  13001      f       60     80    140
1  13003      m       90     72    162

(  A  )

Out: 122.65168539325843

(  B  )

Out: 37.882324111407364
```

<br>

**3. [gender를 그룹변수로 하여 변수 total의 기술통계량을 구하고자 한다. (        ) 명령은?](#prob-3)**
```python
score.head(2)

Out:
   id gender  midterm  final  total
0  13001      f       60     80    140
1  13003      m       90     72    162

gstat = (  )

gstat

Out:
         count        mean        std   min    25%    50%    75%    max
gender                                                                
f         35.0  122.771429  34.295503  35.0  102.5  122.0  152.0  172.0
m         54.0  122.574074  40.351101  36.0   91.5  133.0  156.5  193.0
```

<br>

**4. [다음과 같은 상자그림을 그리고자 한다. (        ) 명령은?](#prob-4)**
```python
import pandas as pd
import seaborn as sns

score.head(2)

Out:
   id gender  midterm  final  total
0  13001      f       60     80    140
1  13003      m       90     72    162

scorebox = (  )(x="gender", y="total", data=score)
```

<br>

**5. [다음과 같은 두 이산형 변수의 분할표를 구하고자 한다. (        ) 명령은?](#prob-5)**
```python
import pandas as pd

grade_q1 = (  )(index=engete["grade"], columns=engete["q1"])

grade_q1.index = ["1학년", "2학년", "3학년", "4학년"]

grade_q1

Out:
      q1   0.0  1.0   2.0
1학년    0   80    23
2학년    0   66    37
3학년    0   55    44
4학년    1   55    38
```

<br>

---

### 🔑 정답

1. score["total"] = score["midterm"]+score["final"]
2. (A) = score['total'].mean(),(B) = score['total'].std()
3. score.groupby("gender")['total'].describe()
4. sns.boxplot
5. pd.crosstab

---

### 🧐 해설

<a id="prob-1"></a>
**1. 새로운 변수 `total`을 생성하는 명령은?**
> **정답**: `score["total"] = score["midterm"] + score["final"]`
> **해설**: Pandas DataFrame에서 새로운 열(column)을 추가하는 가장 간단한 방법은 `df['새로운열이름'] = 값` 형식으로 할당하는 것입니다. 이 코드에서는 기존의 `midterm` 열과 `final` 열을 더한 결과를 `total`이라는 새로운 열에 저장합니다. Pandas는 열 간의 연산을 요소별(element-wise)로 수행하므로, 각 학생의 중간고사와 기말고사 점수가 더해져 총점이 계산됩니다.

<a id="prob-2"></a>
**2. `total` 변수의 평균과 표준편차를 구하는 명령은?**
> **정답**: (A) `score['total'].mean()`, (B) `score['total'].std()`
> **해설**: DataFrame에서 특정 열을 선택하면(`score['total']`), 그 결과는 Pandas Series 객체가 됩니다. Series 객체는 다양한 기술통계 메서드를 내장하고 있습니다.
> - `.mean()`: Series의 모든 값에 대한 산술 평균을 계산합니다.
> - `.std()`: Series의 표준편차를 계산합니다.

<a id="prob-3"></a>
**3. `gender`를 그룹변수로 하여 `total`의 기술통계량을 구하는 명령은?**
> **정답**: `score.groupby("gender")['total'].describe()`
> **해설**: 이 코드는 데이터 분석의 핵심 패턴인 **'Split-Apply-Combine'** 전략을 보여줍니다.
> 1.  **`score.groupby("gender")`**: `score` DataFrame을 `gender` 열의 고유값('f', 'm')에 따라 여러 그룹으로 나눕니다(Split).
> 2.  **`['total']`**: 각 그룹에서 `total` 열만 선택합니다.
> 3.  **`.describe()`**: 각 그룹의 `total` Series에 대해 기술통계량(개수, 평균, 표준편차, 최솟값, 사분위수, 최댓값)을 계산하고(Apply), 그 결과를 하나의 새로운 DataFrame으로 합칩니다(Combine).

<a id="prob-4"></a>
**4. 상자그림(Boxplot)을 그리는 명령은?**
> **정답**: `sns.boxplot`
> **해설**: `seaborn`은 통계적 시각화를 위한 파이썬 라이브러리입니다. `sns.boxplot()` 함수는 범주형 변수에 따른 연속형 변수의 분포를 비교하는 데 매우 유용합니다.
> - `x="gender"`: x축에 범주형 변수인 `gender`를 지정합니다.
> - `y="total"`: y축에 연속형 변수인 `total`을 지정합니다.
> - `data=score`: 사용할 데이터프레임을 지정합니다.
> 이 함수는 `gender`의 각 범주('f', 'm')별로 `total` 점수의 분포를 나타내는 상자 그림을 그려줍니다.

<a id="prob-5"></a>
**5. 두 이산형 변수의 분할표(교차표)를 구하는 명령은?**
> **정답**: `pd.crosstab`
> **해설**: `pandas.crosstab()` 함수는 두 개 이상의 범주형 변수 간의 교차 빈도표(분할표, contingency table)를 생성하는 데 사용됩니다.
> - `index=engete["grade"]`: 분할표의 행(row)이 될 변수를 지정합니다.
> - `columns=engete["q1"]`: 분할표의 열(column)이 될 변수를 지정합니다.
> 결과적으로 각 학년(`grade`)과 질문 응답(`q1`)의 조합이 몇 번 나타나는지를 세어 표 형태로 보여줍니다.

---

## ✅ O/X 확인문제

**1.** [Pandas의 `.describe()` 메서드는 기본적으로 왜도(skewness)와 첨도(kurtosis)를 포함하여 출력한다.](#ox-1) **(O / X)**
**2.** `df.groupby('group_col')` 코드를 실행하는 것만으로도 그룹별 평균이 계산된다. **(O / X)**
**3.** `seaborn` 라이브러리의 `boxplot()` 함수는 범주별 데이터 분포를 비교하는 상자 그림을 그리는 데 사용된다. **(O / X)**
**4.** `pd.crosstab()` 함수는 단일 범주형 변수의 빈도수를 계산하는 데 사용된다. **(O / X)**
**5.** 데이터의 왜도를 계산하려면 반드시 `scipy` 라이브러리를 사용해야 한다. **(O / X)**
**6.** `seaborn`은 `matplotlib`을 기반으로 만들어져, `seaborn` 그래프에 `matplotlib` 함수를 사용하여 세부 조정을 할 수 있다. **(O / X)**
**7.** [Pandas DataFrame에서 `df.groupby('A').agg(['sum', 'mean'])` 코드는 그룹 A별로 합계와 평균을 동시에 계산한다.](#ox-7) **(O / X)**
**8.** `pd.value_counts()`는 두 변수 간의 관계를 나타내는 분할표를 생성하는 함수이다. **(O / X)**
**9.** 히스토그램은 연속형 변수의 분포를 구간별로 나누어 막대 형태로 표현한 그래프이다. **(O / X)**
**10.** [`score.groupby("gender")['total']`의 결과물은 Pandas DataFrame이다.](#ox-10) **(O / X)**


> <a id="ox-1"></a>
> **1. 정답**: X
> **해설**: `.describe()`는 count, mean, std, min, max, 사분위수 등 8가지 기본 통계량만 제공합니다. 왜도나 첨도는 `.skew()`, `.kurt()` 메서드나 `scipy.stats.describe()`를 사용해야 합니다.

> <a id="ox-2"></a>
> **2. 정답**: X
> **해설**: `.groupby()`는 데이터를 그룹으로 묶는 '계획'을 세우고 `DataFrameGroupBy` 객체를 생성할 뿐, 실제 계산을 수행하지 않습니다. `.mean()`, `.sum()`, `.agg()` 등 집계 함수를 호출해야 계산이 실행됩니다.

> <a id="ox-3"></a>
> **3. 정답**: O
> **해설**: `seaborn.boxplot(x="category", y="value", data=df)`와 같이 사용하여 범주형 변수(x)에 따른 연속형 변수(y)의 분포를 상자 그림으로 쉽게 시각화할 수 있습니다.

> <a id="ox-4"></a>
> **4. 정답**: X
> **해설**: `pd.crosstab()`은 두 개 이상의 범주형 변수 간의 교차 빈도표(분할표)를 생성합니다. 단일 변수의 빈도수는 `series.value_counts()`를 사용합니다.

> <a id="ox-5"></a>
> **5. 정답**: X
> **해설**: Pandas Series 객체 자체에 `.skew()` 메서드가 내장되어 있어 `df['column'].skew()`와 같이 직접 계산할 수 있습니다.

> <a id="ox-6"></a>
> **6. 정답**: O
> **해설**: Seaborn은 Matplotlib을 더 사용하기 쉽게 만든 고수준 라이브러리입니다. 따라서 `sns.boxplot()`으로 그래프를 그린 후 `plt.title('My Plot')`과 같이 Matplotlib 함수로 제목을 추가할 수 있습니다.

> <a id="ox-7"></a>
> **7. 정답**: O
> **해설**: `.agg()` 메서드는 여러 집계 함수를 리스트 형태로 전달받아 한 번에 계산하고, 각 함수명을 열 이름으로 하는 DataFrame을 반환합니다.

> <a id="ox-8"></a>
> **8. 정답**: X
> **해설**: `pd.value_counts()`는 하나의 Series(열)에 있는 각 고유값의 개수를 세는 함수입니다. 두 변수 간의 분할표는 `pd.crosstab()`을 사용합니다.

> <a id="ox-9"></a>
> **9. 정답**: O
> **해설**: 히스토그램은 데이터의 전체 범위를 여러 개의 동일한 구간(bin)으로 나누고, 각 구간에 속하는 데이터의 개수를 막대의 높이로 표현하여 분포를 시각화합니다.

> <a id="ox-10"></a>
> **10. 정답**: X
> **해설**: `score.groupby("gender")`는 `DataFrameGroupBy` 객체를, 거기서 `['total']` 열을 선택하면 `SeriesGroupBy` 객체를 반환합니다. 아직 집계 함수가 적용되지 않아 DataFrame이 아닙니다.

---

## 📖 심화 학습 예시 답안

#### 1. 기술통계, 왜 `.describe()`만으로는 부족할까?

`.describe()`는 매우 편리하지만, 본격적인 데이터 분석을 위해서는 데이터의 '분포 형태'까지 파악해야 합니다. `scipy.stats.describe()`나 Pandas의 `.skew()`, `.kurt()` 메서드는 이러한 요구를 충족시켜주는 훌륭한 도구입니다.

1.  **분포의 비대칭성 (왜도, Skewness)**: 데이터 분포가 좌우로 얼마나 치우쳐 있는지를 알려줍니다.
    -   **왜도 > 0 (양의 왜도)**: 분포의 꼬리가 오른쪽으로 길게 늘어져 있으며, 평균이 중앙값보다 큽니다. (예: 개인 소득 분포, 소수의 고소득자가 평균을 끌어올림)
    -   **왜도 < 0 (음의 왜도)**: 분포의 꼬리가 왼쪽으로 길게 늘어져 있으며, 평균이 중앙값보다 작습니다. (예: 쉬운 시험의 점수 분포, 다수가 고득점)
    -   **시나리오**: 두 매장의 일일 매출 데이터 평균이 동일하더라도, 한 매장의 왜도가 매우 크다면 이는 '대박'을 치는 날이 가끔 있지만 평소에는 매출이 저조하다는 의미일 수 있습니다. 이는 안정적인 재고 관리 전략을 수립하는 데 중요한 정보가 됩니다.

2.  **분포의 뾰족함 (첨도, Kurtosis)**: 분포의 중심이 얼마나 뾰족한지를 알려줍니다.
    -   **첨도 > 0 (Leptokurtic)**: 정규분포보다 더 뾰족하고 꼬리가 두껍습니다. 이는 이상치(outlier)가 존재할 가능성을 시사합니다.
    -   **첨도 < 0 (Platykurtic)**: 정규분포보다 더 평평하고 꼬리가 얇습니다.
    -   **시나리오**: 제품 불량률 데이터의 첨도가 매우 높다면, 이는 대부분의 제품은 문제가 없지만 특정 조건에서 불량이 집중적으로 발생하고 있음을 의미할 수 있습니다.

이처럼 왜도와 첨도를 확인하면, 단순히 평균과 표준편차만 보는 것을 넘어 데이터가 어떤 형태의 분포를 가지는지 입체적으로 이해하고, 분석 모델 선택(예: 정규성 가정이 필요한 모델)에 중요한 단서를 얻을 수 있습니다.

#### 2. `groupby`의 세 가지 무기: `agg`, `transform`, `filter`

Pandas의 `groupby` 객체는 단순히 데이터를 요약하는 것을 넘어, 그룹별로 다양한 연산을 수행하는 세 가지 주요 메서드를 제공합니다.

| 메서드 | 반환 형태 | 주요 목적 | 사용 시나리오 |
| :--- | :--- | :--- | :--- |
| **`agg()`** | 그룹별 요약 통계가 담긴 **새로운 DataFrame** | **데이터 집계**: 각 그룹을 하나의 요약된 값(평균, 합계 등)으로 변환 | "각 부서별 평균 연봉은 얼마인가?" |
| **`transform()`** | **원본 DataFrame과 동일한 모양(shape)**의 Series | **그룹 내 표준화**: 그룹별 계산 결과를 원본 데이터의 모든 행에 동일하게 적용 | "각 직원의 연봉이 자신이 속한 부서의 평균 연봉 대비 얼마나 높은가?" |
| **`filter()`** | 원본 DataFrame의 **부분집합(subset)** | **그룹 선택**: 특정 조건을 만족하는 그룹의 데이터 전체를 선택하거나 제외 | "직원이 10명 이상인 부서의 데이터만 보고 싶다." |

**코드 예시:**
```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'department': ['Sales', 'Sales', 'HR', 'HR', 'IT', 'IT', 'IT'],
    'employee': ['John', 'Jane', 'Peter', 'Mary', 'Sue', 'Mike', 'Tom'],
    'salary': [5000, 5500, 4000, 4200, 6000, 6500, 6100]
})

# 1. agg: 부서별 평균 연봉과 직원 수 계산
agg_result = df.groupby('department')['salary'].agg(['mean', 'count'])
# print(agg_result)

# 2. transform: 각 직원의 연봉이 속한 부서 평균 대비 얼마나 차이 나는지 계산
df['salary_vs_dept_mean'] = df['salary'] - df.groupby('department')['salary'].transform('mean')
# print(df)

# 3. filter: 직원이 3명 이상인 부서의 데이터만 필터링
filter_result = df.groupby('department').filter(lambda x: len(x) >= 3)
# print(filter_result)
```

---

## 🌐 최신 동향 및 추가 정보

### 1. Pandas를 넘어서: 대용량 데이터를 위한 Polars의 부상

Pandas는 파이썬 데이터 분석의 표준이지만, 수 기가바이트(GB)가 넘는 대용량 데이터를 다룰 때는 메모리 부족이나 속도 저하 문제를 겪을 수 있습니다. 이러한 한계를 극복하기 위해 Rust 언어로 개발된 **Polars** 라이브러리가 차세대 데이터프레임 도구로 주목받고 있습니다.

-   **핵심 특징**:
    -   **병렬 처리(Multi-core Processing)**: CPU의 모든 코어를 활용하여 데이터를 병렬로 처리하므로 연산 속도가 매우 빠릅니다.
    -   **지연 평가(Lazy Evaluation)**: 사용자가 요청한 전체 계산 과정을 최적화한 후 한 번에 실행하여, 불필요한 중간 계산과 메모리 사용을 최소화합니다.
    -   **효율적인 문법**: Pandas와 유사하면서도 더 간결하고 일관된 API를 제공하여 생산성을 높입니다.

```python
# Polars로 기술통계량 계산하기
import polars as pl

# Polars는 대용량 CSV 파일도 매우 빠르게 읽어들입니다.
df = pl.read_csv("large_dataset.csv")

# .describe() 메서드는 Pandas와 유사하게 동작하며 매우 빠릅니다.
print(df.describe())
```

일상적인 분석에는 Pandas가 여전히 훌륭한 도구이지만, 성능이 중요한 대용량 데이터 처리 환경에서는 Polars가 강력한 대안이 될 수 있습니다.

### 2. 클릭 몇 번으로 보고서 완성: 자동화된 EDA 도구의 활용

데이터의 모든 변수에 대해 일일이 `.describe()`, `.hist()` 등을 실행하는 것은 반복적이고 시간이 많이 소요되는 작업입니다. 최근에는 이러한 탐색적 데이터 분석(EDA) 과정을 자동화하여 종합적인 리포트를 생성해주는 라이브러리들이 널리 사용되고 있습니다.

-   **대표적인 도구: `ydata-profiling`** (구 `pandas-profiling`)
    -   단 몇 줄의 코드로 데이터프레임 전체에 대한 상세한 HTML 리포트를 생성합니다.
    -   리포트에는 각 변수별 기술통계량, 히스토그램, 결측치 분석, 변수 간 상관관계 등 분석에 필요한 거의 모든 정보가 시각화되어 포함됩니다.

```python
# ydata-profiling으로 EDA 리포트 생성하기
# pip install ydata-profiling

from ydata_profiling import ProfileReport
import seaborn as sns

iris = sns.load_dataset('iris')

# ProfileReport 객체를 생성하고 HTML 파일로 저장
profile = ProfileReport(iris, title="Iris Dataset Profiling Report")
profile.to_file("iris_report.html")
```

이러한 자동화 도구는 데이터 분석 초기에 전체 데이터의 특징과 잠재적인 문제점(결측치, 이상치 등)을 빠르게 파악하는 데 매우 유용합니다.

---

## 📚 핵심 용어집

- **기술통계 (Descriptive Statistics)**: 수집한 데이터를 요약, 묘사, 설명하는 통계 기법. 평균, 표준편차, 최빈값, 사분위수 등을 통해 데이터의 중심 경향, 산포도, 분포 형태를 파악하는 것을 목표로 합니다.
- **Pandas**: 파이썬에서 테이블 형태의 데이터를 다루기 위한 핵심 라이브러리. DataFrame과 Series라는 강력한 자료구조를 제공하여 데이터 처리, 정제, 분석을 용이하게 합니다.
- **DataFrame**: 행(row)과 열(column)으로 구성된 2차원 테이블 형태의 Pandas 자료구조. 데이터 분석 작업의 중심이 되며, 엑셀 스프레드시트와 유사한 구조를 가집니다.
- **`groupby`**: Pandas DataFrame의 메서드로, 특정 열의 값을 기준으로 데이터를 여러 그룹으로 나누어(Split) 각 그룹에 집계 함수를 적용(Apply)하고, 그 결과를 다시 하나로 합치는(Combine) 강력한 데이터 집계 도구입니다.
- **왜도 (Skewness)**: 데이터 분포의 비대칭성을 나타내는 척도. 분포의 꼬리가 어느 방향으로 긴지를 알려주며, 0에 가까울수록 좌우 대칭에 가깝습니다.
- **첨도 (Kurtosis)**: 데이터 분포의 뾰족한 정도와 꼬리의 두께를 나타내는 척도. 정규분포와 비교하여 중심이 얼마나 뾰족한지를 알려줍니다.
- **분할표 (Contingency Table)**: 두 개 이상의 범주형 변수에 대한 빈도를 교차하여 정리한 표. `pd.crosstab()` 함수로 생성하며, 변수 간의 관계나 독립성을 파악하는 데 사용됩니다.
- **상자 그림 (Box Plot)**: 데이터의 5가지 요약 수치(최솟값, 1사분위수, 중앙값, 3사분위수, 최댓값)를 사용하여 데이터의 분포와 이상치를 시각적으로 표현하는 그래프. `seaborn.boxplot()`으로 그릴 수 있습니다.

---

## 🤖 AI 학습 파트너를 위한 추가 자료

### 1. 평균의 함정과 중앙값의 중요성

AI가 "데이터의 대표값으로 왜 항상 평균을 쓰면 안 되나요?"라는 질문에 깊이 있는 답변을 생성하도록 유도하는 자료입니다.

-   **핵심**: 평균(Mean)은 **이상치(outlier)에 매우 민감**하지만, 중앙값(Median)은 이상치의 영향을 거의 받지 않아 더 안정적(robust)입니다.
-   **시나리오**: 5명의 연봉 데이터가 `[4000, 4200, 4500, 5000, 5300]` 만원일 때, 평균과 중앙값은 모두 4600만원으로 비슷합니다. 하지만 여기에 연봉이 10억인 한 명이 추가되어 `[4000, 4200, 4500, 5000, 5300, 100000]`이 되면, **평균은 약 19167만원**으로 급등하여 그룹 전체를 대표한다고 보기 어려워집니다. 반면 **중앙값은 4750만원**으로, 여전히 일반적인 연봉 수준을 잘 나타냅니다.
-   **AI 답변 가이드**: 사용자가 대표값에 대해 질문하면, 위와 같은 연봉 시나리오를 예로 들어 설명합니다. "데이터에 극단적인 값이 포함될 수 있는 소득, 부동산 가격 등을 다룰 때는 평균보다 중앙값이 데이터의 중심 경향을 더 안정적으로 나타낼 수 있습니다. 따라서 Pandas의 `.describe()` 결과를 볼 때는 항상 평균(`mean`)과 중앙값(`50%`)을 함께 확인하는 습관이 중요합니다." 와 같이 답변하도록 유도합니다.

### 2. 표준편차 해석의 실제: '68-95-99.7 규칙'

AI가 "표준편차가 10이라는 게 무슨 의미인가요?"라는 질문에 구체적인 해석을 제공하도록 돕는 자료입니다.

-   **핵심**: 데이터가 **정규분포에 가까울 때**, 표준편차는 데이터가 평균으로부터 얼마나 퍼져있는지를 경험적으로 예측하게 해줍니다.
-   **경험적 규칙 (Empirical Rule)**:
    -   **평균 ± 1 * 표준편차** 범위 안에 전체 데이터의 약 **68%**가 포함됩니다.
    -   **평균 ± 2 * 표준편차** 범위 안에 전체 데이터의 약 **95%**가 포함됩니다.
    -   **평균 ± 3 * 표준편차** 범위 안에 전체 데이터의 약 **99.7%**가 포함됩니다.
-   **시나리오**: 어떤 시험 성적의 평균이 70점, 표준편차가 10점이고, 성적 분포가 정규분포를 따른다고 가정합시다.
    -   약 68%의 학생들은 60점(70-10)과 80점(70+10) 사이에 있습니다.
    -   약 95%의 학생들은 50점(70-20)과 90점(70+20) 사이에 있습니다.
    -   95점을 받은 학생은 상위 2.5% 이내에 들 가능성이 높다고 추정할 수 있습니다.
-   **AI 답변 가이드**: 사용자가 표준편차의 의미를 물으면, 단순히 '데이터가 퍼진 정도'라고 답하는 것을 넘어, 정규분포를 가정했을 때의 '68-95-99.7 규칙'을 구체적인 시험 성적 예시와 함께 설명하도록 유도합니다. 이를 통해 사용자는 표준편차를 이용해 특정 데이터 값의 상대적인 위치를 가늠하는 방법을 배울 수 있습니다.

---

## 📚 참고 자료

-   [pandas.DataFrame.describe — pandas documentation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.describe.html): Pandas `describe` 함수의 공식 문서입니다.
-   scipy.stats.describe — SciPy Manual: 왜도, 첨도 등 더 상세한 기술통계량을 제공하는 Scipy 함수의 공식 문서입니다.
-   pandas.DataFrame.groupby — pandas documentation: Pandas `groupby` 기능에 대한 공식 문서로, Split-Apply-Combine 전략을 심도 있게 다룹니다.
-   seaborn.boxplot — seaborn documentation: Seaborn `boxplot` 함수의 공식 문서로, 다양한 시각화 옵션을 확인할 수 있습니다.
-   Python for Data Analysis, 3E by Wes McKinney: Pandas를 개발한 Wes McKinney가 직접 집필한 데이터 분석 필독서입니다.
-   Polars User Guide: 최신 동향에서 소개된 고성능 데이터프레임 라이브러리 Polars의 공식 가이드입니다.