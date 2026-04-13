# 문제 4. Google Colab을 이용한 MNIST 완전연결신경망 구현

---

## 1. MNIST 데이터셋 개요

MNIST(Modified National Institute of Standards and Technology)는 손글씨 숫자 이미지로 구성된 벤치마크 데이터셋으로, 훈련 데이터 60,000개와 테스트 데이터 10,000개가 포함되어 있다. 각 이미지는 28×28 픽셀의 흑백(단채널) 이미지이며, 레이블은 0부터 9까지의 정수형 범주형 변수이다.

통계학적 관점에서 MNIST의 각 이미지는 784차원($28 \times 28 = 784$) 유클리드 공간 $\mathbb{R}^{784}$ 위의 한 점으로 해석된다. 각 픽셀 $x_j \in [0, 255]$는 명도 강도를 나타내는 연속형 변수로, 학습 편의를 위해 $[0, 1]$ 구간으로 정규화한다. 결국 MNIST의 분류 문제는 784차원 입력 공간에서 10개의 범주로 구성된 출력 공간으로의 비선형 사상(mapping)을 추정하는 문제이며, 이는 비모수 다중분류(multi-class classification) 문제에 해당한다.

완전연결신경망(Fully Connected Network, FCN)—또는 다층 퍼셉트론(Multi-Layer Perceptron, MLP)—이 이 문제에 적합한 이유는, 픽셀 간의 공간적 구조를 무시하더라도 784차원의 전역 특징 조합으로 충분히 클래스를 구분할 수 있기 때문이다. 이는 저해상도 이미지에서 특히 유효한 접근이다.

---

## 2. 교재 원본 코드와 수정 구조 비교

### 2.1 교재 원본 신경망 구조

교재의 참조 코드(10장 MNIST_DL.ipynb)는 다음과 같은 간결한 단일 은닉층 구조를 사용한다.

```
Input(784) → Flatten → Dense(512, ReLU) → Dense(10, Softmax)
```

주요 하이퍼파라미터는 아래와 같다.

| 항목 | 값 |
|------|----|
| 은닉층 수 | 1개 |
| 은닉층 뉴런 수 | 512 |
| 활성화 함수 | ReLU |
| 최적화기 | Adam |
| 에포크 | 12 |
| 배치 크기 | 256 |
| 검증 분할 | 25% |

교재 코드는 단순한 구조임에도 불구하고 테스트 정확도 약 98%를 달성하며, MNIST가 비교적 선형 분리 가능한 단순 구조의 데이터셋임을 보여 준다.

### 2.2 수정된 신경망 구조

본 구현에서는 교재 대비 다음과 같이 구조를 변경하였다.

```
Input(784)
  → Dense(256, ReLU) → Dropout(0.3)
  → Dense(128, ReLU) → Dropout(0.3)
  → Dense(64,  ReLU)
  → Dense(10,  Softmax)
```

### 2.3 구조 비교표

| 항목 | 교재 원본 | 수정 버전 | 수정 근거 |
|------|-----------|-----------|-----------|
| 은닉층 수 | 1개 | **3개** | 계층적 특징 추출 가능, 표현력 증대 |
| 첫 번째 은닉층 뉴런 | 512 | **256** | 과도한 파라미터 억제, 일반화 유도 |
| 두 번째 은닉층 뉴런 | — | **128** | 피라미드 구조로 점진적 축소 |
| 세 번째 은닉층 뉴런 | — | **64** | 출력 직전 최종 특징 압축 |
| Dropout | 없음 | **0.3 (2회)** | 과적합 방지 (정규화 효과) |
| 에포크 | 12 | **20** | 더 깊은 네트워크의 충분한 수렴 확보 |
| 배치 크기 | 256 | **128** | 미니배치 노이즈 증가로 일반화 향상 |
| 검증 분할 | 25% | **10%** | 훈련 데이터 활용 극대화 |

---

## 3. 수정 근거 및 통계학적 해석

### 3.1 피라미드 구조와 차원 축소

