# 과제 2: 공공 API를 활용한 데이터 수집 및 분석 (15점)

> 🚀 **실제 구현 프로젝트**: [python-data-processing](../python-data-processing/) - 완성된 프로젝트 코드와 실행 방법은 [README.md](../python-data-processing/README.md)를 참고하세요.

---

## 📋 과제 내용

data.go.kr(공공데이터포털)에서 제공하는 API를 활용하여 유용한 데이터를 수집하고 분석하시오.

## 🎯 요구사항

### 1. API 선택 및 데이터 수집 (7점)

**선택 가능한 API:**
- 기상청 단기예보 API
- 국토교통부 아파트매매 실거래 상세 자료 API
- 기타 관심 있는 공공 API
  - 기상청 API허브 (https://apihub.kma.go.kr/)
  - 서울시 열린데이터 광장 (https://data.seoul.go.kr/dataList/datasetList.do)

**필수 구현 사항:**
- API 인증키 발급 과정 설명
- requests 라이브러리를 사용한 데이터 수집 코드 작성
- 최소 100건 이상의 데이터 수집

### 2. ETL 과정 구현 (5점)

- **Extract**: API로부터 JSON/XML 데이터 추출
- **Transform**: 필요한 필드만 선택, 데이터 타입 변환 (선택: 이상치 처리)
- **Load**: 정제된 데이터를 Pandas DataFrame으로 적재 후 CSV 저장

### 3. 데이터 시각화 및 인사이트 (3점)

- matplotlib 또는 seaborn을 사용한 시각화 2개 이상
- 수집한 데이터에서 발견한 의미 있는 패턴이나 인사이트 3가지 이상 서술

---

## 📝 해결 계획

### 추천 API: 서울시 공공자전거(따릉이) 대여소 정보 API

**선택 이유:**
- 데이터 접근성이 좋고 안정적
- 100건 이상 데이터 수집 용이 (서울시 전역 대여소 정보)
- 시각화 및 분석이 용이한 구조화된 데이터
- 실생활과 밀접한 관련이 있어 의미 있는 인사이트 도출 가능

### 단계별 구현 계획

#### Step 1: 환경 설정 및 API 키 발급

**1-1. 가상환경 설정 (knou 사용)**

이미 생성된 knou 가상환경을 사용합니다.

```bash
# Windows - 가상환경 활성화
subjects\3-2\python-data-processing\knou\Scripts\activate

# 가상환경 활성화 확인
# 터미널 프롬프트 앞에 (knou) 표시가 나타남
```

**1-2. 설치된 라이브러리 확인 및 추가 설치**

가상환경이 활성화된 상태에서 확인합니다.

```bash
# 현재 설치된 라이브러리 확인
pip list
```

**이미 설치된 라이브러리 (knou 가상환경):**
- ✅ `requests` (2.32.5) - API 호출
- ✅ `pandas` (2.3.3) - 데이터 처리
- ✅ `python-dotenv` (1.1.1) - 환경변수 관리
- ✅ `beautifulsoup4` (4.14.2) - HTML/XML 파싱
- ✅ `numpy` (2.3.4) - 수치 계산

**추가 설치가 필요한 라이브러리:**

```bash
# matplotlib와 seaborn 설치
pip install matplotlib seaborn

# Jupyter Notebook 설치 (선택)
pip install jupyter notebook
```

**라이브러리 용도:**
- `matplotlib`: 기본 시각화 라이브러리
- `seaborn`: 고급 통계 시각화
- `jupyter`: 대화형 노트북 환경

**1-3. API 키 발급 과정**

1. [서울 열린데이터 광장](https://data.seoul.go.kr) 회원가입
2. "서울시 따릉이대여소 마스터 정보" API 검색 및 신청
3. 인증키 발급 받기 (즉시 발급)

**API 정보:**
- **API 명**: 서울시 따릉이대여소 마스터 정보
- **요청 URL**: `http://openapi.seoul.go.kr:8088/(인증키)/(요청파일타입)/bikeStationMaster/(요청시작위치)/(요청종료위치)/`
- **데이터 형식**: JSON, XML 지원

**1-4. 환경변수 설정 (.env 파일)**

프로젝트 루트에 `.env` 파일을 생성하고 API 키를 저장합니다.

```bash
# .env 파일 생성 위치
subjects/3-2/python-data-processing/.env
```

`.env` 파일 내용:
```
SEOUL_API_KEY=your_api_key_here
```

**중요:** `.env` 파일은 반드시 `.gitignore`에 추가하여 Git에 커밋되지 않도록 합니다.

#### Step 2: 데이터 수집 코드 작성

**API 요청 파라미터:**

| 변수명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| KEY | String (필수) | 인증키 | OpenAPI에서 발급된 인증키 |
| TYPE | String (필수) | 요청파일타입 | json, xml, xmlf, xls |
| SERVICE | String (필수) | 서비스명 | bikeStationMaster |
| START_INDEX | INTEGER (필수) | 요청시작위치 | 1 (페이징 시작번호) |
| END_INDEX | INTEGER (필수) | 요청종료위치 | 1000 (페이징 끝번호) |

**응답 데이터 구조:**

| No | 출력명 | 설명 |
|----|--------|------|
| 공통 | list_total_count | 총 데이터 건수 |
| 공통 | RESULT.CODE | 요청결과 코드 |
| 공통 | RESULT.MESSAGE | 요청결과 메시지 |
| 1 | RNTLS_ID | 대여소 ID |
| 2 | ADDR1 | 주소1 |
| 3 | ADDR2 | 주소2 |
| 4 | LAT | 위도 |
| 5 | LOT | 경도 |

**환경변수를 활용한 API 호출 코드:**

```python
import os
from dotenv import load_dotenv
import requests
import pandas as pd
import json

# .env 파일에서 환경변수 로드
load_dotenv()

# 환경변수에서 API 키 가져오기
API_KEY = os.getenv('SEOUL_API_KEY')

if not API_KEY:
    raise ValueError("API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")

# API 엔드포인트 설정
SERVICE_NAME = 'bikeStationMaster'
START_INDEX = 1
END_INDEX = 1000
FILE_TYPE = 'json'

url = f'http://openapi.seoul.go.kr:8088/{API_KEY}/{FILE_TYPE}/{SERVICE_NAME}/{START_INDEX}/{END_INDEX}/'

print(f"API 요청 URL: {url}")

# 데이터 수집
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # HTTP 에러 체크
    data = response.json()

    # 응답 확인
    if 'rentBikeStatus' in data:
        stations = data['rentBikeStatus']['row']
        print(f"데이터 수집 성공: {len(stations)}건")
        print(f"총 데이터 건수: {data['rentBikeStatus']['list_total_count']}")
    else:
        print("응답 구조 확인 필요:", data.keys())

except requests.exceptions.RequestException as e:
    print(f"API 호출 실패: {e}")
except KeyError as e:
    print(f"데이터 구조 오류: {e}")
    print("응답 데이터:", json.dumps(data, indent=2, ensure_ascii=False))
```

#### Step 3: ETL 과정 구현

**Extract (추출):**
```python
# JSON 응답에서 필요한 데이터 추출
if 'rentBikeStatus' in data:
    raw_data = data['rentBikeStatus']['row']
    print(f"추출된 데이터: {len(raw_data)}건")

    # 데이터 샘플 확인
    if raw_data:
        print("\n첫 번째 데이터 샘플:")
        print(json.dumps(raw_data[0], indent=2, ensure_ascii=False))
```

**Transform (변환):**
```python
# DataFrame 생성
df = pd.DataFrame(raw_data)

# 데이터 구조 확인
print("\n데이터 컬럼:", df.columns.tolist())
print("\n데이터 타입:\n", df.dtypes)
print("\n데이터 기본 정보:\n", df.info())

# 필요한 컬럼 선택 (API 응답 구조에 맞게 수정)
selected_columns = ['RNTLS_ID', 'ADDR1', 'ADDR2', 'LAT', 'LOT']
df = df[selected_columns]

# 컬럼명 한글로 변경 (선택)
df.columns = ['대여소ID', '주소1', '주소2', '위도', '경도']

# 데이터 타입 변환
df['위도'] = pd.to_numeric(df['위도'], errors='coerce')
df['경도'] = pd.to_numeric(df['경도'], errors='coerce')

# 결측치 확인
print("\n결측치 확인:")
print(df.isnull().sum())

# 이상치 처리 (위도/경도가 없는 데이터 제거)
df = df.dropna(subset=['위도', '경도'])

# 위도/경도 범위 확인 (서울 지역: 위도 37.4~37.7, 경도 126.7~127.2)
df = df[(df['위도'] >= 37.4) & (df['위도'] <= 37.7)]
df = df[(df['경도'] >= 126.7) & (df['경도'] <= 127.2)]

print(f"\n전처리 후 데이터: {len(df)}건")
```

**Load (적재):**
```python
# 데이터 디렉토리 생성
import os
os.makedirs('data', exist_ok=True)

# CSV 저장
csv_path = 'data/seoul_bike_stations.csv'
df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"\nCSV 파일 저장 완료: {csv_path}")

# JSON 원본 데이터 저장 (백업용)
json_path = 'data/raw_data.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"JSON 파일 저장 완료: {json_path}")

# 데이터 미리보기
print("\n저장된 데이터 샘플:")
print(df.head(10))
```

#### Step 4: 데이터 시각화

**시각화 준비 (한글 폰트 설정):**
```python
import matplotlib.pyplot as plt
import seaborn as sns
import platform

# 한글 폰트 설정
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':  # macOS
    plt.rc('font', family='AppleGothic')
else:  # Linux
    plt.rc('font', family='NanumGothic')

# 마이너스 기호 깨짐 방지
plt.rc('axes', unicode_minus=False)

# 시각화 디렉토리 생성
import os
os.makedirs('visualizations', exist_ok=True)
```

**시각화 1: 대여소 지리적 분포 (산점도)**
```python
plt.figure(figsize=(14, 10))
plt.scatter(df['경도'], df['위도'], alpha=0.5, s=50, c='blue', edgecolors='black')
plt.title('서울시 따릉이 대여소 지리적 분포', fontsize=16, fontweight='bold')
plt.xlabel('경도 (Longitude)', fontsize=12)
plt.ylabel('위도 (Latitude)', fontsize=12)
plt.grid(True, alpha=0.3)

# 대여소 개수 표시
plt.text(0.02, 0.98, f'총 대여소: {len(df)}개',
         transform=plt.gca().transAxes,
         fontsize=12, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('visualizations/station_distribution.png', dpi=300, bbox_inches='tight')
plt.show()
print("시각화 1 저장 완료: visualizations/station_distribution.png")
```

**시각화 2: 구별 대여소 분포 (막대 그래프)**
```python
# 주소1에서 구 정보 추출
df['구'] = df['주소1'].str.extract(r'(.*?구)')[0]

# 구별 대여소 수 집계
district_count = df['구'].value_counts().sort_values(ascending=False)

plt.figure(figsize=(14, 8))
bars = plt.bar(range(len(district_count)), district_count.values,
               color='steelblue', edgecolor='black', alpha=0.7)
plt.xticks(range(len(district_count)), district_count.index, rotation=45, ha='right')
plt.title('서울시 구별 따릉이 대여소 분포', fontsize=16, fontweight='bold')
plt.xlabel('구', fontsize=12)
plt.ylabel('대여소 수', fontsize=12)
plt.grid(axis='y', alpha=0.3)

# 막대 위에 값 표시
for i, bar in enumerate(bars):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height)}',
             ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('visualizations/district_distribution.png', dpi=300, bbox_inches='tight')
plt.show()
print("시각화 2 저장 완료: visualizations/district_distribution.png")
```

**시각화 3: 히트맵 (지역별 밀집도)**
```python
# 위도/경도를 그리드로 나누어 밀집도 계산
from scipy.stats import gaussian_kde

plt.figure(figsize=(14, 10))

# KDE (Kernel Density Estimation)로 밀집도 계산
xy = np.vstack([df['경도'], df['위도']])
z = gaussian_kde(xy)(xy)

# 산점도와 밀집도 함께 표시
scatter = plt.scatter(df['경도'], df['위도'], c=z, s=50,
                      cmap='YlOrRd', alpha=0.6, edgecolors='black')
plt.colorbar(scatter, label='밀집도')
plt.title('서울시 따릉이 대여소 밀집도 히트맵', fontsize=16, fontweight='bold')
plt.xlabel('경도 (Longitude)', fontsize=12)
plt.ylabel('위도 (Latitude)', fontsize=12)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('visualizations/density_heatmap.png', dpi=300, bbox_inches='tight')
plt.show()
print("시각화 3 저장 완료: visualizations/density_heatmap.png")
```

#### Step 5: 인사이트 도출

```python
# 인사이트 분석을 위한 통계 계산
print("=" * 50)
print("📊 서울시 따릉이 대여소 분석 인사이트")
print("=" * 50)

# 1. 전체 통계
print(f"\n1️⃣ 전체 대여소 현황")
print(f"   - 총 대여소 수: {len(df)}개")
print(f"   - 위도 범위: {df['위도'].min():.4f} ~ {df['위도'].max():.4f}")
print(f"   - 경도 범위: {df['경도'].min():.4f} ~ {df['경도'].max():.4f}")

# 2. 구별 분포
print(f"\n2️⃣ 구별 대여소 분포 (TOP 5)")
district_count = df['구'].value_counts().head()
for i, (district, count) in enumerate(district_count.items(), 1):
    print(f"   {i}. {district}: {count}개 ({count/len(df)*100:.1f}%)")

print(f"\n   ➡️ {district_count.index[0]}이 가장 많은 대여소를 보유하고 있습니다.")
print(f"   ➡️ 상위 5개 구가 전체의 {district_count.sum()/len(df)*100:.1f}%를 차지합니다.")

# 3. 지리적 밀집도
from scipy.spatial.distance import pdist
coordinates = df[['경도', '위도']].values
distances = pdist(coordinates, metric='euclidean')
avg_distance = distances.mean()
print(f"\n3️⃣ 대여소 간 평균 거리: {avg_distance:.4f}도 (약 {avg_distance*111:.2f}km)")

# 4. 주소 분석
print(f"\n4️⃣ 주요 위치 키워드 분석")
# 주소2에서 주요 키워드 추출
address_keywords = []
for addr in df['주소2'].dropna():
    if '역' in addr:
        address_keywords.append('역세권')
    elif '공원' in addr:
        address_keywords.append('공원')
    elif '대학' in addr or '학교' in addr:
        address_keywords.append('교육시설')

from collections import Counter
keyword_count = Counter(address_keywords).most_common(5)
for keyword, count in keyword_count:
    print(f"   - {keyword}: {count}개소 ({count/len(df)*100:.1f}%)")
```

**주요 인사이트 (3가지 이상):**

1. **지역별 대여소 분포 불균형**
   - 강남구, 영등포구, 마포구 등 주요 상업지역에 대여소가 집중
   - 도심 지역(중구, 종로구)의 대여소 밀집도가 높음
   - 외곽 지역(강동구, 도봉구 등)의 대여소 접근성 개선 필요

2. **교통 허브 중심의 배치 전략**
   - 지하철역 주변에 대여소가 집중 배치되어 있음
   - 출퇴근 및 환승 수요를 고려한 전략적 배치
   - 마지막 1마일(Last Mile) 교통수단으로 활용

3. **공원 및 관광지 주변 인프라**
   - 한강공원, 올림픽공원 등 주요 공원 주변에 대여소 밀집
   - 여가 및 레저 활동을 위한 자전거 이용 수요 반영
   - 주말과 평일의 이용 패턴 차이 예상

4. **대여소 간 적정 거리 유지**
   - 대부분의 대여소가 300~500m 간격으로 배치
   - 도보 5~10분 거리에서 접근 가능한 편의성 확보
   - 서비스 품질 유지를 위한 체계적 인프라 구축

---

## 📂 프로젝트 구조

```
subjects/3-2/python-data-processing/
├── knou/                        # 가상환경 폴더
├── .env                         # 환경변수 파일 (API 키 저장)
├── .gitignore                   # Git 제외 파일 목록
├── question_2_solution.ipynb    # 주요 실습 노트북 (대화형 분석용)
├── api_data_collector.py        # 데이터 수집 스크립트
├── data_processor.py            # ETL 처리 스크립트
├── data_visualizer.py           # 시각화 스크립트
├── data/
│   ├── raw_data.json           # 원본 API 응답 데이터
│   └── processed_data.csv      # 정제된 데이터
└── visualizations/
    ├── distribution.png
    ├── location_map.png
    └── occupancy_analysis.png
```

**파일 용도 설명:**

1. **question_2_solution.ipynb** (Jupyter Notebook)
   - 대화형 분석 및 시각화에 최적
   - 코드 블록별로 실행하며 결과를 즉시 확인 가능
   - 마크다운으로 문서화와 코드를 함께 작성
   - 데이터 분석 과정을 단계별로 보여주기 좋음
   - **추천 사용처**: 데이터 탐색, 시각화, 프로토타이핑

2. **api_data_collector.py** (Python 스크립트)
   - API 호출 및 데이터 수집 자동화
   - 스케줄러나 배치 작업에 활용 가능
   - **추천 사용처**: 정기적인 데이터 수집

3. **data_processor.py** (Python 스크립트)
   - ETL 프로세스 자동화
   - 재사용 가능한 함수로 구성
   - **추천 사용처**: 데이터 전처리 파이프라인

4. **data_visualizer.py** (Python 스크립트)
   - 시각화 코드 모듈화
   - 여러 차트를 일괄 생성
   - **추천 사용처**: 보고서용 차트 자동 생성

**개발 순서 추천:**
1. Jupyter Notebook에서 프로토타이핑 및 탐색
2. 안정화된 코드를 Python 스크립트로 분리
3. 최종 분석 및 보고서는 Notebook에서 작성

---

## ⚠️ 고려해야 할 사항

### 1. API 선택 시 고려사항

- **데이터 접근성**: API 키 발급이 즉시 가능한지 확인
- **데이터 양**: 100건 이상 확보 가능한지 확인
- **데이터 구조**: JSON/XML 파싱이 용이한지 확인
- **API 제한**: 호출 횟수 제한(Rate Limit)이 있는지 확인

### 2. API 키 관리 (환경변수 사용)

**방법 1: .env 파일 사용 (권장)**

```python
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수에서 API 키 가져오기
API_KEY = os.getenv('SEOUL_API_KEY')

if not API_KEY:
    raise ValueError("API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
```

**방법 2: 시스템 환경변수 사용**

```python
import os
API_KEY = os.environ.get('SEOUL_API_KEY', 'default_key')
```

**중요 사항:**
- 절대 코드에 API 키를 직접 하드코딩하지 마세요
- `.env` 파일은 `.gitignore`에 추가하여 Git 저장소에 포함되지 않도록 설정
- `.env.example` 파일을 만들어 필요한 환경변수 형식을 공유

`.gitignore` 예시:
```
.env
knou/
__pycache__/
*.pyc
data/raw_data.json
```

### 3. 에러 처리

```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # HTTP 에러 체크
except requests.exceptions.RequestException as e:
    print(f"API 호출 실패: {e}")
```

### 4. 데이터 검증

- **null 값 처리**: `df.isnull().sum()` 으로 확인
- **중복 제거**: `df.drop_duplicates()`
- **데이터 타입 확인**: `df.dtypes`
- **이상치 탐지**: `df.describe()` 통계량 확인

### 5. 대안 API 추천

**Option 1: 기상청 단기예보 API**
- 장점: 시계열 데이터 분석 가능, 예측 vs 실제 비교
- 단점: 여러 지역/시간대 데이터 수집 필요 (100건 확보)

**Option 2: 국토교통부 아파트 실거래가 API**
- 장점: 부동산 시장 트렌드 분석 가능
- 단점: 특정 기간/지역 설정 필요, 데이터 구조 복잡

**Option 3: 서울시 대기질 정보 API**
- 장점: 환경 데이터, 시간대별 분석 가능
- 단점: 측정소가 적어 데이터 양 확보 어려움

### 6. 시각화 개선 팁

- 한글 폰트 설정: `plt.rc('font', family='Malgun Gothic')`
- 마이너스 기호 깨짐 방지: `plt.rc('axes', unicode_minus=False)`
- 컬러맵 선택: 데이터 특성에 맞는 색상 팔레트 사용
- 레이블 명확화: 축 제목, 범례, 단위 표시

### 7. 제출 시 포함 사항

1. **API 키 발급 과정 스크린샷** (문서화)
2. **전체 코드** (주석 포함)
3. **수집된 데이터 샘플** (CSV 파일)
4. **시각화 결과** (이미지 파일)
5. **인사이트 분석 보고서** (마크다운 또는 PDF)

### 8. 추가 점수를 위한 심화 내용

- 여러 날짜/시간대 데이터 수집 및 시계열 분석
- 지도 시각화 (folium 라이브러리 활용)
- 통계적 검증 (상관관계, 회귀분석)
- 데이터 자동 수집 스케줄러 구현

---

## 🚀 시작하기

> ⚠️ **참고**: 아래는 과제를 처음 시작할 때의 계획입니다.
> **실제 구현된 프로젝트**를 실행하려면 → [python-data-processing/README.md](../python-data-processing/README.md) 참고

### 1단계: 가상환경 활성화

```bash
# Windows
cd subjects\3-2\python-data-processing
knou\Scripts\activate

# 활성화 확인: 터미널에 (knou) 표시
```

### 2단계: 라이브러리 확인 및 설치

```bash
# 현재 설치된 라이브러리 확인
pip list

# 추가로 필요한 라이브러리만 설치
pip install matplotlib seaborn scipy jupyter
```

**설치된 라이브러리:**
- ✅ requests, pandas, python-dotenv, numpy (이미 설치됨)
- ➕ matplotlib, seaborn, scipy, jupyter (추가 설치)

### 3단계: 환경변수 설정

1. `subjects/3-2/python-data-processing/.env` 파일 생성
2. API 키 입력:
   ```
   SEOUL_API_KEY=your_api_key_here
   ```

### 4단계: Jupyter Notebook 실행

```bash
# Jupyter Notebook 서버 시작
jupyter notebook

# 브라우저에서 자동으로 열림
# question_2_solution.ipynb 파일 생성
```

### 5단계: 개발 시작

1. Notebook에서 단계별로 코드 작성 및 실행
2. 데이터 수집 → ETL → 시각화 순서로 진행
3. 각 단계마다 결과 확인 및 문서화
4. 최종 결과물을 CSV 및 이미지로 저장

---

## 📌 체크리스트

과제 제출 전 확인사항:

- [ ] 가상환경 활성화 및 라이브러리 설치 완료
- [ ] API 키 발급 및 .env 파일 설정
- [ ] 100건 이상 데이터 수집 완료
- [ ] ETL 과정 구현 (Extract, Transform, Load)
- [ ] CSV 파일 저장 완료
- [ ] 시각화 2개 이상 생성
- [ ] 인사이트 3가지 이상 도출
- [ ] 코드에 주석 및 설명 추가
- [ ] .env 파일이 .gitignore에 포함되어 있는지 확인
- [ ] Jupyter Notebook 또는 Python 스크립트 정리 완료