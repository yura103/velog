# [ML] 지도학습 - 회귀(2): 앙상블 모델(Ensemble Methods)

- Date: 2026-03-03 09:04:04 UTC
- Velog: https://velog.io/@yura103/ML-%EC%A7%80%EB%8F%84%ED%95%99%EC%8A%B5-%ED%9A%8C%EA%B7%802-%EC%95%99%EC%83%81%EB%B8%94-%EB%AA%A8%EB%8D%B8Ensemble-Methods

---

<h3 id="1-앙상블회귀">1. 앙상블(회귀)</h3>
<p>회귀에서는 출력이 숫자이기 때문에 모델 결합 방식이 &quot;평균&quot;이라는 점!</p>
<pre><code>앙상블(회귀)
├─ Bagging 계열 → 분산(Variance) 감소
└─ Boosting 계열 → 편향(Bias) 감소</code></pre><blockquote>
<p>&quot;분류 vs 회귀&quot;의 결합 방식
결합 규칙: 다수결 vs 평균</p>
<ul>
<li>분류: 결과가 클래스 -&gt; 여러 모델의 결과를 투표(다수결)로 합침.</li>
<li>회귀: 결과가 숫자 -&gt; 여러 모델의 예측값을 평균(또는 중앙값)으로 합침.</li>
</ul>
<p>특히, 회귀는 조금씩 틀린 걸 평균 내면 잡음이 줄고 예측이 매끈해지는 효과(분산 감소)가 눈에 보이게 큼.</p>
</blockquote>
<h3 id="2-bagging">2. Bagging</h3>
<p>: Bootstrap(복원추출)로 데이터셋을 여러 개 만들고 각 데이터셋에 모델을 학습시킨 뒤 예측을 합치는 방법</p>
<ul>
<li>회귀에서는 평균 또는 중앙값 사용</li>
<li>분산이 줄어드는 이유<ul>
<li>불안정한 모델(단일 Decision Tree)는 훈련 데이터가 조금만 바뀌어도 경계/규칙이 크게 바뀜.</li>
<li>서로 다른 표본으로 학습한 트리들을 여러 개 만들고 마지막에 평균내서 각 트리의 '우연한 실수'가 상쇄되게 만듦.
<img alt="" src="https://velog.velcdn.com/images/yura103/post/09927b50-fee8-41fd-8a38-66139a66889b/image.png" /></li>
</ul>
</li>
<li>모델들 오차가 서로 덜 비슷할수록 좋음 = 다양성</li>
</ul>
<h4 id="1-bagging-regressor">1) Bagging Regressor</h4>
<ol>
<li>원본 데이터에서 복원 추출(bootstrap)로 여러 데이터셋 생성</li>
<li>같은 모델을 각각 학습</li>
<li>예측을 평균으로 결합
 <img alt="" src="https://velog.velcdn.com/images/yura103/post/56bcc7c4-b595-41f6-971f-de5e4088af53/image.png" /></li>
</ol>
<ul>
<li>base estimator를 자유롭게 선택 가능</li>
<li>병렬 학습 가능</li>
<li>Bias는 거의 줄이지 못함</li>
<li>Variance 감소가 핵심 목적</li>
</ul>
<h4 id="2-randomforest">2) RandomForest</h4>
<p>= Bagging + Feature Randomness
: 노드마다 일부 피처만 랜덤으로 후보에 올려서 트리들이 서로 다르게 자라도록 강제로 다양성 생성</p>
<ul>
<li>결과: 트리들 상관관계 낮아짐</li>
<li>평균 효과 증가</li>
<li>분산 감소 효과 증가</li>
</ul>
<h4 id="3-extra-trees">3) Extra Trees</h4>
<p>= RandomForest + Split Randomness
RandomForest는 분기 기준값은 최적을 찾지만, ExtraTrees는 분기 기준값도 랜덤으로 뽑음.</p>
<ul>
<li>트리 다양성 더 증가</li>
<li>평균 효과 더 증가</li>
<li>대신 너무 랜덤이면 bias 증가 위험<br />

