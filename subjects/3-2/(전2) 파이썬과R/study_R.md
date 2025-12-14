안녕하세요! 통계데이터학과 학부생으로서 R 언어의 세계에 첫발을 내디딘 것을 환영합니다. R은 통계 분석과 데이터 시각화에 매우 강력한 도구이며, 이 안내서는 여러분이 R과 친숙해지는 데 훌륭한 출발점이 될 것입니다.

이 문서에서는 R 개발 환경 설정부터 간단한 과제를 해결할 수 있는 기본 문법까지, 초보자의 눈높이에 맞춰 단계별로 설명해 드리겠습니다.

---

## 목차

-   Part 1: R 개발 환경 완벽 가이드
    -   1. R 개발 환경의 종류
    -   2. 로컬 개발 환경 (Local)
        -   2.1. R과 RStudio 설치 (초보자 강력 추천)
        -   2.2. RStudio 인터페이스 둘러보기
        -   2.3. (참고) VS Code에서 R 사용하기
    -   3. 웹 개발 환경 (Web-based)
        -   3.1. Posit Cloud (구 RStudio Cloud)
        -   3.2. Google Colab
    -   4. 어떤 환경을 선택해야 할까?
-   Part 2: R 기본 문법 마스터하기
    -   1. 변수와 데이터 타입
    -   2. 데이터 구조 (Vector, Matrix, List, DataFrame)
    -   3. 패키지 설치 및 사용
    -   4. 데이터 불러오기 및 내보내기
    -   5. 기본 함수와 데이터 조작
    -   6. 간단한 시각화

---

## Part 1: R 개발 환경 완벽 가이드

R 프로그래밍을 시작하려면 먼저 코드를 작성하고 실행할 수 있는 환경을 만들어야 합니다. R 개발 환경은 크게 내 컴퓨터에 직접 설치하는 **로컬 환경**과 웹 브라우저를 통해 접속하는 **웹 환경**으로 나눌 수 있습니다.

### 1. R 개발 환경의 종류

| 구분 | 환경 | 장점 | 단점 | 추천 대상 |
| :--- | :--- | :--- | :--- | :--- |
| **로컬** | **RStudio Desktop** | - **R 개발의 표준**<br>- 가장 강력하고 안정적인 기능<br>- 오프라인 작업 가능<br>- 내 컴퓨터의 모든 자원 활용 | - **설치 필요**<br>- 컴퓨터 사양에 영향 받음<br>- 다른 사람과 환경 공유 어려움 | **모든 R 사용자 (특히 진지하게 R을 배울 초보자)** |
| **로컬** | **VS Code + R 확장** | - 범용 코딩 툴 (Python 등)<br>- 가볍고 빠름<br>- 뛰어난 확장성 | - RStudio보다 초기 설정 복잡<br>- R 전용 기능이 부족 | 다른 언어와 함께 VS Code를 이미 사용하는 중급 이상 사용자 |
| **웹** | **Posit Cloud** | - **설치 불필요**<br>- RStudio와 거의 동일한 환경<br>- 프로젝트 공유 및 협업 용이<br>- 어떤 컴퓨터에서든 동일 환경 | - 인터넷 연결 필수<br>- 무료 버전은 사용 시간/성능 제한 | 설치가 부담스러운 입문자, 팀 프로젝트, 강의 수강생 |
| **웹** | **Google Colab** | - 완전 무료, 강력한 하드웨어<br>- Google Drive 연동 편리 | - R이 아닌 Python 중심 환경<br>- R 사용을 위한 추가 설정 필요<br>- RStudio만큼 직관적이지 않음 | 간단한 R 코드 실행, Python과 R을 함께 사용해야 할 때 |

### 2. 로컬 개발 환경 (Local)

가장 일반적이고 강력한 방법입니다. 장기적으로 R을 사용한다면 반드시 익숙해져야 합니다.

#### 2.1. R과 RStudio 설치 (초보자 강력 추천)

**가장 중요:** 반드시 **R을 먼저 설치**한 후, RStudio를 설치해야 합니다. RStudio는 R 언어를 편리하게 사용하도록 도와주는 도구일 뿐, R 자체가 아니기 때문입니다.

**Step 1: R 설치하기**

