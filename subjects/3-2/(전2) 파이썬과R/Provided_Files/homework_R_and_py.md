# 파이썬과 R 과제

## 1. 각 언어 환경에서 “학번: 202334-153257”을 출력하시오.

### (1) 파이썬 (3점)

#### 코드
```python
student_id = "202334-153257"
print(f"학번: {student_id}")
```

#### 실행 결과
```
학번: 202334-153257
```

---

### (2) R (3점)

#### 코드
```R
student_id <- "202334-153257"
print(paste("학번:", student_id))
```

#### 실행 결과
```
[1] "학번: 202334-153257"
```

---

## 2. 각 언어 환경에서 “2025년 9월 8일”은 무슨 요일인지 계산하시오.

### (1) 파이썬 (3점)

#### 코드
```python
import datetime

# 날짜 객체 생성
target_date = datetime.date(2025, 9, 8)

# 요일 계산 (0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일)
weekday_num = target_date.weekday()

# 요일 이름 리스트
days = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

print(f"2025년 9월 8일은 {days[weekday_num]}입니다.")
```

#### 실행 결과
```
2025년 9월 8일은 월요일입니다.
```

---

### (2) R (3점)

#### 코드
```R
# 날짜 객체 생성
target_date <- as.Date("2025-09-08")

# 요일 계산
day_of_week <- weekdays(target_date)

print(paste("2025년 9월 8일은", day_of_week, "입니다."))
```

#### 실행 결과
```
[1] "2025년 9월 8일은 월요일 입니다."
```

---

## 3. 각 언어 환경에서 1부터 10까지 자연수를 순서대로 출력하되, 3의 배수는 건너뛰는 프로그램을 작성하고 수행한 결과를 보이시오 (while문 사용).

### (1) 파이썬 (3점)

#### 코드
```python
i = 1
while i <= 10:
    # 3의 배수인지 확인
    if i % 3 == 0:
        i += 1
        continue  # 다음 반복으로 건너뜀
    
    print(i)
    i += 1
```

#### 실행 결과
```
1
2
4
5
7
8
10
```

---

### (2) R (3점)

#### 코드
```R
i <- 1
while (i <= 10) {
  # 3의 배수인지 확인
  if (i %% 3 == 0) {
    i <- i + 1
    next  # 다음 반복으로 건너뜀
  }
  
  print(i)
  i <- i + 1
}
```

#### 실행 결과
```
[1] 1
[1] 2
[1] 4
[1] 5
[1] 7
[1] 8
[1] 10
```

---

## 4. 각 언어 환경에서 다음 과정을 수행하는 프로그램을 작성하고 그 결과를 보이시오.

> **사전 준비**: 과제 폴더 내에 주어진 `iris.txt` 파일을 사용합니다. 코드에서는 상대 경로를 사용하여 파일을 불러옵니다.
> - **파일 위치**: `2025학년도 2학기 파이썬과R 출석수업 과제물/iris.txt`

### (1) 파이썬 (6점)

#### 코드
```python
import pandas as pd
import os

# iris.txt 파일 경로 (상대 경로)
file_path = os.path.join('2025학년도 2학기 파이썬과R 출석수업 과제물', 'iris.txt')

# iris.txt 파일을 iris_all 이라는 이름의 데이터 프레임으로 입력
iris_all = pd.read_csv(file_path)

# iris_all의 첫 5행만 iris_5 라는 이름의 데이터 프레임으로 저장
# .copy()를 사용하여 복사본을 만듭니다.
iris_5 = iris_all.head(5).copy()

# iris_all의 마지막 행을 가져옴
last_row = iris_all.tail(1)

# iris_5를 두 부분으로 나눔 (세 번째 행 위치에 끼워넣기 위해)
top_part = iris_5.iloc[:2]
bottom_part = iris_5.iloc[2:]

# 마지막 행을 끼워 넣어 iris_6 생성
iris_6 = pd.concat([top_part, last_row, bottom_part]).reset_index(drop=True)

# iris_6를 행 번호를 유지하면서 UTF-8 인코딩으로 iris_6.csv 라는 이름의 파일로 저장
# index=True로 행 번호를 파일에 포함시킵니다.
iris_6.to_csv('iris_6.csv', index=True, encoding='utf-8-sig')

print("iris_6.csv 파일이 생성되었습니다.")
print("\n생성된 iris_6 데이터 프레임 내용:")
print(iris_6)
```

#### 실행 결과
```
iris_6.csv 파일이 생성되었습니다.

생성된 iris_6 데이터 프레임 내용:
   Sepal.Length  Sepal.Width  Petal.Length  Petal.Width     Species
0           5.1          3.5           1.4          0.2      setosa
1           4.9          3.0           1.4          0.2      setosa
2           5.9          3.0           5.1          1.8   virginica
3           4.7          3.2           1.3          0.2      setosa
4           4.6          3.1           1.5          0.2      setosa
5           5.0          3.6           1.4          0.2      setosa
```
> `iris_6.csv` 파일을 엑셀로 열면 행 번호(0부터 5)가 포함된 6행의 데이터가 정상적으로 표시됩니다.

---

### (2) R (6점)

#### 코드
```R
library(here)

# iris.txt 파일 경로 (상대 경로)
# here() 함수는 현재 R 프로젝트 또는 스크립트 위치를 기준으로 경로를 생성합니다.
file_path <- here("2025학년도 2학기 파이썬과R 출석수업 과제물", "iris.txt")

# iris.txt 파일을 iris_all 이라는 이름의 데이터 프레임으로 입력
iris_all <- read.csv(file_path)

# iris_all의 첫 5행만 iris_5 라는 이름의 데이터 프레임으로 저장
iris_5 <- head(iris_all, 5)

# iris_all의 마지막 행을 가져옴
last_row <- tail(iris_all, 1)

# iris_5의 세 번째 행의 위치에 마지막 행을 끼워 넣음
# 1~2행, 마지막 행, 3~5행 순서로 합칩니다.
iris_6 <- rbind(iris_5[1:2, ], last_row, iris_5[3:5, ])

# iris_6를 행 번호를 유지하면서 UTF-8 인코딩으로 iris_6.csv 라는 이름의 파일로 저장
# row.names=TRUE로 행 번호를 파일에 포함시킵니다.
write.csv(iris_6, "iris_6.csv", row.names = TRUE, fileEncoding = "UTF-8")

print("iris_6.csv 파일이 생성되었습니다.")
print("생성된 iris_6 데이터 프레임 내용:")
print(iris_6)
```

#### 실행 결과
```
[1] "iris_6.csv 파일이 생성되었습니다."
[1] "생성된 iris_6 데이터 프레임 내용:"
    Sepal.Length Sepal.Width Petal.Length Petal.Width   Species
1            5.1         3.5          1.4         0.2    setosa
2            4.9         3.0          1.4         0.2    setosa
150          5.9         3.0          5.1         1.8 virginica
3            4.7         3.2          1.3         0.2    setosa
4            4.6         3.1          1.5         0.2    setosa
5            5.0         3.6          1.4         0.2    setosa
```
> `iris_6.csv` 파일을 엑셀로 열면 R의 행 이름(1, 2, 150, 3, 4, 5)이 첫 번째 열로 포함된 6행의 데이터가 정상적으로 표시됩니다.