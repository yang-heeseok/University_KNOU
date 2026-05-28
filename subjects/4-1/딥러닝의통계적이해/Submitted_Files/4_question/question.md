# 문제 4 - Google Colab MNIST 완전연결신경망 (8점)

## 과제 요약

Google Colab을 이용하여 **MNIST 데이터셋에 대한 완전연결신경망(FCN/MLP)** 을 구현하고,  
교재 코드를 참고하되 **신경망 구조를 부분 수정**하여 작성한 후, **과정을 상세히 설명**한다.

---

## 요구사항 체크리스트

- [ ] Google Colab 사용
- [ ] MNIST 데이터셋 기반 완전연결신경망
- [ ] 교재 코드 참고 + **신경망 구조 부분 수정** (은닉층 수, 뉴런 수 등)
- [ ] 코드와 주석만 있으면 감점 → **프로그램 설명(산문 서술) 반드시 포함**
- [ ] 코드 및 **최종 결과 캡처** 포함

---

## 참고 교재 코드

- 원본: https://github.com/data-better/DeepS/blob/master/10%EC%9E%A5_MNIST_DL.ipynb

---

## 수정 방향 제안 (교재 대비 변경 사항)

### 교재 원본 추정 구조
```
Input(784) → Dense(128, ReLU) → Dense(64, ReLU) → Output(10, Softmax)
```

### 수정안 A: 은닉층 추가 + 드롭아웃
```
Input(784) → Dense(256, ReLU) → Dropout(0.3)
           → Dense(128, ReLU) → Dropout(0.3)
           → Dense(64, ReLU)
           → Output(10, Softmax)
```

### 수정안 B: BatchNormalization 추가
```
Input(784) → Dense(512, ReLU) → BatchNormalization()
           → Dense(256, ReLU) → BatchNormalization()
           → Dense(128, ReLU)
           → Output(10, Softmax)
```

### 수정안 C: 더 얕고 넓은 구조 (비교 실험용)
```
Input(784) → Dense(512, ReLU) → Dense(512, ReLU) → Output(10, Softmax)
```

> **추천**: 수정안 A (Dropout 추가) → 명확한 개선 효과 설명 가능

---

## 전체 코드 (수정안 A 기준)

```python
# ============================================================
# MNIST 완전연결신경망 - 수정 구현
# 교재 대비 변경: 은닉층 3개(원본 2개), Dropout 추가
# ============================================================

# 1. 라이브러리 임포트
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

print("TensorFlow 버전:", tf.__version__)

# ============================================================
# 2. 데이터 로드 및 전처리
# ============================================================
# MNIST: 손글씨 숫자 0~9, 60,000개 훈련 / 10,000개 테스트
(X_train, y_train), (X_test, y_test) = keras.datasets.mnist.load_data()

print(f"훈련 데이터: {X_train.shape}, 레이블: {y_train.shape}")
print(f"테스트 데이터: {X_test.shape}, 레이블: {y_test.shape}")

# 정규화: 픽셀값 [0, 255] → [0, 1] 범위로 스케일링
X_train = X_train.astype('float32') / 255.0
X_test  = X_test.astype('float32')  / 255.0

# Flatten: (28, 28) 2D 이미지 → (784,) 1D 벡터
X_train = X_train.reshape(-1, 784)
X_test  = X_test.reshape(-1, 784)

print(f"전처리 후 훈련 데이터: {X_train.shape}")

# 일부 이미지 시각화
fig, axes = plt.subplots(2, 5, figsize=(10, 4))
for i, ax in enumerate(axes.flat):
    ax.imshow(X_train[i].reshape(28, 28), cmap='gray')
    ax.set_title(f"Label: {y_train[i]}")
    ax.axis('off')
plt.tight_layout()
plt.show()

# ============================================================
# 3. 모델 구성 (교재 대비 수정)
# 수정사항:
#   - 은닉층 2개(교재) → 3개로 증가
#   - 뉴런 수 변경: 128, 64 → 256, 128, 64
#   - Dropout(0.3) 추가: 과적합 방지
# ============================================================
model = keras.Sequential([
    # 입력층
    layers.Input(shape=(784,)),
    
    # 은닉층 1: 256 뉴런, ReLU 활성화
    layers.Dense(256, activation='relu', name='hidden1'),
    layers.Dropout(0.3, name='dropout1'),  # 추가: 30% 무작위 비활성화
    
    # 은닉층 2: 128 뉴런, ReLU 활성화
    layers.Dense(128, activation='relu', name='hidden2'),
    layers.Dropout(0.3, name='dropout2'),
    
    # 은닉층 3: 64 뉴런, ReLU 활성화 (교재 대비 추가된 층)
    layers.Dense(64, activation='relu', name='hidden3'),
    
    # 출력층: 10개 클래스(0~9), Softmax 확률 출력
    layers.Dense(10, activation='softmax', name='output')
])

model.summary()

# ============================================================
# 4. 모델 컴파일
# ============================================================
model.compile(
    optimizer='adam',                          # Adam 최적화 (적응형 학습률)
    loss='sparse_categorical_crossentropy',    # 다중분류 손실함수
    metrics=['accuracy']                        # 평가 지표
)

# ============================================================
# 5. 모델 학습
# ============================================================
history = model.fit(
    X_train, y_train,
    epochs=20,
    batch_size=128,
    validation_split=0.1,   # 훈련 데이터의 10%를 검증용으로 사용
    verbose=1
)

# ============================================================
# 6. 모델 평가
# ============================================================
test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
print(f"\n테스트 손실: {test_loss:.4f}")
print(f"테스트 정확도: {test_acc:.4f} ({test_acc*100:.2f}%)")

# ============================================================
# 7. 학습 곡선 시각화
# ============================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# 정확도 곡선
ax1.plot(history.history['accuracy'], label='훈련 정확도')
ax1.plot(history.history['val_accuracy'], label='검증 정확도')
ax1.set_title('모델 정확도')
ax1.set_xlabel('에포크')
ax1.set_ylabel('정확도')
ax1.legend()
ax1.grid(True)

# 손실 곡선
ax2.plot(history.history['loss'], label='훈련 손실')
ax2.plot(history.history['val_loss'], label='검증 손실')
ax2.set_title('모델 손실')
ax2.set_xlabel('에포크')
ax2.set_ylabel('손실')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()

# ============================================================
# 8. 예측 결과 확인
# ============================================================
predictions = model.predict(X_test[:10])
predicted_labels = np.argmax(predictions, axis=1)

print("\n예측 결과 (첫 10개):")
print(f"예측값: {predicted_labels}")
print(f"실제값: {y_test[:10]}")
```

