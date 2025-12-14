# a. 변수와 자료형
student_id = "202334-153257"
count_dict = {"짝수": 0, "홀수": 0}

# b. 반복문과 제어문
for char in student_id:
    if char.isdigit():
        num = int(char)
        
        if num % 2 == 0:
            count_dict["짝수"] += 1
        else:
            count_dict["홀수"] += 1

# c. 결과 출력
print(count_dict)