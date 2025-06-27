import pandas as pd
import matplotlib.pyplot as plt
import os

def create_scatter_plot(file_path='uicrit_public.csv', x_column='aesthetics_rating', y_column='usability_rating', output_dir='plot_uicrit/'):
    """
    CSVファイルを読み込み、指定された2つの列から散布図を生成して保存します。

    Args:
        file_path (str): 入力CSVファイルのパス。
        x_column (str): 散布図のx軸に対応する列名。
        y_column (str): 散布図のy軸に対応する列名。
        output_dir (str): プロット画像を保存するディレクトリ。
    """
    # --- 1. データを読み込む ---
    try:
        # CSVファイルをpandas DataFrameに読み込む
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"エラー: ファイル '{file_path}' が見つかりませんでした。")
        return
    except Exception as e:
        print(f"CSVファイルの読み込み中にエラーが発生しました: {e}")
        return

    # --- 2. 必要な列が存在するか確認する ---
    if x_column not in df.columns or y_column not in df.columns:
        print(f"エラー: 必要な列 ('{x_column}' または '{y_column}') がCSVファイルに存在しません。")
        return

    # --- 3. 出力ディレクトリが存在しない場合は作成する ---
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"出力ディレクトリ '{output_dir}' の準備ができました。")
    except OSError as e:
        print(f"エラー: ディレクトリ '{output_dir}' を作成できませんでした。理由: {e}")
        return

    # --- 4. 散布図を生成して保存する ---
    print(f"'{y_column}' vs '{x_column}' の散布図を生成中...")

    plt.figure(figsize=(10, 8))  # プロット用の新しい図を作成

    # データを数値に変換し、非数値データはNaNとして扱う
    x_data = pd.to_numeric(df[x_column], errors='coerce')
    y_data = pd.to_numeric(df[y_column], errors='coerce')
    
    # xかyのどちらかがNaNである行を削除
    combined_data = pd.concat([x_data, y_data], axis=1).dropna()

    # 散布図を作成
    # alpha値を設定して点の重なりを可視化
    plt.scatter(combined_data[x_column], combined_data[y_column], alpha=0.5)

    # グラフのタイトルとラベルを設定
    plt.title(f'{y_column.replace("_", " ").title()} vs. {x_column.replace("_", " ").title()} Scatter Plot', fontsize=16)
    plt.xlabel(x_column.replace("_", " ").title(), fontsize=12)
    plt.ylabel(y_column.replace("_", " ").title(), fontsize=12)
    
    # グリッドを表示
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # 評価は整数値なので、軸の目盛りを整数に設定
    x_min, x_max = int(combined_data[x_column].min()), int(combined_data[x_column].max())
    y_min, y_max = int(combined_data[y_column].min()), int(combined_data[y_column].max())
    plt.xticks(range(x_min, x_max + 1))
    plt.yticks(range(y_min, y_max + 1))

    # 出力ファイルパスを定義
    save_path = os.path.join(output_dir, f'{y_column}_vs_{x_column}_scatter.png')

    # プロットをファイルに保存
    try:
        plt.savefig(save_path)
        print(f"散布図を '{save_path}' に保存しました。")
    except Exception as e:
        print(f"プロットを保存できませんでした。理由: {e}")
    
    plt.close()  # メモリを解放するために図を閉じる

if __name__ == '__main__':
    # このスクリプトは 'uicrit_public.csv' があるディレクトリから実行するか、
    # ファイルへのフルパスを指定してください。
    create_scatter_plot()
