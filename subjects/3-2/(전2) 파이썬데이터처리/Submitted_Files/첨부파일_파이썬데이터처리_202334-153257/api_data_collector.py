"""
서울시 따릉이 대여소 마스터 정보 API 데이터 수집 스크립트
작성일: 2025-10-23
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
import requests

# UTF-8 출력 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class BikeStationCollector:
    """서울시 따릉이 대여소 데이터 수집 클래스"""

    def __init__(self):
        """초기화 및 환경변수 로드"""
        load_dotenv()
        self.api_key = os.getenv('SEOUL_API_KEY')

        if not self.api_key:
            raise ValueError("API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")

        self.base_url = "http://openapi.seoul.go.kr:8088"
        self.service_name = "bikeStationMaster"
        self.file_type = "json"

    def build_url(self, start_index=1, end_index=1000):
        """API 요청 URL 생성"""
        url = f"{self.base_url}/{self.api_key}/{self.file_type}/{self.service_name}/{start_index}/{end_index}/"
        return url

    def fetch_data(self, start_index=1, end_index=1000):
        """
        API에서 데이터 수집

        Args:
            start_index (int): 요청 시작 위치
            end_index (int): 요청 종료 위치

        Returns:
            dict: API 응답 데이터
        """
        url = self.build_url(start_index, end_index)
        print(f"API 요청 URL: {url}")
        print(f"데이터 수집 중... (Index: {start_index}-{end_index})")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # HTTP 에러 체크

            data = response.json()

            # 응답 확인 (bikeStationMaster 키 사용)
            if 'bikeStationMaster' in data:
                result = data['bikeStationMaster']

                # 에러 체크
                if 'RESULT' in result:
                    code = result['RESULT'].get('CODE')
                    message = result['RESULT'].get('MESSAGE')

                    if code == 'INFO-000':
                        print(f"✅ 데이터 수집 성공!")
                        print(f"   총 데이터 건수: {result.get('list_total_count', 0)}건")
                        print(f"   수집된 데이터: {len(result.get('row', []))}건")
                        return data
                    else:
                        print(f"⚠️ API 응답 에러 - CODE: {code}, MESSAGE: {message}")
                        return None
                else:
                    print("⚠️ RESULT 정보가 없습니다.")
                    return data
            else:
                print("⚠️ 예상하지 못한 응답 구조입니다.")
                print("응답 키:", list(data.keys()))
                return data

        except requests.exceptions.Timeout:
            print("❌ API 요청 시간 초과 (timeout)")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ API 호출 실패: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            return None

    def save_raw_data(self, data, filepath='data/raw_data.json'):
        """
        원본 데이터를 JSON 파일로 저장

        Args:
            data (dict): 저장할 데이터
            filepath (str): 저장 경로
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ JSON 파일 저장 완료: {filepath}")

    def collect_and_save(self, start_index=1, end_index=1000):
        """
        데이터 수집 및 저장 통합 메서드

        Args:
            start_index (int): 요청 시작 위치
            end_index (int): 요청 종료 위치

        Returns:
            dict: 수집된 데이터
        """
        print("=" * 60)
        print(f"📡 서울시 따릉이 대여소 데이터 수집 시작")
        print(f"⏰ 수집 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 데이터 수집
        data = self.fetch_data(start_index, end_index)

        if data:
            # 원본 데이터 저장
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f'data/raw_data_{timestamp}.json'
            self.save_raw_data(data, filepath)

            # 기본 파일에도 저장 (최신 데이터)
            self.save_raw_data(data, 'data/raw_data.json')

            print("=" * 60)
            print("✅ 데이터 수집 완료!")
            print("=" * 60)

            return data
        else:
            print("=" * 60)
            print("❌ 데이터 수집 실패")
            print("=" * 60)
            return None


def main():
    """메인 실행 함수"""
    try:
        collector = BikeStationCollector()

        # 데이터 수집 (최대 1000건)
        data = collector.collect_and_save(start_index=1, end_index=1000)

        if data and 'bikeStationMaster' in data:
            stations = data['bikeStationMaster'].get('row', [])

            if stations:
                print(f"\n📊 데이터 샘플 (첫 번째 대여소):")
                print(json.dumps(stations[0], ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
