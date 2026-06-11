# R을 이용한 회귀모형: 연습문제 및 해설

---

## 제1장 단순회귀모형 (p.23)

### 연습문제

1.  **Yᵢ = β₀ + β₁Xᵢ + εᵢ 에서 절편과 기울기의 추정식은?**

    **답:**
    *   기울기: β̂₁ = Σ(Xᵢ - X̄)(Yᵢ - Ȳ) / Σ(Xᵢ - X̄)²
    *   절편: β̂₀ = Ȳ - β̂₁X̄

2.  **다음은 R을 이용한 회귀적합 결과의 일부이다. 추정된 회귀식은?**

    ```r
    > market_lm = lm(Y ~ X, data=market)
    > summary(market_lm)
    Coefficients:
                Estimate Std. Error t value Pr(>|t|)
    (Intercept)   0.3282     1.4302   0.229    0.822
    X             2.1497     0.1548  13.889 3.55e-09 ***
    ```

    **답:** Ŷ = 0.3282 + 2.1497X

3.  **산점도 위에 회귀직선을 그리고자 한다. R 함수 (a)는?**

    ```r
    > plot(market$X, market$Y, xlab="인테리어비", ylab="총판매액", pch=19)
    > (a)(market_lm)
    ```

    **답:** `abline`

4.  **다음은 분산분석 결과이다. (b) 값을 구하는 식은?**

    ```r
    > anova(market_lm)
    Analysis of Variance Table

    Response: Y
               Df Sum Sq Mean Sq F value    Pr(>F)
    X           1 485.57  485.57     (b) 3.554e-09 ***
    Residuals  13  32.72    2.52
    ```

    **답:** (b) = 485.57 / 2.52

5.  **4번 분산분석 결과에서 오차분산 σ²의 추정값은?**

    **답:** MSE = 2.52

6.  **4번 분산분석 결과에서 결정계수를 구하면?**

    **답:** R² = 485.57 / (485.57 + 32.72) = 485.57 / 518.29 = 0.9369

7.  **4번 분산분석 결과에서 귀무가설 H₀: β₁ = 0의 검정 결과는? (유의수준 0.05 기준)**

    **답:** p-값 = 3.55 × 10⁻⁹ < 0.05이므로 H₀: β₁ = 0을 기각한다.

8.  **주어진 X에서 신뢰구간을 구하고자 한다. 기댓값의 신뢰구간을 구하기 위한 옵션 (f)는?**

    ```r
    > pred_frame = data.frame(X=seq(3.5, 14.5, 0.2))
    > pc = predict(market_lm, (f), newdata=pred_frame)
    ```

    **답:** `interval="confidence"` (또는 `int="c"`)

9.  **주어진 X에서 신뢰구간을 구하고자 한다. 새로운 예측값의 신뢰구간을 구하기 위한 옵션 (g)는?**

    ```r
    > pred_frame = data.frame(X=seq(3.5, 14.5, 0.2))
    > pp = predict(market_lm, (g), newdata=pred_frame)
    ```

    **답:** `interval="prediction"` (또는 `int="p"`)

10. **주어진 X에서 구해진 신뢰구간을 이용하여 신뢰대를 그리고자 한다. R 함수 (h)는?**

    ```r
    > pred_X = pred_frame$X
    > plot(market$X, market$Y, ylim=range(market$Y, pp))
    > (h)(pred_X, pc, lty=c(1,2,2), col="BLUE")
    > (h)(pred_X, pp, lty=c(1,3,3), col="RED")
    ```

    **답:** `matlines`

11. **ggplot2를 이용하여 신뢰대를 그리고자 한다. R 명령 (i)는?**

    ```r
    > library(ggplot2)
    > ggplot(all_data, aes(x=X, y=Y)) +
      (i) +                               # 산점도 그리기
      stat_smooth(method=lm) +            # confidence band 그리기
      geom_line(aes(y = lwr), col = "coral2", linetype = "dashed") +
      geom_line(aes(y = upr), col = "coral2", linetype = "dashed")
    ```

    **답:** `geom_point()`

---

## 제2장 중회귀모형 (p.40)

### 연습문제