---

## 보고서 작성 구성 (코드 + 설명)

### ⚠️ 중요: 주석만 있으면 감점! 반드시 산문 형식의 프로그램 설명 포함

### (1) 데이터 소개 및 전처리 설명 [캡처: 데이터 시각화]
> MNIST는 0부터 9까지의 손글씨 숫자 이미지 데이터셋으로, 28×28 픽셀의 흑백 이미지 70,000개로 구성된다. 완전연결신경망의 입력은 1차원 벡터여야 하므로, 28×28 행렬을 784차원 벡터로 평탄화(flatten)하는 전처리가 필요하다. 또한 픽셀값의 범위를 [0, 255]에서 [0, 1]로 정규화하여 학습 안정성을 높인다.

### (2) 신경망 구조 설명 [캡처: model.summary()]
> 본 모델은 교재의 구조(은닉층 2개)를 기반으로, 은닉층을 3개로 늘리고 각 층에 드롭아웃을 추가하여 수정하였다. 첫 번째 은닉층은 256개 뉴런, 두 번째는 128개, 세 번째는 64개로 점진적으로 줄어드는 피라미드 구조를 채택했다. 이는 고차원 특징에서 점차 중요한 특징만을 추출하는 과정을 모방한다.

### (3) 컴파일 및 하이퍼파라미터 선택 근거
> Adam 최적화기는 모멘텀과 적응형 학습률을 결합한 방법으로, MNIST 같은 표준 데이터셋에서 빠른 수렴을 보인다. 손실함수로는 다중분류 문제이므로 sparse_categorical_crossentropy를 사용했으며, 이는 최대가능도추정(MLE)의 관점에서 예측 분포와 실제 레이블 분포의 KL-발산을 최소화하는 것과 동치이다.

### (4) 학습 과정 설명 [캡처: 학습 출력 로그]
> 20번의 에포크 동안 128개의 미니배치로 학습을 진행하며, 훈련 데이터의 10%를 검증 데이터로 사용한다. 에포크가 진행될수록 훈련 손실이 감소하고 정확도가 향상되는 것을 관찰할 수 있다. 검증 손실과 훈련 손실의 간격이 벌어지면 과적합의 징후이므로 Dropout이 이를 억제하는 역할을 한다.

### (5) 최종 결과 분석 [캡처: 학습 곡선, 최종 정확도]
> 테스트 정확도는 약 XX%로, 교재 원본 모델 대비 (개선됨/유사함)을 확인하였다. 학습 곡선에서 훈련 정확도와 검증 정확도가 함께 수렴하는 것은 드롭아웃이 과적합 방지에 효과적임을 보여준다.

---

## 교재 코드 대비 수정 요약표

| 항목 | 교재 원본 | 수정 버전 | 수정 이유 |
|------|---------|---------|---------|
| 은닉층 수 | 2개 | **3개** | 더 깊은 표현력 확보 |
| 첫 번째 은닉층 뉴런 | 128개 | **256개** | 초기 특징 추출 강화 |
| Dropout | 없음 | **추가 (0.3)** | 과적합 방지 |
| 에포크 | (교재 확인) | **20회** | 충분한 수렴 보장 |

---

## 주의사항

- 코드 블록 사이사이에 **산문 형식의 설명 단락** 반드시 삽입
- 최종 정확도 및 손실값 **숫자 직접 기재**
- 학습 곡선 그래프 **캡처 포함** (훈련/검증 정확도 & 손실)
- 코드는 실제 Colab에서 **실행하여 결과 확인 후** 캡처

---

## 예상 결과

| 지표 | 예상값 |
|------|--------|
| 테스트 정확도 | 97~98% |
| 학습 시간 | Colab CPU 기준 약 2~3분 |
| 총 파라미터 수 | 약 232,074개 |
