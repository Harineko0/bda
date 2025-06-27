import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def analyze_ratings_by_category(
    main_file='uicrit_public.csv', 
    category_file='uicrit_public_task_category.csv', 
    output_dir='plot_uicrit_by_category/'
):
    """
    メインの評価データとタスクカテゴリデータを結合し、カテゴリ別の分析を行います。
    1. カテゴリごとのサンプルサイズを計算し、グラフ化します。
    2. カテゴリごとの評価の平均値を計算して表示します。
    3. カテゴリごとの評価のヒストグラムを生成し、保存します。
    4. カテゴリごとの評価の相関ヒートマップを生成し、保存します。

    Args:
        main_file (str): UI評価データが含まれるメインのCSVファイル。
        category_file (str): タスクカテゴリ情報が含まれるCSVファイル。
        output_dir (str): 生成されたグラフを保存するディレクトリ。
    """
    # --- 1. データの読み込みと結合 ---
    print("--- データの読み込みと結合 ---")
    try:
        df_main = pd.read_csv(main_file)
        df_category = pd.read_csv(category_file)
        print("CSVファイルの読み込みに成功しました。")
    except FileNotFoundError as e:
        print(f"エラー: ファイルが見つかりません。({e.filename})")
        return

    # ファイルの行数が一致するか確認
    if len(df_main) != len(df_category):
        print("エラー: 2つのCSVファイルの行数が異なります。処理を中断します。")
        return

    # 'task_category' 列をメインのデータフレームに追加
    df_merged = pd.concat([df_main, df_category['task_category']], axis=1)
    print("データの結合が完了しました。\n")

    # --- 2. 評価スケールの調整とデータ準備 ---
    print("--- 評価スケールの調整 ---")
    columns_to_scale = ['aesthetics_rating', 'usability_rating', 'design_quality_rating']
    for col in columns_to_scale:
        if col in df_merged.columns:
            df_merged[col] = df_merged[col] / 2.0
    
    rating_columns = [
        'aesthetics_rating', 'learnability', 'efficency', 
        'usability_rating', 'design_quality_rating'
    ]
    
    # 評価データを数値に変換し、欠損値を含む行を削除
    for col in rating_columns:
        df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce')
    df_merged = df_merged.dropna(subset=rating_columns + ['task_category'])

    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)
    print(f"出力ディレクトリ '{output_dir}' の準備ができました。\n")

    # --- 3. 分析の実行 ---
    
    # 分析1: task category ごとのサンプルサイズ
    print("--- 分析1: カテゴリごとのサンプルサイズ ---")
    category_counts = df_merged['task_category'].value_counts()
    print(category_counts)
    
    plt.figure(figsize=(12, 7))
    sns.barplot(x=category_counts.index, y=category_counts.values, palette='viridis')
    plt.title('Sample Size per Task Category', fontsize=16)
    plt.xlabel('Task Category', fontsize=12)
    plt.ylabel('Number of Samples', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    save_path = os.path.join(output_dir, 'hist_sample_size_by_category.png')
    plt.savefig(save_path)
    plt.close()
    print(f"\nサンプルサイズのグラフを '{save_path}' に保存しました。")
    print("\n" + "="*60 + "\n")
    
    # 分析2: task category ごとの rating の平均値
    print("--- 分析2: カテゴリごとの平均評価 ---")
    mean_ratings = df_merged.groupby('task_category')[rating_columns].mean()
    print(mean_ratings)
    print("\n" + "="*60 + "\n")

    # 分析3: task category ごとの rating のヒストグラム
    print("--- 分析3: カテゴリごとの評価ヒストグラム ---")
    for rating_col in rating_columns:
        plt.figure(figsize=(12, 7))
        sns.histplot(data=df_merged, x=rating_col, hue='task_category', multiple='dodge', shrink=0.8, bins=10)
        plt.title(f'Distribution of {rating_col.replace("_", " ").title()} by Task Category', fontsize=16)
        plt.xlabel(f'{rating_col.replace("_", " ").title()} (5-point scale)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.tight_layout()
        
        save_path = os.path.join(output_dir, f'hist_{rating_col}_by_category.png')
        plt.savefig(save_path)
        plt.close()
        print(f"ヒストグラムを '{save_path}' に保存しました。")
    print("\n" + "="*60 + "\n")

    # 分析4: task category ごとの相関行列とヒートマップ
    print("--- 分析4: カテゴリごとの相関ヒートマップ ---")
    categories = df_merged['task_category'].unique()
    for category in categories:
        df_cat = df_merged[df_merged['task_category'] == category]
        
        # カテゴリ内のデータが少なすぎる場合はスキップ
        if len(df_cat) < 2:
            print(f"カテゴリ '{category}' はデータが少ないため、相関ヒートマップをスキップします。")
            continue
            
        correlation_matrix = df_cat[rating_columns].corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            correlation_matrix, 
            annot=True, 
            cmap='coolwarm', 
            fmt='.2f', 
            linewidths=.5,
            vmin=-1, vmax=1  # 色の範囲を-1から1に固定
        )
        plt.title(f'Correlation Heatmap for: {category}', fontsize=16)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        # ファイル名として使えない文字を置換
        safe_category_name = category.replace(" ", "_").replace("/", "_")
        save_path = os.path.join(output_dir, f'heatmap_{safe_category_name}.png')
        plt.savefig(save_path)
        plt.close()
        print(f"ヒートマップを '{save_path}' に保存しました。")
    print("\n" + "="*60)

if __name__ == '__main__':
    analyze_ratings_by_category()
