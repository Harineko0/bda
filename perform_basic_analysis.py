import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def perform_basic_analysis(file_path='uicrit_public.csv', output_dir='plot_uicrit/'):
    """
    CSVファイルを読み込み、基礎的なデータ分析を実行します。
    1. 記述統計量をコンソールに出力します。
    2. 評価指標間の相関ヒートマップを生成し、画像として保存します。
    3. 各評価指標の分布を比較する箱ひげ図を生成し、画像として保存します。

    Args:
        file_path (str): 入力CSVファイルのパス。
        output_dir (str): プロット画像を保存するディレクトリ。
    """
    # --- データの読み込み ---
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"エラー: ファイル '{file_path}' が見つかりませんでした。")
        return
    except Exception as e:
        print(f"CSVファイルの読み込み中にエラーが発生しました: {e}")
        return

    # --- 評価スケールの調整 ---
    # 5段階評価以外の指標を5段階評価に合わせるため、2で割る
    columns_to_scale = [
        'aesthetics_rating',
        'usability_rating',
        'design_quality_rating'
    ]
    print("--- 評価スケールの調整 ---")
    for col in columns_to_scale:
        if col in df.columns:
            df[col] = df[col] / 2.0
            print(f"列 '{col}' の値を 1/2 にしました。")
        else:
            print(f"警告: スケール調整対象の列 '{col}' が見つかりません。")
    print("\n" + "="*50 + "\n")


    # --- 分析対象の列と出力ディレクトリの準備 ---
    rating_columns = [
        'aesthetics_rating',
        'learnability',
        'efficency',
        'usability_rating',
        'design_quality_rating'
    ]
    
    # 存在しない列があれば警告を出し、リストから削除
    for col in list(rating_columns): # イテレート中にリストを変更するためコピーをループ
        if col not in df.columns:
            print(f"警告: 列 '{col}' がファイルに存在しません。分析から除外されます。")
            rating_columns.remove(col)

    # データを数値に変換
    df_ratings = df[rating_columns].apply(pd.to_numeric, errors='coerce').dropna()

    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)
    print(f"出力ディレクトリ '{output_dir}' の準備ができました。\n")

    # --- 1. 記述統計量の要約 ---
    print("--- 1. 記述統計量の要約 ---")
    # .describe()を使用して統計情報を生成し、表示
    descriptive_stats = df_ratings.describe()
    print(descriptive_stats)
    print("\n" + "="*50 + "\n")


    # --- 2. 相関行列とヒートマップの作成 ---
    print("--- 2. 相関ヒートマップの生成 ---")
    try:
        plt.figure(figsize=(10, 8))
        
        # 相関行列を計算
        correlation_matrix = df_ratings.corr()
        
        # seabornのheatmapを使用して可視化
        sns.heatmap(
            correlation_matrix, 
            annot=True,          # 数値をセルに表示
            cmap='coolwarm',     # 色のテーマ
            fmt='.2f',           # 小数点以下2桁まで表示
            linewidths=.5
        )
        
        plt.title('Correlation Heatmap of UI/UX Ratings (Scaled)', fontsize=16)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout() # レイアウトを自動調整

        # 画像を保存
        save_path_heatmap = os.path.join(output_dir, 'correlation_heatmap.png')
        plt.savefig(save_path_heatmap)
        plt.close()
        print(f"相関ヒートマップを '{save_path_heatmap}' に保存しました。")
    except Exception as e:
        print(f"ヒートマップの生成中にエラーが発生しました: {e}")
    
    print("\n" + "="*50 + "\n")

    # --- 3. 箱ひげ図による比較 ---
    print("--- 3. 箱ひげ図の生成 ---")
    try:
        plt.figure(figsize=(12, 7))
        
        # seabornのboxplotを使用して可視化
        sns.boxplot(data=df_ratings)
        
        plt.title('Distribution of UI/UX Ratings (Scaled)', fontsize=16)
        plt.ylabel('Rating Score (5-point scale)', fontsize=12)
        plt.xlabel('Rating Categories', fontsize=12)
        plt.xticks(rotation=15)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout() # レイアウトを自動調整

        # 画像を保存
        save_path_boxplot = os.path.join(output_dir, 'ratings_boxplot.png')
        plt.savefig(save_path_boxplot)
        plt.close()
        print(f"箱ひげ図を '{save_path_boxplot}' に保存しました。")

    except Exception as e:
        print(f"箱ひげ図の生成中にエラーが発生しました: {e}")
    
    print("\n" + "="*50)


if __name__ == '__main__':
    perform_basic_analysis()