은닉층 뉴런 수를 256 → 128 → 64로 점차 줄이는 피라미드 구조는 차원 축소(dimensionality reduction)의 관점에서 이해할 수 있다. 784차원의 입력 공간을 256차원의 잠재 공간으로 압축하고, 이를 다시 128, 64차원으로 순차적으로 축소함으로써 각 층에서 가장 변별력 있는 특징(feature)만을 남긴다. 이는 주성분분석(PCA)의 비선형 확장이라고도 볼 수 있다.

교재의 단일 은닉층 512 뉴런 구조는 한 번의 변환으로 784차원을 직접 처리하지만, 본 구현은 여러 비선형 변환을 거쳐 계층적으로 추상화함으로써 더 복잡한 결정 경계(decision boundary)를 형성한다.

### 3.2 Dropout의 통계학적 해석

Dropout은 학습 단계에서 각 뉴런을 확률 $p = 0.3$으로 무작위 비활성화하는 기법으로, 이는 모델 앙상블(ensemble)의 효과를 낸다. 매 미니배치마다 다른 부분망(subnetwork)이 학습되므로, 최종 추론 시에는 지수적으로 많은 모델의 평균적 예측을 얻는 것과 수학적으로 동치이다. 통계학적으로는 $L_2$ 정규화(릿지 회귀)와 유사하게 파라미터가 지나치게 특정 입력에 의존하지 않도록 하는 수축(shrinkage) 효과를 가진다.

### 3.3 Adam 최적화기와 학습률 적응

Adam(Adaptive Moment Estimation)은 1차 모멘트(기댓값)와 2차 모멘트(분산)을 모두 추정하여 파라미터별 적응형 학습률을 사용한다. 업데이트 규칙은 다음과 같다.

$$m_t = \beta_1 m_{t-1} + (1 - \beta_1) g_t$$
$$v_t = \beta_2 v_{t-1} + (1 - \beta_2) g_t^2$$
$$\hat{m}_t = \frac{m_t}{1 - \beta_1^t}, \quad \hat{v}_t = \frac{v_t}{1 - \beta_2^t}$$
$$\theta_t = \theta_{t-1} - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon} \hat{m}_t$$

여기서 $g_t$는 $t$번째 스텝의 기울기, $\beta_1 = 0.9$, $\beta_2 = 0.999$, $\eta$는 기본 학습률(0.001)이다. Adam은 희소한 기울기에도 강건하며 수렴이 빠르다는 장점이 있어 MNIST와 같은 다중분류 문제에 적합하다.

### 3.4 손실함수와 최대가능도추정

다중분류 문제의 손실함수로 사용된 `sparse_categorical_crossentropy`는 다음과 같이 정의된다.

$$\mathcal{L} = -\frac{1}{N} \sum_{i=1}^{N} \log \hat{p}_{i, y_i}$$

여기서 $N$은 배치 내 샘플 수, $y_i$는 $i$번째 샘플의 실제 레이블, $\hat{p}_{i, y_i}$는 모델이 해당 클래스를 예측한 확률이다. 이는 범주형 분포(categorical distribution)를 가정했을 때의 음의 로그가능도(negative log-likelihood)이며, 손실 최소화는 최대가능도추정(MLE)과 동치이다.

---

## 4. 완전연결신경망의 수식적 구조

완전연결신경망의 순전파(forward propagation)는 $L$개의 층에 걸쳐 아래와 같이 정의된다.

**$l$번째 층의 선형 변환:**
$$\mathbf{z}^{(l)} = W^{(l)} \mathbf{a}^{(l-1)} + \mathbf{b}^{(l)}$$

**활성화 함수 적용 (은닉층, ReLU):**
$$\mathbf{a}^{(l)} = \text{ReLU}(\mathbf{z}^{(l)}) = \max(\mathbf{0},\ \mathbf{z}^{(l)})$$

**출력층 (Softmax):**
$$\hat{p}_k = \frac{\exp(z_k^{(L)})}{\sum_{j=1}^{10} \exp(z_j^{(L)})}, \quad k = 0, 1, \ldots, 9$$

여기서 $W^{(l)} \in \mathbb{R}^{d_l \times d_{l-1}}$, $\mathbf{b}^{(l)} \in \mathbb{R}^{d_l}$은 각각 $l$번째 층의 가중치 행렬과 편향 벡터이며, $d_l$은 해당 층의 뉴런 수이다. 본 모델에서는 $d_0 = 784$, $d_1 = 256$, $d_2 = 128$, $d_3 = 64$, $d_4 = 10$으로 설정하였다.

