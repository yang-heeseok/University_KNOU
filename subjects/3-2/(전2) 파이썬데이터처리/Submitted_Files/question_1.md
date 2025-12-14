# 웹 스크래핑 과제 해결 가이드

## 과제 개요
네이버 뉴스에서 특정 키워드 관련 기사를 수집하고 분석하는 프로젝트

---

## 1단계: 환경 설정

### 가상환경 생성 (권장)
라이브러리 충돌을 방지하기 위해 가상환경 사용을 권장합니다.

#### Windows
```bash
# 1. 가상환경 생성
python -m venv knou

# 2. 가상환경 활성화
knou\Scripts\activate

# 3. 가상환경 비활성화 (작업 종료 시)
deactivate
```

#### macOS/Linux
```bash
# 1. 가상환경 생성
python3 -m venv knou

# 2. 가상환경 활성화
source knou/bin/activate

# 3. 가상환경 비활성화 (작업 종료 시)
deactivate
```

**가상환경 활성화 확인**
- 터미널 프롬프트 앞에 `(knou)` 표시가 나타남
- `which python` (macOS/Linux) 또는 `where python` (Windows)로 경로 확인

### 필요한 라이브러리 설치
가상환경이 활성화된 상태에서 설치합니다.

```bash
pip install requests beautifulsoup4 pandas selenium webdriver-manager konlpy
```

**설치 확인**
```bash
pip list
```

### 라이브러리 선택
- **BeautifulSoup**: 정적 페이지 스크래핑에 적합, 빠르고 간단
- **Selenium**: 동적 페이지(JavaScript 렌더링)에 필요

네이버 뉴스는 검색 결과 페이지가 동적으로 로드되므로 **Selenium 권장**

---

## 2단계: 데이터 수집 전략

### 키워드 선택
예시: "인공지능", "기후변화", "반도체" 등 뉴스가 많은 키워드 선택

### 네이버 뉴스 검색 URL 구조
```
https://search.naver.com/search.naver?where=news&query={키워드}&sm=tab_opt&sort=1&photo=0&field=0&pd=3&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:dd,p:1w
```

주요 파라미터:
- `query`: 검색 키워드
- `sort=1`: 최신순 정렬
- `nso=so:dd,p:1w`: 최근 1주일

### 수집할 데이터
1. 기사 제목 (title)
2. 게시 날짜 (date)
3. 언론사 (press)
4. 요약문 (summary) - 있는 경우

---

## 3단계: 스크래핑 구현

### 기본 구조
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

# 1. 드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 2. 검색 페이지 접근
keyword = "인공지능"
url = f"https://search.naver.com/search.naver?where=news&query={keyword}&nso=so:dd,p:1w"
driver.get(url)

# 3. 페이지 로딩 대기
time.sleep(2)

# 4. HTML 파싱
soup = BeautifulSoup(driver.page_source, 'html.parser')

# 5. 데이터 추출
articles = []
# 기사 요소 찾기 및 데이터 추출 로직
```

### 페이지네이션 처리
50건 이상 수집을 위해 여러 페이지 순회 필요
```python
for page in range(1, 6):  # 5페이지까지
    # 페이지 이동
    # 데이터 수집
    # 다음 페이지 버튼 클릭
```

### HTML 구조 분석 팁
1. 브라우저 개발자 도구(F12)로 HTML 구조 확인
2. 기사 목록의 CSS 클래스/태그 찾기
3. 제목, 날짜, 언론사, 요약문의 선택자 파악

---

## 4단계: 데이터 처리 및 저장

### DataFrame 생성
```python
import pandas as pd

df = pd.DataFrame(articles, columns=['제목', '날짜', '언론사', '요약문'])

# 데이터 확인
print(df.head())
print(f"총 수집 기사 수: {len(df)}")
```

### 데이터 전처리
```python
# 날짜 형식 통일 (예: "1시간 전" -> 날짜 형식으로 변환)
# 중복 제거
df = df.drop_duplicates(subset=['제목'])

# 결측치 처리
df['요약문'] = df['요약문'].fillna('')
```

### CSV 저장
```python
df.to_csv('news_data.csv', index=False, encoding='utf-8-sig')
```
*encoding='utf-8-sig'는 한글이 깨지지 않도록 BOM 추가*

---

## 5단계: 데이터 분석

### 1) 일자별 기사 수 집계
```python
# 날짜 형식 변환
df['날짜'] = pd.to_datetime(df['날짜'])

# 일자별 집계
daily_count = df.groupby(df['날짜'].dt.date).size()
print(daily_count)

# 시각화 (선택사항)
import matplotlib.pyplot as plt
plt.rc('font', family='Malgun Gothic')  # 한글 폰트
daily_count.plot(kind='bar')
plt.title('일자별 기사 수')
plt.show()
```

### 2) 언론사별 기사 수 TOP 10
```python
press_count = df['언론사'].value_counts().head(10)
print(press_count)
```

### 3) 제목에서 가장 많이 등장한 단어 TOP 20
```python
from collections import Counter
from konlpy.tag import Okt

okt = Okt()

# 모든 제목 합치기
all_titles = ' '.join(df['제목'].tolist())

# 형태소 분석 (명사만 추출)
nouns = okt.nouns(all_titles)

# 불용어 제거
stopwords = ['것', '등', '및', '수', '년', '월', '일', '때', '개', '명']
filtered_nouns = [word for word in nouns if word not in stopwords and len(word) > 1]

# 빈도 계산
word_count = Counter(filtered_nouns)
top20 = word_count.most_common(20)

print(top20)
```

---

## 6단계: 코드 정리 및 문서화

### 최종 코드 구조
```
1. 라이브러리 임포트
2. 설정 변수 (키워드, 수집 기간 등)
3. 스크래핑 함수 정의
4. 데이터 수집 실행
5. 데이터 전처리
6. CSV 저장
7. 분석 및 시각화
```

### 주석 및 설명 추가
각 단계마다 무엇을 하는지 주석으로 설명

---

## 주의사항

### 법적/윤리적 고려사항
- robots.txt 확인
- 과도한 요청 방지 (time.sleep() 활용)
- 학술 목적임을 명시

### 기술적 팁
1. **에러 처리**: try-except로 예외 상황 대비
2. **대기 시간**: 페이지 로딩 충분히 대기
3. **User-Agent 설정**: 봇 차단 방지
4. **데이터 검증**: 수집 후 데이터 확인

### 디버깅
- 작은 단위로 테스트 (먼저 1페이지만 수집)
- print()로 중간 결과 확인
- 브라우저 창을 닫지 않고 확인 (headless=False)

---

## 체크리스트

- [ ] 가상환경 생성 및 활성화
- [ ] 라이브러리 설치 완료
- [ ] 키워드 선정
- [ ] 네이버 뉴스 HTML 구조 분석
- [ ] 스크래핑 코드 작성
- [ ] 50건 이상 데이터 수집
- [ ] DataFrame 생성 및 확인
- [ ] CSV 파일 저장
- [ ] 일자별 집계
- [ ] 언론사별 TOP 10
- [ ] 단어 빈도 TOP 20
- [ ] 코드 주석 및 설명 추가
- [ ] 최종 보고서 작성

---

## 추가 개선 아이디어

1. 기사 본문까지 수집하여 더 깊이 있는 분석
2. 워드클라우드로 시각화
3. 감성 분석 (긍정/부정 분류)
4. 시계열 트렌드 분석
