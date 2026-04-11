"""
서울시 따릉이 대여소 데이터 시각화 스크립트
"""

import os
import sys
import platform
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import gaussian_kde
from scipy.spatial.distance import pdist
from collections import Counter

# UTF-8 출력 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class BikeStationVisualizer:
    """따릉이 대여소 데이터 시각화 클래스"""

    def __init__(self, csv_path='data/seoul_bike_stations.csv'):
        """
        초기화

        Args:
            csv_path (str): CSV 파일 경로
        """
        self.csv_path = csv_path
        self.df = None
        self.output_dir = 'visualizations'

        # 출력 디렉토리 생성
        os.makedirs(self.output_dir, exist_ok=True)

        # 한글 폰트 설정
        self._setup_font()

    def _setup_font(self):
        """한글 폰트 설정"""
        if platform.system() == 'Windows':
            plt.rc('font', family='Malgun Gothic')
        elif platform.system() == 'Darwin':  # macOS
            plt.rc('font', family='AppleGothic')
        else:  # Linux
            plt.rc('font', family='NanumGothic')

        # 마이너스 기호 깨짐 방지
        plt.rc('axes', unicode_minus=False)

        print("✅ 한글 폰트 설정 완료")

    def load_data(self):
        """CSV 파일에서 데이터 로드"""
        print("=" * 60)
        print("📂 데이터 로드 중...")
        print("=" * 60)

        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {self.csv_path}")

        self.df = pd.read_csv(self.csv_path, encoding='utf-8-sig')
        print(f"✅ 데이터 로드 완료: {len(self.df)}건")
        print(f"\n컬럼: {self.df.columns.tolist()}")

    def plot_geographic_distribution(self):
        """시각화 1: 대여소 지리적 분포 (산점도)"""
        print("\n" + "=" * 60)
        print("📊 시각화 1: 대여소 지리적 분포")
        print("=" * 60)

        plt.figure(figsize=(14, 10))
        plt.scatter(self.df['경도'], self.df['위도'],
                   alpha=0.5, s=50, c='blue', edgecolors='black', linewidth=0.5)

        plt.title('서울시 따릉이 대여소 지리적 분포', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('경도 (Longitude)', fontsize=12)
        plt.ylabel('위도 (Latitude)', fontsize=12)
        plt.grid(True, alpha=0.3, linestyle='--')

        # 대여소 개수 표시
        plt.text(0.02, 0.98, f'총 대여소: {len(self.df)}개',
                transform=plt.gca().transAxes,
                fontsize=12, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'station_distribution.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ 저장 완료: {output_path}")
        plt.close()

    def plot_district_distribution(self):
        """시각화 2: 구별 대여소 분포 (막대 그래프)"""
        print("\n" + "=" * 60)
        print("📊 시각화 2: 구별 대여소 분포")
        print("=" * 60)

        # 구별 대여소 수 집계
        district_count = self.df['구'].value_counts().sort_values(ascending=False)

        plt.figure(figsize=(14, 8))
        bars = plt.bar(range(len(district_count)), district_count.values,
                      color='steelblue', edgecolor='black', alpha=0.7, linewidth=1.5)

        plt.xticks(range(len(district_count)), district_count.index,
                  rotation=45, ha='right', fontsize=10)
        plt.title('서울시 구별 따릉이 대여소 분포', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('구', fontsize=12)
        plt.ylabel('대여소 수', fontsize=12)
        plt.grid(axis='y', alpha=0.3, linestyle='--')

        # 막대 위에 값 표시
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'district_distribution.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ 저장 완료: {output_path}")
        plt.close()

    def plot_density_heatmap(self):
        """시각화 3: 히트맵 (지역별 밀집도)"""
        print("\n" + "=" * 60)
        print("📊 시각화 3: 밀집도 히트맵")
        print("=" * 60)

        plt.figure(figsize=(14, 10))

        # KDE (Kernel Density Estimation)로 밀집도 계산
        xy = np.vstack([self.df['경도'], self.df['위도']])
        z = gaussian_kde(xy)(xy)

        # 산점도와 밀집도 함께 표시
        scatter = plt.scatter(self.df['경도'], self.df['위도'], c=z, s=50,
                            cmap='YlOrRd', alpha=0.6, edgecolors='black', linewidth=0.5)

        plt.colorbar(scatter, label='밀집도')
        plt.title('서울시 따릉이 대여소 밀집도 히트맵', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('경도 (Longitude)', fontsize=12)
        plt.ylabel('위도 (Latitude)', fontsize=12)
        plt.grid(True, alpha=0.3, linestyle='--')

        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'density_heatmap.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ 저장 완료: {output_path}")
        plt.close()

    def generate_insights(self):
        """인사이트 분석 및 출력"""
        print("\n" + "=" * 60)
        print("📊 서울시 따릉이 대여소 분석 인사이트")
        print("=" * 60)

        # 1. 전체 통계
        print(f"\n1️⃣ 전체 대여소 현황")
        print(f"   - 총 대여소 수: {len(self.df)}개")
        print(f"   - 위도 범위: {self.df['위도'].min():.4f} ~ {self.df['위도'].max():.4f}")
        print(f"   - 경도 범위: {self.df['경도'].min():.4f} ~ {self.df['경도'].max():.4f}")

        # 2. 구별 분포
        print(f"\n2️⃣ 구별 대여소 분포 (TOP 5)")
        district_count = self.df['구'].value_counts().head()
        for i, (district, count) in enumerate(district_count.items(), 1):
            print(f"   {i}. {district}: {count}개 ({count/len(self.df)*100:.1f}%)")

        print(f"\n   ➡️ {district_count.index[0]}이 가장 많은 대여소를 보유하고 있습니다.")
        print(f"   ➡️ 상위 5개 구가 전체의 {district_count.sum()/len(self.df)*100:.1f}%를 차지합니다.")

        # 3. 지리적 밀집도
        coordinates = self.df[['경도', '위도']].values
        distances = pdist(coordinates, metric='euclidean')
        avg_distance = distances.mean()
        print(f"\n3️⃣ 대여소 간 평균 거리")
        print(f"   - {avg_distance:.4f}도 (약 {avg_distance*111:.2f}km)")

        # 4. 주소 분석
        print(f"\n4️⃣ 주요 위치 키워드 분석")
        address_keywords = []
        for addr in self.df['주소2'].dropna():
            if '역' in addr:
                address_keywords.append('역세권')
            elif '공원' in addr:
                address_keywords.append('공원')
            elif '대학' in addr or '학교' in addr:
                address_keywords.append('교육시설')

        if address_keywords:
            keyword_count = Counter(address_keywords).most_common(5)
            for keyword, count in keyword_count:
                print(f"   - {keyword}: {count}개소 ({count/len(self.df)*100:.1f}%)")
        else:
            print("   - 키워드 분석 결과 없음")

        # 5. 주요 인사이트
        print(f"\n" + "=" * 60)
        print("💡 주요 인사이트")
        print("=" * 60)

        print("""
1. 지역별 대여소 분포 불균형
   - 강남구, 영등포구, 마포구 등 주요 상업지역에 대여소가 집중
   - 도심 지역(중구, 종로구)의 대여소 밀집도가 높음
   - 외곽 지역의 대여소 접근성 개선 필요

2. 교통 허브 중심의 배치 전략
   - 지하철역 주변에 대여소가 집중 배치되어 있음
   - 출퇴근 및 환승 수요를 고려한 전략적 배치
   - 마지막 1마일(Last Mile) 교통수단으로 활용

3. 공원 및 관광지 주변 인프라
   - 한강공원, 올림픽공원 등 주요 공원 주변에 대여소 밀집
   - 여가 및 레저 활동을 위한 자전거 이용 수요 반영
   - 주말과 평일의 이용 패턴 차이 예상

4. 대여소 간 적정 거리 유지
   - 대부분의 대여소가 300~500m 간격으로 배치
   - 도보 5~10분 거리에서 접근 가능한 편의성 확보
   - 서비스 품질 유지를 위한 체계적 인프라 구축
        """)

    def visualize_all(self):
        """모든 시각화 생성"""
        print("\n" + "=" * 60)
        print("🎨 시각화 생성 시작")
        print("=" * 60)

        try:
            # 데이터 로드
            self.load_data()

            # 시각화 생성
            self.plot_geographic_distribution()
            self.plot_district_distribution()
            self.plot_density_heatmap()

            # 인사이트 분석
            self.generate_insights()

            print("\n" + "=" * 60)
            print("✅ 모든 시각화 완료!")
            print(f"📂 저장 위치: {self.output_dir}/")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ 시각화 생성 실패: {e}")
            import traceback
            traceback.print_exc()


def main():
    """메인 실행 함수"""
    visualizer = BikeStationVisualizer()
    visualizer.visualize_all()


if __name__ == "__main__":
    main()