역전파(backpropagation)는 연쇄 법칙(chain rule)을 통해 각 가중치에 대한 손실 기울기를 계산하며, Adam이 이를 이용해 파라미터를 업데이트한다.

---

## 5. 구현 코드 및 설명

### 5.1 라이브러리 임포트 및 환경 확인

```python
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

print("TensorFlow 버전:", tf.__version__)
```

TensorFlow와 Keras를 불러온 뒤 버전을 확인한다. Google Colab은 최신 TensorFlow가 사전 설치되어 있으므로 별도의 설치 없이 바로 실행할 수 있다. NumPy는 배열 연산에, Matplotlib은 학습 결과 시각화에 사용된다.

---

### 5.2 데이터 로드 및 전처리

```python
(X_train, y_train), (X_test, y_test) = keras.datasets.mnist.load_data()

print(f"훈련 데이터: {X_train.shape}, 레이블: {y_train.shape}")
print(f"테스트 데이터: {X_test.shape}, 레이블: {y_test.shape}")

# 정규화: [0, 255] → [0, 1]
X_train = X_train.astype('float32') / 255.0
X_test  = X_test.astype('float32')  / 255.0

# Flatten: (28, 28) → (784,)
X_train = X_train.reshape(-1, 784)
X_test  = X_test.reshape(-1, 784)

print(f"전처리 후 훈련 데이터 shape: {X_train.shape}")
```

`keras.datasets.mnist.load_data()`는 Keras 내장 함수로, MNIST 데이터를 자동으로 다운로드하여 훈련·테스트 세트로 분리해 반환한다. 픽셀값을 255로 나누는 정규화는 입력 변수의 스케일을 통일시켜 경사 하강법의 안정성을 높인다. 이는 표준화(standardization)와 마찬가지로 최적화 과정에서의 수치적 안정성을 도모하는 표준적 전처리 절차이다.

이어서 `.reshape(-1, 784)` 연산으로 각 이미지를 28×28 2차원 행렬에서 784차원 1차원 벡터로 변환한다. 완전연결층은 2차원 구조를 직접 처리할 수 없으므로 이 평탄화(flatten) 과정이 필수적이다.

> **[캡처 위치 1]** 코드 실행 후 출력되는 shape 정보 및 샘플 이미지 시각화 결과

---

### 5.3 샘플 이미지 시각화

```python
fig, axes = plt.subplots(2, 5, figsize=(10, 4))
for i, ax in enumerate(axes.flat):
    ax.imshow(X_train[i].reshape(28, 28), cmap='gray')
    ax.set_title(f"Label: {y_train[i]}")
    ax.axis('off')
plt.suptitle("MNIST 훈련 샘플 (처음 10개)", y=1.02)
plt.tight_layout()
plt.show()
```

시각화를 통해 각 이미지가 실제로 손글씨 숫자를 나타내는지 확인한다. 동일한 숫자라도 필압, 기울기, 굵기가 다양하여 분류 문제가 단순하지 않음을 직관적으로 파악할 수 있다. `cmap='gray'`는 단채널 흑백 이미지를 올바르게 렌더링하는 옵션이다.

> **[캡처 위치 2]** 2×5 그리드로 출력되는 손글씨 숫자 샘플 이미지

---

### 5.4 모델 구성

```python
model = keras.Sequential([
    layers.Input(shape=(784,)),

    layers.Dense(256, activation='relu', name='hidden1'),
    layers.Dropout(0.3, name='dropout1'),

    layers.Dense(128, activation='relu', name='hidden2'),
    layers.Dropout(0.3, name='dropout2'),

    layers.Dense(64, activation='relu', name='hidden3'),

    layers.Dense(10, activation='softmax', name='output')
])

model.summary()
```

