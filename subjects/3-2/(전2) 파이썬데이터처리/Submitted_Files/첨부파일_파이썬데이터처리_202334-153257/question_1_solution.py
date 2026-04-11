"""
네이버 뉴스 스크래핑 프로그램
과제: 특정 키워드 관련 뉴스 기사 수집 및 분석
"""

import sys
import io

# UTF-8 출력 설정 (Windows 한글 깨짐 방지)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import re
import pandas as pd
from collections import Counter

# ============================================
# 1단계: 설정 변수
# ============================================

# 검색할 키워드 설정
KEYWORD = "인공지능"

# 수집할 기사 목표 개수
TARGET_ARTICLE_COUNT = 50

# 페이지 대기 시간 (초)
WAIT_TIME = 2


# ============================================
# 2단계: 네이버 뉴스 검색 URL 생성
# ============================================

def get_naver_news_url(keyword, page=1):
    """
    네이버 뉴스 검색 URL 생성

    Args:
        keyword (str): 검색 키워드
        page (int): 페이지 번호 (1부터 시작)

    Returns:
        str: 네이버 뉴스 검색 URL
    """
    base_url = "https://search.naver.com/search.naver"
    params = {
        "where": "news",           # 뉴스 검색
        "query": keyword,          # 검색어
        "sm": "tab_opt",
        "sort": "1",               # 최신순 정렬 (0: 관련도순, 1: 최신순)
        "photo": "0",
        "field": "0",
        "pd": "3",                 # 기간 설정
        "ds": "",
        "de": "",
        "docid": "",
        "related": "0",
        "mynews": "0",
        "office_type": "0",
        "office_section_code": "0",
        "news_office_checked": "",
        "nso": "so:dd,p:1w",       # 최신순(so:dd), 최근 1주일(p:1w)
        "start": (page - 1) * 10 + 1  # 페이지네이션
    }

    # URL 파라미터 조합
    param_str = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{param_str}"


# ============================================
# 3단계: 스크래핑 함수
# ============================================

def setup_driver():
    """
    Selenium 웹드라이버 설정

    Returns:
        webdriver: 설정된 Chrome 웹드라이버
    """
    print("웹드라이버 설정 중...")

    # Chrome 옵션 설정
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # 브라우저 창 숨기기 (디버깅 시 주석 처리)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    # User-Agent 설정 (봇 차단 방지)
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # 웹드라이버 생성
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    print("웹드라이버 설정 완료!")
    return driver