</li>
</ul>
<h3 id="3-boosting">3. Boosting</h3>
<p>: 이전 모델이 못 맞춘 부분을 다음 모델이 집요하게 보정하면서 순차적으로 쌓는 방식</p>
<ul>
<li>Bagging이 병렬 평균이면, Boosting은 순차 보정임!</li>
<li>회귀에서 Boosting의 직관성 : 잔차(residual)<ol>
<li>첫 모델 예측: y^​1​</li>
<li>잔차: r1​=y−y^​1​</li>
<li>다음 모델은 r1을 맞추도록 학습</li>
<li>계속 반복
<img alt="" src="https://velog.velcdn.com/images/yura103/post/1b1b4023-4731-4fa5-a968-f72dc36d458b/image.png" /></li>
</ol>
</li>
</ul>
<blockquote>
<p>분류는 y가 0/1 같은 범주라서</p>
<ul>
<li>&quot;잔차 = y - ŷ”를 그대로 쓰기엔 구조가 맞지 않는 경우가 많고</li>
<li>대신 손실함수의 gradient(기울기)를 다음 모델이 학습한다는 관점이 더 정확함.
회귀: 숫자 오차가 남기 때문에 잔차를 직관적으로 보정
분류: 맞/틀 문제라서 확률 공간에서 손실을 줄이는 방향을 보정</li>
</ul>
</blockquote>
<h4 id="1-gbdtgradient-boosting-decision-tree">1) GBDT(Gradient Boosting Decision Tree)</h4>
<p>: 손실을 줄이는 방향(gradient)을 다음 트리가 근사하도록 얕은 트리를 하나씩 순차적으로 더해가는 기본 부스팅 모델</p>
<ul>
<li>작동 원리<ol>
<li>초기값: y의 평균으로 시작</li>
<li>현재 예측의 오차(또는 gradient) 계산</li>
<li>다음 트리가 그 오차를 맞추도록 학습</li>
<li>기존 예측에 더함</li>
<li>반복
<img alt="" src="https://velog.velcdn.com/images/yura103/post/bb4baf20-fda2-4f75-9aad-64d402cefbca/image.png" /></li>
</ol>
</li>
<li>강한 이유<ul>
<li>비선형 관계 자동 학습</li>
<li>피처 간 상호작용 자동 발견</li>
<li>스케일링 거의 불필요</li>
<li>tabular 데이터에서 매우 강력</li>
</ul>
</li>
<li>핵심 파라미터
<img alt="" src="https://velog.velcdn.com/images/yura103/post/134c5381-0b37-423d-a16b-098104924795/image.png" /></li>
<li>한계<ul>
<li>순차 학습 -&gt; 느림</li>
<li>과적합 쉬움</li>
<li>대규모 데이터에서 비효율적일 수 있음.</li>
</ul>
</li>
</ul>
<h4 id="2-xgboost">2) XGBoost</h4>
<p>:GBDT에 정규화와 안정적 최적화를 추가한 모델</p>
<ul>
<li>GBDT와의 차이점<ul>
<li>목적함수에 트리 복잡도 벌점 추가<ul>
<li>리프 수 벌점</li>
<li>리프 값 크기 벌점 -&gt; 과적합 구조적으로 억제</li>
</ul>
</li>
<li>2차 미분(gradient+hessian) 사용<ul>
<li>분기 판단이 더 안정적</li>
<li>수렴이 빠르고 정확</li>
</ul>
</li>
<li>Pruning(가지치기) 전략<ul>
<li>손실 감소가 작으면 분기 안 함</li>
</ul>
</li>
<li>시스템 최적화<ul>
<li>병렬 처리</li>
<li>결측치 자동 처리</li>
<li>희소 데이터 대응</li>
</ul>
</li>
</ul>
</li>
<li>대표 파라미터<ul>
<li>eta(learning_rate)</li>
<li>max_depth</li>
<li>min_child_weight</li>
<li>subsample</li>
<li>colsample_bytree</li>
<li>gamma(분기 최소 이득)</li>
<li>reg_lambda/reg_alpha<h4 id="3-lightgbm">3) LightGBM</h4>
: 대규모 데이터에서 빠르게 학습하도록 설계된 고속 GBDT 구현체</li>
</ul>
</li>
<li>Histogram 기반 분기<ul>
<li>연속값을 bin으로 압축</li>
<li>계산량 대폭 감소</li>
</ul>
</li>
<li>Leaf-wise 성장<ul>
<li>손실을 가장 많이 줄일 수 있는 리프부터 확장</li>
<li>level-wise보다 수렴 빠름</li>
</ul>
</li>
<li>특징<ul>
<li>매우 빠르고 대용량에 강하며, 메모리 효율적</li>
<li>leaf-wise 특성상 과적합 빠름</li>
<li>작은 데이터에서는 불안정할 수 있음<table>
<thead>
<tr>
<th>파라미터</th>
<th>의미</th>
</tr>
</thead>
<tbody><tr>
<td>num_leaves</td>
<td>최대 리프 수 (표현력 핵심)</td>
</tr>
<tr>
<td>max_depth</td>
<td>깊이 제한</td>
</tr>
<tr>
<td>min_data_in_leaf</td>
<td>과적합 방지</td>
</tr>
<tr>
<td>feature_fraction</td>
<td>피처 샘플링</td>
</tr>
<tr>
<td>bagging_fraction</td>
<td>데이터 샘플링</td>
</tr>
</tbody></table>
</li>
</ul>
</li>
</ul>
<h4 id="4-catboost">4) CatBoost</h4>
<p>: 범주형 피처 처리를 내부에서 안정적으로 수행하는 GBDT 구현체</p>
<ul>
<li>범주형 인코딩을 모델 내부에서 처리</li>
<li>타깃 누수 완화 전략 포함</li>
<li>기본 설정으로도 강한 성능</li>
<li>범주형 많은 데이터에 강하며 전처리 부담이 감소되고 안정적인 학습</li>
<li>데이터/환경에 따라 속도 차이가 나며, 튜닝 옵션 구조가 다른 계열과 다름</li>
</ul>
<h4 id="정리">정리</h4>
<table>
<thead>
<tr>
<th>모델</th>
<th>핵심 목적</th>
<th>강점</th>
<th>주의점</th>
</tr>
</thead>
<tbody><tr>
<td>GBDT</td>
<td>기본 부스팅</td>
<td>개념 단순</td>
<td>느릴 수 있음</td>
</tr>
<tr>
<td>XGBoost</td>
<td>안정+정규화</td>
<td>성능/안정 밸런스</td>
<td>파라미터 많음</td>
</tr>
<tr>
<td>LightGBM</td>
<td>속도+대규모</td>
<td>빠름/대용량</td>
<td>leaf-wise 과적합</td>
</tr>
<tr>
<td>CatBoost</td>
<td>범주형+누수 완화</td>
<td>범주형 강함</td>
<td>상황별 속도</td>
</tr>
</tbody></table>
<h3 id="총정리">총정리</h3>
<table>
<thead>
<tr>
<th>항목</th>
<th>Bagging</th>
<th>Boosting</th>
</tr>
</thead>
<tbody><tr>
<td>핵심 목표</td>
<td>분산 감소(안정화)</td>
<td>편향 감소(정교화)</td>
</tr>
<tr>
<td>방식</td>
<td>병렬로 여러 모델 → 평균/투표</td>
<td>순차로 계속 보정</td>
</tr>
<tr>
<td>회귀 결합</td>
<td>평균/중앙값</td>
<td>잔차(gradient) 누적</td>
</tr>
<tr>
<td>분류 결합</td>
<td>다수결/확률 평균</td>
<td>확률 공간에서 gradient 보정</td>
</tr>
<tr>
<td>과적합</td>
<td>비교적 덜함</td>
<td>더 쉬움(파라미터 중요)</td>
</tr>
<tr>
<td>대표</td>
<td>RF, ExtraTrees</td>
<td>GBDT, XGB, LGBM, Cat</td>
</tr>
</tbody></table>