1.  **중회귀모형 Y = Xβ + ε에서 β의 최소제곱추정량 β̂는?**

    **답:** β̂ = (X'X)⁻¹X'Y

2.  **행렬 X의 치환행렬과의 곱 X'X를 구하는 R 명령은?**

    ```r
    > XTX = (a)
    ```

    **답:** `t(X) %*% X`

3.  **행렬 X'X의 역행렬을 구하는 R 함수는?**

    ```r
    > XTXI = (b)(XTX)
    ```

    **답:** `solve`

4.  **총제곱합 SST를 행렬식으로 표현하면?**

    **답:** SST = Y'(I - (1/n)J)Y

5.  **잔차제곱합 SSE를 행렬식으로 표현하면?**

    **답:** SSE = Y'(I - H)Y, 여기서 H = X(X'X)⁻¹X'

6.  **다음은 중회귀모형을 적합한 결과이다. 물음에 답하시오.**

    ```r
    > market2_lm = lm(Y ~ X1+X2, data=market2)
    > summary(market2_lm)

    Call:
    lm(formula = Y ~ X1 + X2, data = market2)

    Residuals:
         Min       1Q   Median       3Q      Max
    -1.30465 -0.69561 -0.01755  0.69003  1.53127

    Coefficients:
                Estimate Std. Error t value Pr(>|t|)
    (Intercept)  0.85041    0.84624   1.005 0.334770
    X1           1.55811    0.14793  10.532 2.04e-07 ***
    X2           0.42736    0.08431   5.069 0.000276 ***
    ---
    Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

    Residual standard error: 0.9318 on 12 degrees of freedom
    Multiple R-squared:  0.9799,    Adjusted R-squared:  0.9765
    F-statistic: 292.5 on 2 and 12 DF,  p-value: 6.597e-11
    ```

    (1) **회귀분석 결과에서 적합된 회귀식은?**
        **답:** Ŷ = 0.8504 + 1.5581X₁ + 0.4274X₂

    (2) **적합된 회귀모형에 대한 결정계수는?**
        **답:** 0.9799

    (3) **귀무가설 H₀: β₁ = β₂ = 0에 대한 검정 결과는? (유의수준 0.05 기준)**
        **답:** 유의확률 p-값 = 6.597 × 10⁻¹¹로서 매우 작아 귀무가설을 기각한다.

7.  **다음은 분산분석 결과이다. 아래의 분산분석표 빈칸을 완성하시오.**

    ```r
    > anova(market2_lm)
    Analysis of Variance Table

    Response: Y
               Df Sum Sq Mean Sq   F value    Pr(>F)
    X1          1 485.57  485.57 559.283 1.955e-11 ***
    X2          1  22.30   22.30  25.691 0.0002758 ***
    Residuals  12  10.42    0.87
    ```

    **분산분석표 완성:**
    | 요인 | 자유도 | 제곱합 | 평균제곱 | F₀ |
    | :--- | :---: | :---: | :---: | :---: |
    | 회귀 | 2 | 507.87 | 253.94 | 292 |
    | 잔차 | 12 | 10.42 | 0.87 | |
    | 계 | 14 | 518.29 | | |

8.  **7번 분산분석표 결과에서 결정계수를 구하면?**

    **답:** R² = 507.87 / 518.29 = 0.9799