1.  **CRAN (The Comprehensive R Archive Network)** 사이트에 접속합니다.
2.  자신의 운영체제에 맞는 링크를 클릭합니다. (Download R for Windows, macOS, or Linux)
3.  **Windows 사용자**: `base` 링크를 클릭한 후, "Download R-x.x.x for Windows"를 클릭하여 설치 파일을 다운로드하고 실행합니다. 설치 중 별다른 설정 변경 없이 "다음"을 눌러 기본값으로 설치하면 됩니다.
4.  **macOS 사용자**: 최신 버전의 `R-x.x.x.pkg` 파일을 다운로드하여 설치합니다.

**Step 2: RStudio 설치하기**

1.  **Posit (RStudio 개발사)** 사이트에 접속합니다.
2.  페이지를 아래로 스크롤하여 자신의 운영체제에 맞는 RStudio Desktop 설치 파일을 다운로드합니다. (무료 버전을 설치하면 됩니다.)
3.  다운로드한 파일을 실행하여 설치를 완료합니다.

이제 바탕화면이나 프로그램 목록에 생성된 **RStudio 아이콘**을 실행하면 R을 사용할 준비가 끝납니다.

#### 2.2. RStudio 인터페이스 둘러보기

RStudio를 실행하면 보통 4개의 창(Pane)이 나타납니다. 이 4분할 구조는 R 데이터 분석의 생산성을 극대화합니다.

1.  **스크립트 창 (Script Editor, 좌상단)**
    -   `.R` 스크립트 파일을 작성하고 저장하는 곳입니다.
    -   여러 줄의 코드를 작성하고, `Ctrl+Enter` (macOS: `Cmd+Return`)로 한 줄씩 실행할 수 있습니다.

2.  **콘솔 창 (Console, 좌하단)**
    -   코드가 실제로 실행되고 결과가 출력되는 곳입니다.
    -   한 줄씩 코드를 바로 입력하고 테스트해볼 수 있습니다.

3.  **환경 창 (Environment/History, 우상단)**
    -   `Environment`: 현재 생성된 변수, 데이터 목록과 값을 보여줍니다.
    -   `History`: 지금까지 실행했던 코드 기록을 보여줍니다.

4.  **파일/플롯/패키지 창 (Files/Plots/Packages, 우하단)**
    -   `Files`: 컴퓨터의 파일과 폴더를 탐색합니다.
    -   `Plots`: 시각화 결과(그래프, 차트)가 나타나는 곳입니다.
    -   `Packages`: 패키지를 설치하거나 로드할 수 있습니다.
    -   `Help`: 함수나 패키지에 대한 도움말을 볼 수 있습니다. (예: 콘솔에 `?mean` 입력)

#### 2.3. (참고) VS Code에서 R 사용하기

만약 다른 과목 때문에 VS Code 사용이 익숙하다면, 아래 방법으로 R 환경을 구축할 수도 있습니다.

1.  **R 설치**: 위의 2.1 Step 1과 동일하게 R을 먼저 설치합니다.
2.  **VS Code 설치**: VS Code 공식 홈페이지에서 설치합니다.
3.  **R 확장 프로그램 설치**: VS Code 좌측의 확장(Extensions) 탭에서 `R`을 검색하여 `R Editor for VS Code`를 설치합니다.
4.  **R Language Server 설치**: R 콘솔에서 `install.packages("languageserver")`를 실행합니다.

### 3. 웹 개발 환경 (Web-based)

프로그램 설치 없이 웹 브라우저만으로 R 코드를 작성하고 실행할 수 있어 매우 편리합니다.

#### 3.1. Posit Cloud (구 RStudio Cloud)

RStudio를 웹에서 그대로 사용하는 방식입니다. R을 처음 배울 때 설치 과정의 어려움을 겪지 않고 바로 시작할 수 있어 매우 유용합니다.

-   **접속**: Posit Cloud

**설정 방법:**

1.  사이트에 접속하여 `Sign Up` 버튼을 눌러 회원가입을 합니다. (Google 계정 연동 가능)
2.  로그인 후, `Your Workspace`에서 `New Project` 버튼을 클릭합니다.
3.  잠시 기다리면 로딩이 완료되고, RStudio Desktop과 거의 동일한 화면이 웹 브라우저에 나타납니다.
4.  이제 로컬 환경처럼 코드를 작성하고 실행하면 됩니다. 프로젝트는 클라우드에 자동 저장됩니다.

#### 3.2. Google Colab

원래는 Python을 위한 환경이지만, 간단한 설정을 통해 R 코드를 실행할 수 있습니다.

-   **접속**: Google Colaboratory

**설정 방법:**

1.  Google 계정으로 로그인 후, `파일 > 새 노트`를 선택합니다.
2.  코드 셀에 다음 코드를 입력하고 실행(`Shift+Enter`)하여 R 매직 커맨드를 활성화합니다.
    ```
    %load_ext rpy2.ipython
    ```
