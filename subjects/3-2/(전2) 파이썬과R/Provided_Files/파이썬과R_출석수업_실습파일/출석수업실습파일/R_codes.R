#명령어 파일일
source("D:\\lang\\R\\hello.r")

#문자열 합치기기
paste('abc','cdf')

a<-'abc'
b<-'cdf'
paste(a,b)

#날짜와 시간
format(as.Date('1945-8-15'),"%A")

#재활용규칙
a <- c(1, 2, 3, 4)
b <- c(10, 20)
a + b

c <- c(1, 2, 3, 4, 5)
d <- c(10, 20)
c + d

e <- c(1, 2, 3)
f <- c(4, 5)
e * f


#벡터의 연산
x<-1:4
x1<-c(x, 5)
x2<-x*2
x1
x2

#행렬의 항목 추가
xm <- matrix(1:12, ncol=6, byrow=T)
cbind(xm[,1:2], c(10,20), xm[,3:6])

#데이터프레임
x1<-c('kim', 'lee', 'park')
x2<-c(170, 160, 180)
x3<-c(60,55,75)
data<-data.frame('name'=x1, 'height'=x2, 'weight'=x3)
data[1,2:3]
c(data[1,2], data[1,3])


#반복문
# for
for (n in 1:5) {              
  print(n)
}

# while
n <- 1
while (n <= 5) {
  print(n)
  n <- n + 1
}

# while - continue
n <- 1
while (n <= 5) {
  if (n == 4) {
    n <- n + 1
    next   
  }
  print(n)
  n <- n + 1
}

# while - break
n <- 1
while (n <= 5) {
  if (n == 4) {
    n <- n + 1
    break   
  }
  print(n)
  n <- n + 1
}

# 조건문 & 함수 작성
mysign <- function(x) {
  if (x > 0) {
    cat(paste0(x, " : 양수\n"))
  } else if (x < 0) {
    cat(paste0(x, " : 음수\n"))
  } else {
    cat("0입니다\n")
  }
}

mysign(1)
mysign(-3)
mysign(0)

# 조건문 & 함수 작성
mywage <- function(h) {
  r1 <- 10000          
  r2 <- r1 * 1.5       
  if (h <= 40) {
    wage <- h * r1
  } else {
    wage <- 40 * r1 + (h - 40) * r2
  }
  return(wage)
}


mywage(35)
mywage(45)

#파이썬 클래스
example <- function(name){
  a = paste("Hello", name, "!")
  b = paste("Good-bye", name, "!")
  result <-list(a=a, b=b)
  return(result)
}
aaa<-example("David")
aaa


# 텍스트 파일 출력과 입력
data(iris)
write.table(iris, file="iris.txt", 
            quote=F, 
            row.names=F, 
            fileEncoding = 'UTF-8')
iris2<-read.table("iris.txt", header=T)

# csv 파일 입력과 출력
iris_csv<-read.csv("iris.csv",sep=",",header=T)
write.csv(iris_csv,file="iris2.csv",
          quote=F, 
          row.names=F, 
          fileEncoding = 'UTF-8')

#문자열 바꾸기
addr <- c("충남 연기군 조치원읍 신흥리 123",
          "충남 연기군 조치원읍 교리 9-1",
          "충남 당진시 수청동 1002")
addr2<-gsub("충남 연기군",'세종시', addr)
