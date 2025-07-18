// hierarchical_ordered_logistic.stan
data {
  int<lower=0> N; // データ総数（タスクの数）
  int<lower=1> K; // 説明変数の数
  int<lower=1> J; // task_categoryの種類数
  array[N] int<lower=0, upper=10> y; // 目的変数 (usability_rating)
  matrix[N, K] X; // 説明変数の行列
  array[N] int<lower=1, upper=J> task_id; // 各データのtask_category ID
}
parameters {
  // 固定効果
  vector[K] beta; // 説明変数の係数
  
  // 変動効果 (task_category)
  real mu_alpha; // 階層の全体平均
  real<lower=0> sigma_alpha; // 階層の標準偏差 (必ず0以上)
  vector[J] alpha_task_raw; // non-centered parameterization用のパラメータ
  
  // 順序ロジスティック回帰のカットポイント
  ordered[9] c; // 0-10の評価なので9個の境界 (0|1, 1|2, ...)
}
transformed parameters {
  // non-centered parameterization
  // サンプリング効率を向上させるためのテクニック
  vector[J] alpha_task = mu_alpha + sigma_alpha * alpha_task_raw;
}
model {
  // --- 事前分布 ---
  // 係数 beta: 標準正規分布
  beta ~ normal(0, 1);
  
  // 階層の全体平均 mu_alpha: 標準正規分布
  mu_alpha ~ normal(0, 1);
  
  // 階層の標準偏差 sigma_alpha: 半t分布
  sigma_alpha ~ student_t(3, 0, 1);
  
  // non-centered parameterization用のパラメータ: 標準正規分布
  alpha_task_raw ~ normal(0, 1);
  
  // --- 尤度 ---
  vector[N] eta;
  for (n in 1 : N) {
    // 線形予測子
    eta[n] = alpha_task[task_id[n]] + X[n] * beta;
  }
  
  // 目的変数は順序ロジスティック分布に従う
  y ~ ordered_logistic(eta, c);
}