3.  이제부터 R 코드를 실행하고 싶은 셀의 맨 위에 `%%R`을 입력하면 해당 셀 전체가 R 코드로 인식됩니다.

    ```R
    %%R
    # 이 셀은 R 코드로 실행됩니다.
    my_data <- data.frame(x = 1:5, y = c(1, 4, 9, 16, 25))
    print(my_data)
    
    # ggplot2 시각화도 가능합니다.
    # install.packages("ggplot2") # 필요시 설치
    library(ggplot2)
    ggplot(my_data, aes(x=x, y=y)) + geom_point()
    ```

### 4. 어떤 환경을 선택해야 할까?

-   **"나는 앞으로 R을 계속 사용할 전문적인 데이터 분석가가 될 거야!"**
    -   ➡️ **RStudio Desktop**을 설치하세요. 가장 표준적이고 강력한 환경입니다.
-   **"일단 R이 어떤 건지 빠르게 맛만 보고 싶어. 설치는 귀찮아."**
    -   ➡️ **Posit Cloud**를 사용하세요. 클릭 몇 번으로 RStudio 환경을 체험할 수 있습니다.
-   **"학교 컴퓨터, 집 컴퓨터 등 여러 곳에서 동일한 환경으로 작업하고 싶어."**
    -   ➡️ **Posit Cloud**가 최고의 선택입니다.
-   **"나는 파이썬이 주력인데, 가끔 R 코드를 돌려봐야 해."**
    -   ➡️ **Google Colab**이나 **VS Code**가 편리할 수 있습니다.

**결론:** 통계학과 학생이라면 **RStudio Desktop을 메인으로 사용**하되, 팀 프로젝트나 외부 실습 시 **Posit Cloud를 보조로 활용**하는 방법을 추천합니다.

---

## Part 2: R 기본 문법 마스터하기

여기서는 간단한 과제를 수행할 수 있을 정도의 핵심적인 R 문법을 다룹니다.

### 1. 변수와 데이터 타입

-   **변수 할당**: `<-` 또는 `=`를 사용합니다. `<-`가 R에서는 전통적으로 선호됩니다.
-   **주석**: `#` 뒤에 오는 내용은 코드로 실행되지 않습니다.

```R
# 변수 a에 10을 할당
a <- 10
b <- "Hello, R!" # 문자열은 따옴표로 감쌉니다.

# 변수 출력
print(a)
b # print() 없이 변수명만 입력해도 콘솔에 출력됩니다.

# 간단한 계산
c <- a * 2
print(c) # 20 출력
```

-   **기본 데이터 타입**:
    -   `numeric`: 숫자 (예: `10`, `3.14`)
    -   `character`: 문자열 (예: `"data"`, `'R'`)
    -   `logical`: 논리형 (`TRUE`, `FALSE`, 단축형 `T`, `F`)
    -   `factor`: 범주형 데이터 (예: 성별, 혈액형). 통계 분석에서 매우 중요합니다.

### 2. 데이터 구조 (Vector, Matrix, List, DataFrame)

R에서 데이터 분석은 대부분 이 데이터 구조들을 다루는 것입니다.

#### **Vector (가장 기본)**

-   **하나의 데이터 타입**으로 구성된 1차원 배열입니다.
-   `c()` 함수로 생성합니다.

```R
# 숫자형 벡터
num_vec <- c(1, 2, 3, 4, 5)

# 문자형 벡터
char_vec <- c("a", "b", "c")

# 벡터 연산
num_vec * 2 # 결과: 2 4 6 8 10

# 벡터 인덱싱 (R은 1부터 시작!)
num_vec[1]      # 첫 번째 요소: 1
num_vec[2:4]    # 2번째부터 4번째까지: 2 3 4
num_vec[c(1, 5)] # 1번째와 5번째 요소: 1 5
```

#### **Matrix**

-   **하나의 데이터 타입**으로 구성된 2차원 행렬입니다.
-   `matrix()` 함수로 생성합니다.

```R
mat <- matrix(1:6, nrow = 2, ncol = 3)
print(mat)
#      [,1] [,2] [,3]
# [1,]    1    3    5
# [2,]    2    4    6

# 인덱싱: [행, 열]
mat[1, 3] # 1행 3열: 5
mat[1, ]  # 1행 전체: 1 3 5
```

#### **List**

-   **서로 다른 데이터 타입**을 담을 수 있는 유연한 구조입니다.