def parse_relative_date(date_str):
    """
    상대 시간 표현을 날짜로 변환
    예: "1시간 전" -> 2025-10-22 10:00:00

    Args:
        date_str (str): 상대 시간 문자열

    Returns:
        str: 변환된 날짜 문자열 (YYYY-MM-DD HH:MM:SS)
    """
    now = datetime.now()

    # "N시간 전"
    if "시간" in date_str:
        hours = int(re.findall(r'\d+', date_str)[0])
        return (now - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')

    # "N분 전"
    elif "분" in date_str:
        minutes = int(re.findall(r'\d+', date_str)[0])
        return (now - timedelta(minutes=minutes)).strftime('%Y-%m-%d %H:%M:%S')

    # "N일 전"
    elif "일" in date_str:
        days = int(re.findall(r'\d+', date_str)[0])
        return (now - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

    # 이미 날짜 형식인 경우
    else:
        return date_str


def scrape_news_page(driver, url):
    """
    한 페이지의 뉴스 기사 정보 수집

    Args:
        driver: Selenium 웹드라이버
        url (str): 수집할 페이지 URL

    Returns:
        list: 기사 정보 리스트
    """
    print(f"페이지 접근 중: {url}")
    driver.get(url)

    # 페이지 로딩 대기
    time.sleep(WAIT_TIME)

    # HTML 파싱
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    articles = []

    # 네이버 뉴스 새로운 구조 (2025년 기준)
    news_items = soup.select('div.IgJMhH4Xrhuw6jctOE_e')

    print(f"발견된 기사 수: {len(news_items)}")

    # 디버깅: 페이지 구조 확인 (항상 첫 페이지는 저장)
    if url.endswith("start=1"):
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("  ! debug_page.html 파일로 저장됨.")

    if len(news_items) == 0:
        print("  ! 기사를 찾을 수 없습니다. HTML 구조 확인 필요.")

    for item in news_items:
        try:
            # 제목 - 새로운 구조
            title_elem = item.select_one('span.sds-comps-text-type-headline1')
            title = title_elem.get_text(strip=True) if title_elem else ""

            # 언론사 - 프로필 영역에서 추출
            press_elem = item.select_one('div.sds-comps-profile-info-title a span.sds-comps-text-ellipsis-1')
            press = press_elem.get_text(strip=True) if press_elem else ""

            # 날짜 - 프로필 subtext에서 추출
            date_elem = item.select_one('span.sds-comps-profile-info-subtext span.sds-comps-text-type-body2')
            date = date_elem.get_text(strip=True) if date_elem else ""

            # 상대 시간을 날짜로 변환
            if date:
                date = parse_relative_date(date)

            # 요약문 - body1 텍스트
            summary_elem = item.select_one('span.sds-comps-text-ellipsis-3.sds-comps-text-type-body1')
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            # <mark> 태그 제거
            summary = summary.replace('<mark>', '').replace('</mark>', '')

            # 기사 정보 저장
            if title:
                article = {
                    '제목': title,
                    '날짜': date,
                    '언론사': press,
                    '요약문': summary
                }
                articles.append(article)
                print(f"  - 수집: {title[:30]}...")

        except Exception as e:
            print(f"  ! 기사 파싱 오류: {e}")
            continue

    return articles


def collect_news(keyword, target_count=50, max_pages=10):
    """
    뉴스 기사 수집 메인 함수

    Args:
        keyword (str): 검색 키워드
        target_count (int): 목표 수집 개수
        max_pages (int): 최대 페이지 수

    Returns:
        list: 수집된 기사 리스트
    """
    separator = "=" * 60
    print(f"\n{separator}")
    print(f"뉴스 수집 시작")
    print(f"키워드: {keyword}")
    print(f"목표 개수: {target_count}개")
    print(f"{separator}\n")

    driver = setup_driver()
    all_articles = []

    try:
        page = 1
        while len(all_articles) < target_count and page <= max_pages:
            print(f"\n[페이지 {page}/{max_pages}]")

            # URL 생성
            url = get_naver_news_url(keyword, page)

            # 기사 수집
            articles = scrape_news_page(driver, url)
            all_articles.extend(articles)

            print(f"현재까지 수집된 기사: {len(all_articles)}개")

            # 목표 달성 확인
            if len(all_articles) >= target_count:
                print(f"\n목표 달성! 총 {len(all_articles)}개 수집 완료")
                break

            page += 1
            time.sleep(WAIT_TIME)

    except Exception as e:
        print(f"\n오류 발생: {e}")

    finally:
        driver.quit()
        print("\n웹드라이버 종료")

    return all_articles


# ============================================
# 4단계: 데이터 처리 및 저장
# ============================================

def save_to_dataframe(articles):
    """
    수집된 기사를 DataFrame으로 변환 및 CSV 저장

    Args:
        articles (list): 수집된 기사 리스트

    Returns:
        DataFrame: 변환된 DataFrame
    """
    print(f"\n{'=' * 60}")
    print("데이터 처리 중...")
    print(f"{'=' * 60}\n")

    # DataFrame 생성
    df = pd.DataFrame(articles)

    # 데이터 확인
    print(f"총 수집 기사 수: {len(df)}개")
    print(f"\n[데이터 구조]")
    print(df.info())

    # 중복 제거
    before_count = len(df)
    df = df.drop_duplicates(subset=['제목'])
    after_count = len(df)
    if before_count != after_count:
        print(f"\n중복 제거: {before_count - after_count}개 제거됨")

    # 결측치 처리
    df['요약문'] = df['요약문'].fillna('')

    # 날짜 형식 변환 (문자열을 datetime으로)
    try:
        df['날짜'] = pd.to_datetime(df['날짜'])
        df['날짜_문자열'] = df['날짜'].dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"날짜 변환 경고: {e}")
        df['날짜_문자열'] = df['날짜']

    # CSV 저장
    csv_filename = f'news_data_{KEYWORD}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    print(f"\n✓ CSV 파일 저장 완료: {csv_filename}")

    return df


# ============================================
# 5단계: 데이터 분석
# ============================================

def analyze_data(df):
    """
    수집된 데이터 분석

    Args:
        df (DataFrame): 분석할 DataFrame
    """
    print(f"\n{'=' * 60}")
    print("데이터 분석")
    print(f"{'=' * 60}\n")

    analysis_results = {}

    # 1. 일자별 기사 수 집계
    print("[1] 일자별 기사 수 집계")
    print("-" * 40)
    try:
        daily_count = df.groupby(df['날짜'].dt.date).size().sort_index()
        print(daily_count)
        print(f"\n총 {len(daily_count)}일간의 기사")

        # DataFrame으로 변환
        daily_df = pd.DataFrame({
            '날짜': daily_count.index,
            '기사수': daily_count.values
        })
        analysis_results['일자별_기사수'] = daily_df
    except Exception as e:
        print(f"일자별 집계 오류: {e}")
        # 날짜 파싱이 실패한 경우 텍스트 그룹화 시도
        daily_count = df.groupby('날짜').size()
        daily_df = pd.DataFrame({
            '날짜': daily_count.index,
            '기사수': daily_count.values
        })
        analysis_results['일자별_기사수'] = daily_df
        print(daily_count.head(10))

    # 2. 언론사별 기사 수 TOP 10
    print(f"\n[2] 언론사별 기사 수 TOP 10")
    print("-" * 40)
    press_count = df['언론사'].value_counts().head(10)
    for i, (press, count) in enumerate(press_count.items(), 1):
        print(f"{i:2d}. {press:20s} : {count}개")

    # DataFrame으로 변환
    press_df = pd.DataFrame({
        '순위': range(1, len(press_count) + 1),
        '언론사': press_count.index,
        '기사수': press_count.values
    })
    analysis_results['언론사별_TOP10'] = press_df

    # 3. 제목에서 가장 많이 등장한 단어 TOP 20
    print(f"\n[3] 제목에서 가장 많이 등장한 단어 TOP 20")
    print("-" * 40)

    # 모든 제목 합치기
    all_titles = ' '.join(df['제목'].tolist())

    # 간단한 단어 추출 (한글만)
    import re
    # 한글 2글자 이상 추출
    words = re.findall(r'[가-힣]{2,}', all_titles)

    # 불용어 제거
    stopwords = ['것', '등', '및', '수', '년', '월', '일', '때', '개', '명',
                 '있는', '하는', '되는', '있다', '한다', '이다', '그', '저',
                 '위한', '통해', '대한', '관련', '지난']
    filtered_words = [word for word in words if word not in stopwords]

    # 빈도 계산
    word_count = Counter(filtered_words)
    top20 = word_count.most_common(20)

    for i, (word, count) in enumerate(top20, 1):
        print(f"{i:2d}. {word:10s} : {count}회")

    # DataFrame으로 변환
    word_df = pd.DataFrame({
        '순위': range(1, len(top20) + 1),
        '단어': [word for word, count in top20],
        '출현횟수': [count for word, count in top20]
    })
    analysis_results['단어빈도_TOP20'] = word_df

    # 분석 결과를 하나의 CSV로 저장
    csv_filename = f'news_analysis_{KEYWORD}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    # 3개의 분석 결과를 하나의 CSV에 저장 (구분선으로 분리)
    with open(csv_filename, 'w', encoding='utf-8-sig', newline='') as f:
        # 1. 일자별 기사 수
        f.write("=== 일자별 기사 수 집계 ===\n")
        analysis_results['일자별_기사수'].to_csv(f, index=False)
        f.write("\n")

        # 2. 언론사별 TOP 10
        f.write("=== 언론사별 기사 수 TOP 10 ===\n")
        analysis_results['언론사별_TOP10'].to_csv(f, index=False)
        f.write("\n")

        # 3. 단어 빈도 TOP 20
        f.write("=== 제목 단어 빈도 TOP 20 (불용어 제외) ===\n")
        analysis_results['단어빈도_TOP20'].to_csv(f, index=False)

    print(f"\n✓ 분석 결과 CSV 파일 저장 완료: {csv_filename}")

    print(f"\n{'=' * 60}")
    print("분석 완료!")
    print(f"{'=' * 60}\n")

    return analysis_results


# ============================================
# 메인 실행
# ============================================

if __name__ == "__main__":
    # 뉴스 수집
    articles = collect_news(KEYWORD, TARGET_ARTICLE_COUNT)

    separator = "=" * 60
    print(f"\n{separator}")
    print(f"수집 완료!")
    print(f"총 수집 기사 수: {len(articles)}개")
    print(f"{separator}\n")

    # 수집된 데이터 미리보기
    if articles:
        print("\n[수집된 데이터 미리보기]")
        for i, article in enumerate(articles[:3], 1):
            print(f"\n{i}. 제목: {article['제목']}")
            print(f"   언론사: {article['언론사']}")
            print(f"   날짜: {article['날짜']}")
            summary = article['요약문'][:50] + "..." if len(article['요약문']) > 50 else article['요약문']
            print(f"   요약: {summary}")

        # DataFrame 생성 및 CSV 저장
        df = save_to_dataframe(articles)

        # 데이터 분석
        analyze_data(df)
    else:
        print("수집된 기사가 없습니다.")
