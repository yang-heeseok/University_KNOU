# a. 변수와 자료형
student_id = "202334-153257"
id_list = []

# b. 반복문 및 형 변환
for char in student_id:
    if char.isdigit():
        id_list.append(int(char))

print(id_list)

total_sum = sum(id_list)

if total_sum > 30:
    print("학번 숫자의 총합은 30보다 큽니다.")
else:
    print("학번 숫자의 총합은 30보다 작거나 같습니다.")