import pandas as pd
from sklearn.preprocessing import StandardScaler
from cmdstanpy import CmdStanModel
import numpy as np
import arviz as az
import matplotlib.pyplot as plt

# --- 設定項目 ---
# マージ済みのCSVファイル
INPUT_CSV = 'dataset_for_bda/merged_comments_with_ratings.csv'
# Stanモデルファイル
STAN_FILE = 'src/stan/1/hierarchical_ordered_logistic.stan'


def prepare_data(input_file: str) -> dict:
    """
    CSVファイルを読み込み、集計と前処理を行い、Stanに渡すデータ辞書を作成する。
    """
    print(f"'{input_file}' を読み込んでいます...")
    df_merged = pd.read_csv(input_file)
    
    print("カテゴリ変数を数値コードに変換しています...")
    cols_to_factorize = [
        'task_category',
        'comments_category',
        'comment_problem',
        'comment_verb',
        'comment_obj'
    ]
    for col in cols_to_factorize:
        if col in df_merged.columns:
            df_merged[col] = pd.factorize(df_merged[col])[0]
        else:
            print(f"警告: カラム '{col}' が見つかりませんでした。スキップします。")

    # --- 1. データ準備：集約と特徴量エンジニアリング ---
    print("コメントデータをタスクIDごとに集約しています...")

    df_problems_onehot = pd.get_dummies(df_merged[['id', 'comment_problem']],
                                        columns=['comment_problem'],
                                        prefix='count_problem')

    df_aggregated = df_problems_onehot.groupby('id').sum()

    df_tasks = df_merged.drop_duplicates(subset='id').set_index('id')
    df_model_input = df_tasks.join(df_aggregated)
    df_model_input.reset_index(inplace=True)

    # nan を 0 で埋める
    problem_count_vars = [col for col in df_model_input.columns if 'count_problem_' in col]
    df_model_input[problem_count_vars] = df_model_input[problem_count_vars].fillna(0)

    print("データ集約が完了しました。")

    # --- 2. 変数選択とStan用データ作成 ---
    print("Stanモデル用のデータを準備しています...")

    y = df_model_input['usability_rating'].astype(int)

    control_vars = ['aesthetics_rating', 'learnability', 'efficency', 'design_quality_rating']
    problem_count_vars = [col for col in df_model_input.columns if 'count_problem_' in col]
    predictor_vars = control_vars + problem_count_vars
    
    # 1. スケーラーを準備
    scaler = StandardScaler()
    
    # 2. 元のdf_model_inputのcontrol_vars列を直接標準化して上書きする
    df_model_input[control_vars] = scaler.fit_transform(df_model_input[control_vars])
    
    # 3. 修正されたdf_model_inputからXを作成する
    X = df_model_input[predictor_vars]
    
    # 3.5 Save X to tmp CSV file for debugging
    X.to_csv('tmp_X.csv', index=False)
    
    # 4. NaNチェック
    # if X.isnull().sum().sum() > 0:
    #     print("\n致命的なエラー: 説明変数XにNaNが含まれています。処理を中断します。")
    #     print(X.isnull().sum()[X.isnull().sum() > 0])
    #     print("NaNが含まれるカラム:", X.columns[X.isnull().any()].tolist())
    #     print("NaNが含まれる行数:", X[X.isnull().any(axis=1)].shape[0])
    #     exit() # プログラムを終了
    # else:
    #     print("説明変数XのNaNチェック... 問題ありません。")

    task_id = df_model_input['task_category'] + 1 # task_categoryは数値である必要がある

    stan_data = {
        'N': len(df_model_input),
        'K': X.shape[1],
        'J': task_id.nunique(),
        'y': y.values,
        'X': X.values,
        'task_id': task_id.values,
    }
    
    stan_data['predictor_names'] = predictor_vars

    return stan_data

def plot(fit):
    # (ArviZの変換コードは同じ)
    idata = az.from_cmdstanpy(
        posterior=fit,
        coords={'predictor': predictor_names},
        dims={'beta': ['predictor']}
    )

    # フォレストプロットを描画
    az.plot_forest(
        idata,
        var_names=['beta'],
        filter_vars="regex",
        combined=True,
        hdi_prob=0.94,
        figsize=(10, 8),
        r_hat=False
    )
    plt.title('Effect of UI Problems on Usability Rating (beta coefficients)')

    # -------------------------------------------------
    # 変更点: plt.show() の代わりに plt.savefig() を使う
    # -------------------------------------------------
    plt.savefig('beta_forest_plot.png', dpi=300, bbox_inches='tight')
    plt.close() # メモリ解放のためにプロットを閉じるのが良い習慣です
    # -------------------------------------------------

    print("フォレストプロットを 'beta_forest_plot.png' として保存しました。")
    
    # トレースプロットを描画
    az.plot_trace(idata, var_names=['mu_alpha', 'sigma_alpha'])
    plt.tight_layout()

    # 画像として保存
    plt.savefig('trace_plot.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("トレースプロットを 'trace_plot.png' として保存しました。")

def main():
    """
    メイン処理
    """
    # データの準備
    stan_data = prepare_data(INPUT_CSV)
    predictor_names = stan_data.pop('predictor_names') # Stanに渡さないので取り出しておく

    # Stanモデルのコンパイル
    print(f"'{STAN_FILE}' をコンパイルしています...")
    try:
        model = CmdStanModel(stan_file=STAN_FILE)
    except Exception as e:
        print(f"モデルのコンパイル中にエラーが発生しました: {e}")
        return

    # MCMCサンプリングの実行
    print("MCMCサンプリングを実行しています...（数分かかる場合があります）")
    fit = model.sample(
        data=stan_data,
        seed=1234,
        chains=4,
        parallel_chains=4,
        iter_warmup=1000,
        iter_sampling=1000,
        show_progress=True
    )
    
    # 収束診断
    print("\n収束診断 (Rhat < 1.05 が望ましい):")
    print(fit.diagnose())

    # 結果の要約
    print("\n推定結果の要約:")
    summary_df = fit.summary()
    # βの係数名を設定
    beta_rows = [f'beta[{i+1}]' for i in range(len(predictor_names))]
    summary_df.loc[beta_rows, 'Variable'] = predictor_names
    
    # 関心のあるパラメータのみ表示
    display_vars = ['beta', 'mu_alpha', 'sigma_alpha']
    print(summary_df[summary_df.index.str.contains('|'.join(display_vars))])
    
    # プロットの生成
    plot(fit)


if __name__ == '__main__':
    main()