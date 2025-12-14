# student_id = "202334-153257"
# print(student_id)




""" 파이썬에서 “2025년 9월 8일”은 무슨 요일인지 계산하는 코드를 간단히 작성해줘. """
# import datetime
# target_date = datetime.date(2025, 9, 8)
# days = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
# day_name = days[target_date.weekday()]
# print(f"2025년 9월 8일은 {day_name}입니다.")




""" 파이썬으로 1부터 10까지 자연수를 순서대로 출력하되, 3의 배수는 건너뛰는 프로그램을 while문 사용해서 작성해줘 """
# i = 1
# while i <= 10:
#     if i % 3 == 0:
#         i += 1
#         continue
#     print(i)
#     i += 1 





r""" 
C:\project\airtown\University_KNOU\subjects\3-2(전2) 파이썬과R\Provided_Files\iris.txt
파이썬으로 iris.txt 파일을 iris_all 이라는 이름의 데이터 프레임으로 입력
 Ÿ iris_all의 첫 5행만 iris_5 라는 이름의 데이터 프레임으로 저장
 Ÿ iris_all의 마지막 행을 iris_5의 세 번째 행의 위치에 끼워 넣어 iris_6이라는 데이터 프레임 을 생성 
 Ÿ iris_6를 행 번호를 유지하면서 UTF-8 인코딩으로 iris_6.csv 라는 이름의 파일로 저장 
"""

import csv

# 1. iris.txt 파일을 읽기
# CSV 파일은 보통 리스트의 리스트(list of lists) 형태로 데이터를 다룹니다.
file_path = r'C:\project\airtown\University_KNOU\subjects\3-2\(전2) 파이썬과R\Provided_Files\iris.txt'

header = []
data_rows = []
with open(file_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)  # 첫 줄(헤더)을 읽음
    for row in reader:
        data_rows.append(row) # 나머지 데이터 행들을 리스트에 추가

# 2. 첫 5행만 저장
iris_5_rows = data_rows[:5]
print("--- iris_5 (리스트 형태) ---")
print(iris_5_rows)

# 3. 마지막 행을 세 번째 위치에 끼워 넣기
last_row = data_rows[-1]
iris_6_rows = iris_5_rows[:2] + [last_row] + iris_5_rows[2:]
print("\n--- iris_6 (리스트 형태) ---")
print(iris_6_rows)

# 4. iris_6.csv 파일로 저장
output_filepath = r'subjects\3-2\(전2) 파이썬과R\Provided_Files\iris_6.csv'
with open(output_filepath, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(header)      # 헤더 쓰기
    writer.writerows(iris_6_rows) # 데이터 행들 쓰기

print(f"\n'{output_filepath}' 파일이 생성되었습니다.")
