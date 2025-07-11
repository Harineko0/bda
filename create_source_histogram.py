import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import ast
from collections import Counter

def create_source_histogram(
    input_file='uicrit_public.csv', 
    output_dir='plot_uicrit/'
):
    """
    CSVファイルの 'comments_source' 列を解析し、各ソース（human, llm, both）の
    出現回数を集計してヒストグラム（棒グラフ）として保存します。

    Args:
        input_file (str): 入力となるCSVファイル名。
        output_dir (str): 生成されたグラフを保存するディレクトリ。
    """
    # --- 1. データの読み込み ---
    print(f"'{input_file}' を読み込んでいます...")
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"エラー: 入力ファイル '{input_file}' が見つかりませんでした。")
        return
    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")
        return

    if 'comments_source' not in df.columns:
        print(f"エラー: '{input_file}' に 'comments_source' という列が見つかりません。")
        return

    # --- 2. 'comments_source' 列の解析と集計 ---
    print("'comments_source' 列を解析しています...")
    all_sources = []
    
    # 'comments_source' 列の各行をループ処理
    for item in df['comments_source'].dropna():
        try:
            # 文字列形式のリストをPythonのリストオブジェクトに安全に変換
            sources_list = ast.literal_eval(item)
            # 変換後のリストが本当にリスト形式か確認
            if isinstance(sources_list, list):
                all_sources.extend(sources_list)
        except (ValueError, SyntaxError):
            # 変換に失敗した場合はスキップ
            print(f"警告: '{item}' の解析に失敗しました。この行はスキップされます。")
            continue
            
    # 各ソースの出現回数をカウント
    source_counts = Counter(all_sources)
    
    # カウント結果をDataFrameに変換してプロットしやすくする
    df_counts = pd.DataFrame(source_counts.items(), columns=['Source', 'Count']).sort_values('Count', ascending=False)
    
    print("\n--- コメントソースの集計結果 ---")
    print(df_counts)
    
    # --- 3. ヒストグラム（棒グラフ）の作成と保存 ---
    print("\nヒストグラムを作成しています...")
    plt.figure(figsize=(8, 6))
    
    # seabornを使用して棒グラフを作成
    sns.barplot(x='Source', y='Count', data=df_counts, palette='viridis')
    
    plt.title('Distribution of Comment Sources', fontsize=16)
    plt.xlabel('Source Type', fontsize=12)
    plt.ylabel('Total Count', fontsize=12)
    
    # グラフの上部に余白を追加
    plt.ylim(0, df_counts['Count'].max() * 1.1)

    # 棒グラフの上に数値を表示
    for index, row in df_counts.iterrows():
        plt.text(row.name, row.Count, row.Count, color='black', ha="center", va="bottom")

    plt.tight_layout()

    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)
    
    # 画像を保存
    save_path = os.path.join(output_dir, 'comments_source_histogram.png')
    plt.savefig(save_path)
    plt.close()
    
    print(f"ヒストグラムを '{save_path}' に保存しました。")


if __name__ == '__main__':
    create_source_histogram()