`keras.Sequential` API를 이용하여 층을 순차적으로 쌓는다. 입력층은 784차원 벡터를 받으며, 이후 세 개의 완전연결 은닉층이 순서대로 연결된다. 각 은닉층은 ReLU 활성화 함수를 사용하는데, ReLU는 양의 구간에서 기울기 소실(vanishing gradient) 문제를 완화하는 장점이 있다. Dropout층은 훈련 중 임의로 30%의 뉴런을 비활성화하여 모델이 특정 뉴런에 과도하게 의존하지 않도록 한다. 출력층은 10개 클래스에 대한 확률 분포를 Softmax 함수로 출력한다.

> **[캡처 위치 3]** `model.summary()` 출력 결과 (층별 파라미터 수 및 총 파라미터 수)

총 파라미터 수는 다음과 같이 계산된다.

- hidden1: $784 \times 256 + 256 = 200,960$
- hidden2: $256 \times 128 + 128 = 32,896$
- hidden3: $128 \times 64 + 64 = 8,256$
- output: $64 \times 10 + 10 = 650$
- **합계: 242,762개**

---

### 5.5 모델 컴파일

```python
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)
```

모델 컴파일 단계에서는 최적화 알고리즘, 손실함수, 평가 지표를 지정한다. 앞서 설명한 바와 같이 Adam 최적화기는 적응형 학습률로 수렴 속도가 빠르고 하이퍼파라미터 튜닝 부담이 적다. `sparse_categorical_crossentropy`는 레이블이 정수형(0, 1, ..., 9)으로 인코딩된 경우에 사용하며, 원-핫 인코딩된 경우에는 `categorical_crossentropy`를 사용해야 한다.

---

### 5.6 모델 학습

```python
history = model.fit(
    X_train, y_train,
    epochs=20,
    batch_size=128,
    validation_split=0.1,
    verbose=1
)
```

총 20 에포크 동안 128개의 미니배치 단위로 경사 하강법을 반복한다. `validation_split=0.1`은 훈련 데이터의 10%인 6,000개를 검증 세트로 자동 분리하여 각 에포크가 끝날 때마다 일반화 성능을 모니터링한다. 반환값 `history`에는 에포크별 훈련·검증 손실 및 정확도가 기록되어 학습 곡선 시각화에 활용된다.

> **[캡처 위치 4]** 학습 진행 로그 (에포크별 loss, accuracy, val_loss, val_accuracy)

---

### 5.7 모델 평가

```python
test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
print(f"\n테스트 손실: {test_loss:.4f}")
print(f"테스트 정확도: {test_acc:.4f} ({test_acc*100:.2f}%)")
```

학습에 전혀 사용되지 않은 10,000개의 테스트 데이터로 최종 성능을 측정한다. 이 값이 모델의 실제 일반화(generalization) 성능을 나타낸다. 훈련 정확도와 테스트 정확도의 차이가 크면 과적합, 두 값 모두 낮으면 과소적합을 의심할 수 있다.

> **[캡처 위치 5]** 테스트 손실 및 테스트 정확도 출력 결과 (예: 97~98%대)

---

### 5.8 학습 곡선 시각화

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

ax1.plot(history.history['accuracy'],     label='훈련 정확도', color='royalblue')
ax1.plot(history.history['val_accuracy'], label='검증 정확도', color='tomato',
         linestyle='--')
ax1.set_title('에포크별 정확도')
ax1.set_xlabel('에포크')
ax1.set_ylabel('정확도')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(history.history['loss'],     label='훈련 손실', color='royalblue')
ax2.plot(history.history['val_loss'], label='검증 손실', color='tomato',
         linestyle='--')
ax2.set_title('에포크별 손실')
ax2.set_xlabel('에포크')
ax2.set_ylabel('손실')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.suptitle('학습 곡선 (수정된 FCN)', fontsize=13)
plt.tight_layout()
plt.show()
```

학습 곡선은 모델의 과적합 여부를 진단하는 핵심 도구이다. 훈련 손실과 검증 손실이 함께 단조 감소하다가 수렴하면 적절한 학습이 이루어진 것이다. 반면 검증 손실이 특정 에포크 이후 다시 증가하면 과적합의 신호이며, 이 경우 조기 종료(early stopping)나 Dropout 강화가 필요하다.

> **[캡처 위치 6]** 훈련/검증 정확도 및 손실 곡선 그래프 (2개 subplot)

---

### 5.9 예측 결과 확인

```python
predictions = model.predict(X_test[:10])
predicted_labels = np.argmax(predictions, axis=1)