```R
my_list <- list(name = "Alice", age = 25, scores = c(95, 88, 100))
print(my_list)

# 리스트 요소 접근
my_list$name      # "Alice"
my_list[["age"]]  # 25
my_list[[3]][1]   # scores 벡터의 첫 번째 요소: 95
```

#### **Data Frame (가장 중요)**

-   엑셀 시트처럼 생긴 2차원 테이블 구조입니다. 통계 분석에서 가장 많이 사용됩니다.
-   각 열(column)은 **하나의 데이터 타입**을 가져야 하지만, **서로 다른 열은 다른 타입**을 가질 수 있습니다.
-   `data.frame()` 함수로 생성합니다.

```R
# 데이터 프레임 생성
students <- data.frame(
  id = c(101, 102, 103),
  name = c("Alice", "Bob", "Charlie"),
  midterm = c(85, 92, 78)
)
print(students)

# 데이터 프레임 구조 확인
str(students) # 가장 유용한 함수 중 하나!
head(students) # 처음 6개 행 출력

# 열 선택
students$name
students[["midterm"]]

# 행과 열 선택
students[1, ]      # 1행 전체
students[ , "name"] # name 열 전체
students[1, "name"] # 1행의 name: "Alice"
```

### 3. 패키지 설치 및 사용

R의 강력함은 수많은 패키지(추가 기능 모음)에서 나옵니다.

-   **설치**: `install.packages("패키지명")` (한 번만 하면 됨)
-   **로드**: `library(패키지명)` (R 세션을 새로 시작할 때마다 필요)

```R
# 데이터 조작에 필수적인 dplyr 패키지 설치 및 로드
install.packages("dplyr") # 최초 한 번만 실행
library(dplyr)

# 시각화에 필수적인 ggplot2 패키지 설치 및 로드
install.packages("ggplot2")
library(ggplot2)
```

### 4. 데이터 불러오기 및 내보내기

주로 CSV(Comma-Separated Values) 파일을 사용합니다.

```R
# R에 내장된 iris 데이터셋을 CSV 파일로 저장하기
write.csv(iris, "iris_data.csv", row.names = FALSE)

# 저장된 CSV 파일 불러오기
my_data <- read.csv("iris_data.csv")

# 데이터 확인
head(my_data)
```

### 5. 기본 함수와 데이터 조작

-   **기본 통계 함수**: `mean()`, `median()`, `sd()`, `var()`, `summary()`

```R
# iris 데이터셋의 Sepal.Length 열의 평균 계산
mean(iris$Sepal.Length)

# 전체 데이터셋 요약 통계
summary(iris)
```

-   **`dplyr` 패키지를 이용한 데이터 조작 (매우 중요)**
    -   `filter()`: 조건에 맞는 행 선택
    -   `select()`: 원하는 열 선택
    -   `mutate()`: 새로운 열 추가
    -   `arrange()`: 데이터 정렬
    -   `group_by()` & `summarise()`: 그룹별 요약

```R
library(dplyr)

# iris 데이터에서 Species가 setosa이고 Sepal.Length가 5.0 초과인 데이터 필터링
iris %>%
  filter(Species == "setosa" & Sepal.Length > 5.0)

# Species별로 각 측정값의 평균 계산
iris %>%
  group_by(Species) %>%
  summarise(
    avg_sepal_len = mean(Sepal.Length),
    avg_petal_len = mean(Petal.Length)
  )
```

### 6. 간단한 시각화

R은 기본 시각화 기능도 좋지만, `ggplot2` 패키지를 사용하면 훨씬 미려하고 체계적인 그래프를 그릴 수 있습니다.

```R
library(ggplot2)

# 기본 산점도 (Sepal.Length vs Petal.Length)
plot(iris$Sepal.Length, iris$Petal.Length)

# ggplot2를 이용한 산점도 (Species별로 색상 구분)
ggplot(data = iris, aes(x = Sepal.Length, y = Petal.Length, color = Species)) +
  geom_point() +
  labs(title = "Sepal Length vs Petal Length", x = "Sepal Length", y = "Petal Length")

# ggplot2를 이용한 막대 그래프 (Species별 개수)
ggplot(data = iris, aes(x = Species, fill = Species)) +
  geom_bar() +
  labs(title = "Count of Iris Species")
```

이 가이드가 R 언어 학습의 튼튼한 기초가 되기를 바랍니다. 이제 RStudio를 열고 직접 코드를 입력하며 R의 강력한 기능을 탐험해 보세요!

