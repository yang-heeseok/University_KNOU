
student_id <- "202334-153257"
print(student_id)



target_date <- as.Date("2025-09-08")
day_of_week <- weekdays(target_date)
print(paste("2025년 9월 8일은", day_of_week, "입니다."))



i <- 1
while (i <= 10) {
  if (i %% 3 == 0) {
    i <- i + 1
    next  
  }
  print(i)
  i <- i + 1
}