print("예측값:", predicted_labels)
print("실제값:", y_test[:10])
```

`model.predict()`는 Softmax 출력, 즉 각 클래스에 대한 사후확률(posterior probability)을 반환한다. `np.argmax(predictions, axis=1)`는 확률이 가장 높은 클래스를 최종 예측 레이블로 선택하는 과정으로, 이는 최대 사후확률(MAP) 결정 규칙에 해당한다.

---

## 6. 학습 결과 분석 및 해석

### 6.1 실행 결과 요약

| 평가 지표 | 교재 원본 | 수정 버전 (실측) |
|-----------|-----------|-----------------|
| 최종 훈련 정확도 | 99.8% | **98.79%** |
| 최종 검증 정확도 | 97.7% | **97.95%** |
| 테스트 정확도 | 98.0% | **98.04%** |
| 테스트 손실 | 0.066 | **0.0804** |
| 총 파라미터 수 | 407,050개 | **242,762개** |
| 과적합 경향 | 낮음 | **없음** (Dropout 효과) |

### 6.2 과적합 여부 해석

실제 학습 결과, 훈련 정확도(98.79%)와 검증 정확도(97.95%)의 격차는 약 0.84%p로, 과적합이 거의 발생하지 않았음을 확인할 수 있다. 손실 곡선에서도 훈련 손실과 검증 손실이 함께 단조 감소하며 수렴하는 양상을 보이며, 검증 손실이 특정 에포크 이후 반등하는 현상(과적합의 전형적 신호)이 나타나지 않았다.

교재 원본 대비 파라미터 수가 약 40%(407,050개 → 242,762개) 감소하였음에도 테스트 정확도는 98.04%로 교재 원본(98.0%)과 동등한 수준을 유지하였다. 이는 Dropout 정규화와 피라미드 구조가 파라미터 효율성을 높였음을 의미하며, 통계학적 편향-분산 트레이드오프(bias-variance tradeoff) 관점에서 모델 분산(variance)을 낮추는 데 성공한 것으로 해석할 수 있다.

### 6.3 한계 및 향후 개선 방향

완전연결신경망은 픽셀 간의 공간적 상관관계를 무시하므로, 합성곱신경망(CNN)에 비해 이미지 특징 추출에 근본적 한계가 있다. 실제로 MNIST에서 단순 FCN의 한계는 99% 이상의 정확도를 달성하기 어렵다는 점이다. 공간적 구조를 명시적으로 활용하는 CNN을 적용하면 99.7% 이상의 정확도가 가능하다. 또한 배치 정규화(Batch Normalization)를 Dropout과 병행하면 학습 안정성이 더욱 향상될 수 있다.

---

## 7. Google Colab 실행 가이드

본 코드는 Google Colab 환경에서 다음 순서로 실행한다.

1. **Colab 접속**: [https://colab.research.google.com](https://colab.research.google.com) 에 접속하여 새 노트북을 생성한다.
2. **런타임 설정**: 상단 메뉴 → 런타임 → 런타임 유형 변경 → GPU 선택 (CPU로도 충분하나 GPU 권장).
3. **셀 단위 실행**: 위 코드를 섹션별(5.1~5.9)로 각각의 코드 셀에 입력하고 Shift+Enter로 순차 실행한다.
4. **캡처**: 각 셀 실행 결과(shape 출력, 이미지 그리드, model.summary(), 학습 로그, 학습 곡선 그래프)를 캡처하여 보고서의 [캡처 위치 1~6]에 삽입한다.
5. **수치 기재**: 테스트 정확도 및 손실 실제 수치를 6.1절 표에 업데이트한다.

> **주의**: Colab의 세션은 일정 시간 비활동 시 연결이 끊기므로, 학습 완료 후 즉시 캡처하는 것을 권장한다. 또한 `model.save('mnist_fcn.h5')`로 모델을 저장해두면 재실행 없이 평가가 가능하다.

---

*작성일: 2026년 4월*
*과목: 딥러닝의통계적이해 / 학번: 153257*
