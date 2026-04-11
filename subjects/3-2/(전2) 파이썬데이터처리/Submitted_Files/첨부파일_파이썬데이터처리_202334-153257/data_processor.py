"""
서울시 따릉이 대여소 데이터 ETL 처리 스크립트
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime

# UTF-8 출력 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class BikeStationProcessor:
    """따릉이 대여소 데이터 ETL 처리 클래스"""

    def __init__(self, raw_data_path='data/raw_data.json'):
        """
        초기화

        Args:
            raw_data_path (str): 원본 JSON 파일 경로
        """
        self.raw_data_path = raw_data_path
        self.df = None

    def extract(self):
        """
        Extract: JSON 파일에서 데이터 추출

        Returns:
            list: 추출된 대여소 데이터 리스트
        """
        print("=" * 60)
        print("📤 EXTRACT: 원본 데이터 추출 중...")
        print("=" * 60)

        if not os.path.exists(self.raw_data_path):
            raise FileNotFoundError(f"원본 데이터 파일을 찾을 수 없습니다: {self.raw_data_path}")

        with open(self.raw_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'bikeStationMaster' in data:
            raw_data = data['bikeStationMaster']['row']
            print(f"✅ 추출된 데이터: {len(raw_data)}건")

            # 데이터 샘플 출력
            if raw_data:
                print(f"\n첫 번째 데이터 샘플:")
                print(json.dumps(raw_data[0], ensure_ascii=False, indent=2))

            return raw_data
        else:
            raise ValueError("예상하지 못한 데이터 구조입니다.")

    def transform(self, raw_data):
        """
        Transform: 데이터 변환 및 정제

        Args:
            raw_data (list): 원본 데이터

        Returns:
            pd.DataFrame: 변환된 DataFrame
        """
        print("\n" + "=" * 60)
        print("🔄 TRANSFORM: 데이터 변환 및 정제 중...")
        print("=" * 60)

        # DataFrame 생성
        df = pd.DataFrame(raw_data)

        print(f"\n📊 원본 데이터 정보:")
        print(f"   - 전체 컬럼: {df.columns.tolist()}")
        print(f"   - 전체 행 수: {len(df)}")
        print(f"\n데이터 타입:\n{df.dtypes}")

        # 필요한 컬럼만 선택
        required_columns = ['RNTLS_ID', 'ADDR1', 'ADDR2', 'LAT', 'LOT']

        # 컬럼 존재 확인
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            print(f"⚠️ 누락된 컬럼: {missing_cols}")
            print(f"사용 가능한 컬럼: {df.columns.tolist()}")

        # 컬럼 선택
        df = df[required_columns].copy()

        # 컬럼명 한글로 변경
        df.columns = ['대여소ID', '주소1', '주소2', '위도', '경도']

        print(f"\n✅ 선택된 컬럼: {df.columns.tolist()}")

        # 데이터 타입 변환
        print(f"\n🔧 데이터 타입 변환 중...")
        df['위도'] = pd.to_numeric(df['위도'], errors='coerce')
        df['경도'] = pd.to_numeric(df['경도'], errors='coerce')

        print(f"   - 위도/경도를 숫자형으로 변환")

        # 결측치 확인
        print(f"\n📋 결측치 확인:")
        null_counts = df.isnull().sum()
        for col, count in null_counts.items():
            if count > 0:
                print(f"   - {col}: {count}건 ({count/len(df)*100:.1f}%)")

        # 결측치 제거
        initial_count = len(df)
        df = df.dropna(subset=['위도', '경도'])
        removed_count = initial_count - len(df)

        if removed_count > 0:
            print(f"\n⚠️ 위도/경도 결측치 제거: {removed_count}건")

        # 이상치 처리 (서울 지역 범위)
        print(f"\n🔍 이상치 처리 중...")
        print(f"   - 서울 지역 위도 범위: 37.4 ~ 37.7")
        print(f"   - 서울 지역 경도 범위: 126.7 ~ 127.2")

        initial_count = len(df)
        df = df[(df['위도'] >= 37.4) & (df['위도'] <= 37.7)]
        df = df[(df['경도'] >= 126.7) & (df['경도'] <= 127.2)]
        removed_count = initial_count - len(df)

        if removed_count > 0:
            print(f"⚠️ 범위 밖 데이터 제거: {removed_count}건")

        # 중복 제거
        initial_count = len(df)
        df = df.drop_duplicates(subset=['대여소ID'])
        removed_count = initial_count - len(df)

        if removed_count > 0:
            print(f"⚠️ 중복 데이터 제거: {removed_count}건")

        # 구 정보 추출
        print(f"\n🏘️ 구 정보 추출 중...")
        df['구'] = df['주소1'].str.extract(r'(.*?구)')[0]

        print(f"\n✅ 전처리 완료!")
        print(f"   - 최종 데이터: {len(df)}건")
        print(f"\n기술 통계:")
        print(df[['위도', '경도']].describe())

        return df

    def load(self, df, csv_path='data/seoul_bike_stations.csv'):
        """
        Load: 정제된 데이터를 CSV 파일로 저장

        Args:
            df (pd.DataFrame): 정제된 DataFrame
            csv_path (str): CSV 저장 경로
        """
        print("\n" + "=" * 60)
        print("💾 LOAD: 데이터 저장 중...")
        print("=" * 60)

        # 디렉토리 생성
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        # CSV 저장
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"✅ CSV 파일 저장 완료: {csv_path}")

        # 타임스탬프 포함 백업 파일 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'data/seoul_bike_stations_{timestamp}.csv'
        df.to_csv(backup_path, index=False, encoding='utf-8-sig')
        print(f"✅ 백업 파일 저장 완료: {backup_path}")

        # 데이터 미리보기
        print(f"\n📊 저장된 데이터 샘플 (처음 5개):")
        print(df.head().to_string())

        # 구별 통계
        print(f"\n📈 구별 대여소 분포:")
        district_counts = df['구'].value_counts()
        for district, count in district_counts.head(10).items():
            print(f"   - {district}: {count}개")

    def process(self):
        """ETL 전체 프로세스 실행"""
        print("\n" + "=" * 60)
        print("🚀 ETL 프로세스 시작")
        print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        try:
            # Extract
            raw_data = self.extract()

            # Transform
            self.df = self.transform(raw_data)

            # Load
            self.load(self.df)

            print("\n" + "=" * 60)
            print("✅ ETL 프로세스 완료!")
            print(f"⏰ 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)

            return self.df

        except Exception as e:
            print(f"\n❌ ETL 프로세스 실패: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """메인 실행 함수"""
    processor = BikeStationProcessor()
    df = processor.process()

    if df is not None:
        print(f"\n✅ 처리 완료! DataFrame이 준비되었습니다.")
        print(f"   - 총 {len(df)}개의 대여소 데이터")
        print(f"   - CSV 파일: data/seoul_bike_stations.csv")


if __name__ == "__main__":
    main()