9.  **Y = Xβ + ε, ε ~ N(0, Iσ²)에서 추정량 β̂의 분산을 구하면?**

    **답:** Var(β̂) = (X'X)⁻¹σ²

10. **y = β₀ + β₁X₁ + β₂X₂ + ε을 적합시켰을 때, x₁ = 10, x₂ = 10에서 E(Y)를 95% 신뢰구간으로 추정하고자 한다. R 함수 (a)는?**

    ```r
    > pred_x = data.frame(X1=10, X2=10)
    > pc = (a)(market2_lm, int="c", newdata=pred_x)
    > pc
           fit      lwr      upr
    1 20.70503 19.95796 21.45209
    ```

    **답:** `predict`

11. **다음은 추가제곱합을 구하기 위한 R 분석 결과이다. 물음에 답하시오.**

    ```r
    > h3_lm = lm(Y ~ X1+X3+X4, data=health)
    > h4_lm = lm(Y ~ X1+X2+X3+X4, data=health)
    > anova(h3_lm, h4_lm)
    Analysis of Variance Table

    Model 1: Y ~ X1 + X3 + X4
    Model 2: Y ~ X1 + X2 + X3 + X4
      Res.Df    RSS Df Sum of Sq      F Pr(>F)
    1     26 20856
    2     25 20551  1    304.62 0.3706 0.5482
    ```

    (1) **(X₁, X₃, X₄)인 모형에 X₂을 추가하는 경우의 증가되는 추가회귀제곱합은?**
        **답:** 304.62

    (2) **유의수준 0.05에서 검정할 때, 변수 X₂는 (X₁, X₃, X₄) 모형에 유의한 변수인지 검정하시오.**
        **답:** p-값 = 0.5482 > 0.05이므로 귀무가설을 받아들인다. 즉, 변수 X₂는 유의하지 않다.

12. **추가변수그림을 그리고자 한다. R 패키지 car에서 이용하는 함수 (b)는?**

    ```r
    > library(car)
    > h4_lm = lm(Y ~ X1+X2+X3+X4, data=health)
    > (b)(h4_lm)
    ```

    **답:** `avPlots`

---

## 제3장 변수선택 (p.54)

### 연습문제

1.  **분산팽창인자를 계산하고자 한다. R 함수 (a)는?**

    ```r
    > install.packages("fmsb")
    > library(fmsb)
    > (a)(lm(X1~X2+X3+X4+X5, data=hospital))
    [1] 9597.571
    ```

    **답:** `VIF`

2.  **1번 결과에서 볼 때, 다중공선성이 존재한다고 할 수 있는가?**

    **답:** VIF 값 = 9597로 매우 크므로 다중공선성이 존재한다.

3.  **다음은 모든 가능한 회귀를 위한 R 결과이다. 물음에 답하시오.**

    ```r
    > library(leaps) # (a)
    > all_lm = regsubsets(Y ~ ., data=hald)
    > (rs=summary(all_lm))
    Subset selection object
    Call: regsubsets.formula(Y ~ ., data = hald)
    4 Variables (and intercept)
             Forced in Forced out
    X1           FALSE      FALSE
    X2           FALSE      FALSE
    X3           FALSE      FALSE
    X4           FALSE      FALSE
    1 subsets of each size up to 4
    Selection Algorithm: exhaustive
             X1  X2  X3  X4
    1  ( 1 ) " " " " " " "*"
    2  ( 1 ) "*" "*" " " " "
    3  ( 1 ) "*" "*" " " "*"
    4  ( 1 ) "*" "*" "*" "*"

    > names(rs)
    [1] "which" "rsq"   "rss"   "adjr2" "cp"    "bic"   "outmat" "obj"

    > round(rs$rsq, 3)
    [1] 0.675 0.979 0.982 0.982
    > round(rs$adjr2, 3)
    [1] 0.645 0.974 0.976 0.974
    > round(rs$cp, 3)
    [1] 138.731   2.678   3.018   5.000
    ```

    (1) **모든 가능한 회귀를 위한 R 패키지 (a)는?**
        **답:** `leaps`

    (2) **변수가 하나인 경우 최적으로 채택되는 변수는?**
        **답:** X4

    (3) **변수가 둘인 경우 최적으로 채택되는 변수는?**
        **답:** (X1, X2)

    (4) **수정결정계수 기준으로 볼 때 최적으로 채택되는 변수는?**
        **답:** (X1, X2, X4) (adjr2=0.976)

    (5) **Cₚ를 판정기준으로 할 경우에 채택되는 두 후보군을 고르면?**
        **답:** (X1, X2) (Cp=2.678), (X1, X2, X4) (Cp=3.018)

4.  **앞으로부터 선택법을 이용하여 변수선택을 하고자 한다. 옵션 (b)는?**

    ```r
    > start_lm = lm(Y~1, data=hald)
    > full_lm = lm(Y~., data=hald)
    > step(start_lm, scope=list(lower=start_lm,upper=full_lm), direction="(b)")
    ```

    **답:** `forward`

5.  **뒤로부터 제거법을 이용하여 변수선택을 하고자 한다. 옵션 (c)는?**

    ```r
    > step(full_lm, data=hald, direction="(c)")
    ```

    **답:** `backward`

6.  **단계별 회귀방법을 이용하여 변수선택을 하고자 한다. 옵션 (d)는?**

    ```r
    > step(start_lm, scope=list(upper=full_lm), data=hald, direction="(d)")
    ```

    **답:** `both`

7.  **다음은 R 패키지 olsrr을 이용한 단계별 회귀선택 결과이다. 선택된 독립변수는?**

    ```r
    > library(olsrr)
    > model = lm(Y~ X1+X2+X3+X4, data=hald)
    > ols_step_both_p(model)

                      Stepwise Selection Summary
    ----------------------------------------------------------------
    Added/       Adj.
    Step Variable Removed R-Square R-Square    C(p)       AIC     RMSE
    ----------------------------------------------------------------
    1      X4     addition   0.675    0.645  138.7310   97.7440   8.9639
    2      X1     addition   0.972    0.967    5.4960   67.6341   2.7343
    3      X2     addition   0.982    0.976    3.0180   63.8663   2.3087
    ----------------------------------------------------------------
    ```

    **답:** (X4, X1, X2)

---

## 제4장 모형개발 (p.64)

### 연습문제

1.  **두 변수의 산점도가 다음과 같다. maraton 자료에서 m1990을 반응변수로, sect를 설명변수로 한 3차 다항회귀모형을 적합하고자 한다. (a)에 들어갈 R 명령은?**

    ```r
    > plot(maraton$sect, maraton$m1990, pch=19)
    > maraton_lm = lm(a)
    ```

    **답:** `m1990 ~ sect + I(sect^2) + I(sect^3), data=maraton`

2.  **3차 다항회귀모형 적합 결과가 다음과 같다. 모형적합식은?**

    ```r
    > summary(maraton_lm)
    Coefficients:
                 Estimate Std. Error  t value Pr(>|t|)
    (Intercept) 917.592857   8.083355  113.516 3.61e-08 ***
    sect         13.785281   1.462847    9.424 0.000707 ***
    I(sect^2)    -0.683225   0.073387   -9.310 0.000741 ***
    I(sect^3)     0.012248   0.001077   11.375 0.000341 ***
    ```

    **답:** m1990̂ = 917.593 + 13.785 × sect - 0.683 × sect² + 0.012 × sect³

3.  **2번 3차 다항회귀모형 적합 결과에서 결정계수는?**

    **답:** 0.9983

4.  **다음과 같은 soup 자료에서 변수 D의 0="Line0", 1="Line1"로 범주화하려고 한다. R 함수 (b)는?**

    ```r
    > soup = read.csv("c:/data/reg/soup.csv")
    > soup[c(1,15,16,27),]
        Y   X D
    1  218 100 1
    15 367 265 1
    16 140 105 0
    27 410 295 0
    > soup$D = (b)(soup$D, levels=c(0,1), label=c("Line0", "Line1"))
    ```

    **답:** `factor`

5.  **다음과 같이 그룹을 구분하여 산점도를 그리고자 한다. R 함수 (d)는?**

    ```r
    > plot(soup$X, soup$Y, type="n")
    > (d)(soup$X[soup$D=="Line1"], soup$Y[soup$D=="Line1"], pch=17, col="BLUE")
    > (d)(soup$X[soup$D=="Line0"], soup$Y[soup$D=="Line0"], pch=19, col="RED")
    > legend("bottomright", legend=levels(soup$D), pch=c(19,17), col=c("RED","BLUE"))
    ```

    **답:** `points`

6.  **5번 산점도를 보고, 다음과 같이 생산라인을 고려한 회귀모형을 적합하였다. 적합된 모형식은?**

    ```r
    > soup_lm = lm(Y ~ X+D, data=soup)
    > summary(soup_lm)
    Coefficients:
                Estimate Std. Error t value Pr(>|t|)
    (Intercept) 27.28179   15.40701   1.771  0.0893 .
    X            1.23074    0.06555  18.775 7.48e-16 ***
    DLine1      53.12920    8.21003   6.471 1.08e-06 ***
    ```

    **답:** Ŷ = 27.282 + 1.231X + 53.129D

7.  **6번 회귀적합 결과에서 생산라인 0과 1의 절편의 차이는?**

    **답:** Line1이 Line0보다 53.129 높다.

---

## 제5장 자료의 진단 (p.74)

### 연습문제

1.  **잔차벡터 e와 H = X(X'X)⁻¹X'와의 관계식은?**

    **답:** e = (I - H)Y

2.  **표준화 잔차(standardized residual) 식은?**

    **답:** rᵢ = eᵢ / √[MSE(1 - hᵢᵢ)]

3.  **스튜던트화 잔차(studentized residuals) 식은?**

    **답:** tᵢ = eᵢ / √[MSE(i)(1 - hᵢᵢ)]

4.  **스튜던트화 잔차 tᵢ와 표준화 잔차 rᵢ와의 관계식은?**

    **답:** tᵢ = rᵢ * √[(n - k - 2) / (n - k - 1 - rᵢ²)]

5.  **잔차분석을 하고자 한다. R 함수 (a)는?**

    ```r
    > forbes_res = (a)(forbes_lm)
    > names(forbes_res)
    [1] "std.dev" "hat" "std.res" "stud.res" "cooks" "dfits" ...
    ```

    **답:** `ls.diag`

6.  **5번 결과에서 hat 값을 저장한 변수 (b)는?**

    ```r
    > hat_value = (b)
    ```

    **답:** `forbes_res$hat`

7.  **회귀적합모형의 분산분석 결과가 다음과 같다. 12번째 관측값의 스튜던트화 잔차는 12.374이다. 이 관측점의 Bonferroni 보정 유의확률 p 값을 계산하는 R 식 (a)는?**

    ```r
    > anova(forbes_lm)
    Analysis of Variance Table
    Response: Lpress
               Df Sum Sq Mean Sq F value    Pr(>F)
    temp         1 425.76  425.76  2961.5 < 2.2e-16 ***
    Residuals   15   2.16    0.14
    ```

    **답:** `2 * 17 * (1 - pt(12.374, 14))` (n=17, df_res=15-1=14)

8.  **특이점 검정을 위해서는 R 패키지 car의 함수를 이용하고자 한다. R 함수 (b)는?**

    ```r
    > install.packages("car")
    > library(car)
    > (b)(forbes_lm)
       rstudent unadjusted p-value Bonferonni p
    12 12.37386          6.3025e-09   1.0714e-07
    ```

    **답:** `outlierTest`

9.  **다음과 같은 모형적합 결과 soil.lm에서 Cook의 거리를 구하고자 한다. R 함수 (c)는?**

    ```r
    > soil_lm = lm(SL ~ SG+LOBS+PGC, data=soil)
    > Di = (c)(soil_lm)
    > round(Di, 3)
       1     2     3     4     5     6     7     8     9    10    11
    0.117 0.029 0.000 0.000 0.002 0.000 1.227 0.041 0.171 0.289 0.022
    ```

    **답:** `cooks.distance`

10. **9번 결과에서 영향력 있는 관측점으로 판단되는 관측점은?**

    **답:** 7번 (Cook's D가 1을 초과하여 매우 큼)

---

## 제6장 모형의 진단 (p.84)

### 연습문제

1.  **오차의 등분산성을 검정하고자 한다. R 함수 (a)는?**

    ```r
    > install.packages("car")
    > library(car)
    > (a)(goose_lm)
    Non-constant Variance Score Test
    Variance formula: ~ fitted.values
    Chisquare = 81.41318, Df = 1, p = 1.831324e-19
    ```

    **답:** `ncvTest`

2.  **1번 결과에서 등분산 가정에 대한 검정 결과는? (단, 유의수준 0.05 기준)**

    **답:** 유의확률 p-값 = 1.83 × 10⁻¹⁹이 0.05보다 작으므로 등분산 가정을 기각한다.

3.  **다음과 같은 잔차산점도를 그렸다. 가장 뚜렷하게 의심되는 모형의 가정은?**

    (U자형 잔차 패턴 그림)

    **답:** 모형의 선형성 (잔차에 패턴이 있으므로 선형 관계가 아님을 시사)

4.  **3번 잔차산점도에서 모형에 새로 포함시키는 것이 요구되는 변수항은?**

    **답:** D² (2차항)

5.  **오차의 정규성을 검정할 때, 정규확률그림을 그리기 위한 R 함수 (d)는?**

    ```r
    > library(ggplot2)
    > library(qqplotr)
    > goose_lm = lm(photo ~ obsA, data=goose)
    > rstandard_values = rstandard(goose_lm)
    > (d)(mapping = aes(sample = rstandard_values)) +
      stat_qq_point(size = 2, color = "red") +
      stat_qq_line(color="black") +
      xlab("theoretical") + ylab("rstandard")
    ```

    **답:** `ggplot`

6.  **Shapiro-Wilk의 정규성 검정을 실시하고자 한다. R 함수 (e)는?**

    ```r
    > goose_rstandard = rstandard(goose_lm)
    > (e)(goose_rstandard)

        Shapiro-Wilk normality test

    data:  goose.rstandard
    W = 0.79132, p-value = 1.541e-06
    ```

    **답:** `shapiro.test`

7.  **6번 결과에서 정규성 검정 결과는? (단, 유의수준 0.05 기준)**

    **답:** p-값 = 1.541 × 10⁻⁶ < 0.05이므로 정규분포를 따른다는 가설을 기각한다.

8.  **다음은 Box-Cox 변환 결과이다. 적절한 Y 변수의 변환은?**

    (λ의 최댓값이 0.5 근처인 log-Likelihood 그래프)
    ```r
    > bc_lambda
    [1] 0.4646465
    ```

    **답:** √Y (제곱근) 변수변환 (λ가 0.5에 가까움)

---

## 제7장 일반화선형모형 I (p.98)

### 연습문제

1.  **일반화선형모형의 세 가지 구성성분은?**

    **답:** 반응변수의 분포, 선형예측자, 연결함수

2.  **반응변수가 베르누이분포인 경우, 정준연결 함수는?**

    **답:** g(μ) = log(μ / (1 - μ)) (로짓 함수)

3.  **반응변수가 포아송분포인 경우, 정준연결 함수는?**

    **답:** g(μ) = log(μ) (로그 함수)

4.  **다음 자료에서 occur를 반응변수(1=yes, 0=no)로 하여 로지스틱회귀모형을 적합하고자 한다. (a)에 들어갈 옵션은?**

    ```r
    > logit_m1 <- glm(occurr~p_size_km+con_metric, family=(a)(link=logit), data=glider)
    ```

    **답:** `binomial`

5.  **다음은 4번 logit_m1의 결과이다. 물음에 답하시오.**

    ```r
    > summary(logit_m1)
    Coefficients:
                 Estimate Std. Error z value Pr(>|z|)
    (Intercept) -3.606207   1.436391  -2.511  0.01205 *
    p_size_km    0.023566   0.007462   3.158  0.00159 **
    con_metric   1.631800   1.642758   0.993  0.32055

    (Dispersion parameter for binomial family taken to be 1)

        Null deviance: 68.994  on 49  degrees of freedom
    Residual deviance: 54.661  on 47  degrees of freedom
    AIC: 60.661
    ```
    (1) **적합된 로지스틱회귀식을 쓰시오.**
        **답:** log(π / (1 - π)) = -3.606 + 0.024 * p_size_km + 1.632 * con_metric

    (2) **유의수준 0.05에서 검정할 때, 두 독립변수(con_metric, p_size_km) 중 유의한 변수를 고르면?**
        **답:** p_size_km (p-value=0.00159)

    (3) **이탈도(Residual deviance)에 근거하여 모형의 적합도에 대하여 평가하시오.**
        **답:** 이탈도/자유도 = 54.661/47 = 1.163으로 1에 가까워 모형적합도가 있다고 판단한다.

    (4) **다음에서 두 모형의 분산분석 결과를 비교하기 위한 R 함수 (b)는?**
        ```r
        > logit_m2 <- glm(occurr ~ p_size_km, family=binomial(link=logit), data=glider)
        > (b)(logit_m2, logit_m1, test='Chisq')
        ```
        **답:** `anova`

    (5) **위 (4)번 결과에서 변수 con_metric를 추가하는 것이 유의한지 검정 결과는? (단, 유의수준 0.05 기준)**
        (Pr(>Chi) = 0.3045)
        **답:** p-값 = 0.305 > 0.05이므로 유의하지 않다.

    (6) **두 모형의 AIC 결과가 다음과 같다. 두 모형 중에서 더 적합한 모형은?**
        ```
        df      AIC
        logit_m2 2 59.71577
        logit_m1 3 60.66120
        ```
        **답:** `logit_m2` (AIC가 더 작음)

    (7) **AIC 값을 기준으로 가장 적합한 모형을 자동으로 선택하고자 한다. R 명령 (c)는?**
        ```r
        > library(MASS)
        > (c)(logit_m1, direction='both')
        ```
        **답:** `stepAIC`

6.  **... p_size_km이 1km 증가할 때 Sugar Glider가 출현할 승산은 몇 배 증가할 것으로 추정되는가?**

    ```r
    > exp(coef(logit_m2))
    (Intercept)   p_size_km
    0.07979473   1.02196464
    ```

    **답:** 1.022배

7.  **... p_size_km=150인 경우, Sugar Glider가 출현할 확률을 구하고자 한다. R 명령 (a)는?**

    ```r
    > x <- 150
    > (a)(logit_m2, list(p_size_km=x), type="response")
    0.6749669
    ```

    **답:** `predict`

---

## 제8장 일반화선형모형 II (p.115)

### 연습문제

1.  **다음 2x2 분할표의 확률분포에서 X 값에 대한 승산비(odds ratio)는?**

    **답:** OR = [π₁ * (1 - π₂)] / [π₂ * (1 - π₁)]

2.  **1번 분할표에서 상대위험도(relative risk)는?**

    **답:** RR = π₁ / π₂

3.  **다음은 다항로짓모형 적용 결과이다. (a) 함수는?**

    ```r
    > install.packages("nnet")
    > library(nnet)
    > ml.prog1 <- (a)(program ~ ses + write, data = prg.d)
    ```

    **답:** `multinom`

4.  **3번의 결과에서 log[ P(Y=academic) / P(Y=general) ]의 추정식은?**

    ```
    Coefficients:
             (Intercept) sesmiddle   seshigh     write
    academic       0.205     0.533     1.163     0.549
    vocation      -0.572     0.824     0.180    -0.528
    ```

    **답:** log[ P(Y=academic) / P(Y=general) ] = 0.205 + 0.533x₁ + 1.163x₂ + 0.549x₃

5.  **... 쓰기 점수(x₃)가 1 증가하면 'general' 학습 프로그램보다 'academic'을 선택할 승산은?**

    ```r
    > exp(coef(ml.prog1))
                 (Intercept) sesmiddle  seshigh     write
    academic     1.2275077 1.704530 3.198976 1.7316510
    ```

    **답:** 승산은 e⁰.⁵⁴⁹ = 1.732배 증가한다.

6.  **... 고속도로의 속도제한이 평균 교통사고 발생건수에 어떤 영향을 주는지 분석하고자 한다. R 명령 (a)는?**

    ```r
    > log_m1 <- glm(y~limit+day, (a))
    ```

    **답:** `family = poisson(link=log)`

7.  **다음은 6번 결과의 일부이다. 모형의 적합검정 결과는?**

    ```
    Residual deviance: 107.64  on 91  degrees of freedom
    > 1-pchisq(107.64,91)
    [1] 0.1123525
    ```

    **답:** 잔차 이탈도/자유도 = 107.64/91 ≈ 1.18로 1에 가깝고, 적합결여검정 유의확률이 0.112(>0.05)로 모형의 적합결여는 통계적으로 유의하지 않다.

8.  **6번에서 exp(beta)의 추정값이 다음과 같다. ... 속도제한을 했을 때의 평균 교통사고 발생건수를 속도제한을 하지 않았을 때와 비교하면?**

    ```r
    > exp(coef(log_m1))
    (Intercept)    limityes
    9.0000000   0.7435897
    ```

    **답:** 74.4% 수준으로 감소한다. (1 - 0.744 = 0.256)

