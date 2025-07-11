import pandas as pd
import matplotlib.pyplot as plt
import os

# CSVファイルへのパス
csv_file_path = 'dataset_modified/uicrit_id_task_category.csv'

# 保存する画像ファイル名
output_image_path = 'plot_uicrit/task_category_histogram.png'

# --- CSVデータ読み込み ---
try:
    # ファイルからデータを読み込む
    df = pd.read_csv(csv_file_path)
except FileNotFoundError:
    print(f"エラー: ファイルが見つかりません - {csv_file_path}")
    # サンプルデータで続行するためのダミーデータフレームを作成
    print("サンプルデータを使用してグラフを作成します。")
    data = {'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'comments_category': ['Layout', 'Text Readability', 'Layout', 'Layout', 
                                  'Usability of Buttons', 'Layout', 'Usability of Buttons', 
                                  'Text Readability', 'Usability of Buttons', 'Layout']}
    df = pd.DataFrame(data)
    # ダミーデータ用のディレクトリを作成
    if not os.path.exists('dataset_modified'):
        os.makedirs('dataset_modified')
    df.to_csv(csv_file_path, index=False)
    print(f"サンプルファイルを作成しました: {csv_file_path}")


# --- グラフ作成 ---
# 日本語文字化け対策（Mac/Linux向け、Windowsの場合は 'MS Gothic' などに変更）
plt.rcParams['font.family'] = 'Hiragino Sans'
plt.rcParams['font.size'] = 12

# グラフのサイズを指定
plt.figure(figsize=(10, 6))

# 'task_category' 列の各カテゴリの出現回数を棒グラフで表示
# value_counts()で集計し、降順でプロット
category_counts = df['task_category'].value_counts()
category_counts.plot(kind='bar', color='skyblue', edgecolor='black')

# グラフのタイトルとラベルを設定
plt.title('タスクカテゴリの分布', fontsize=16)
plt.xlabel('カテゴリ', fontsize=12)
plt.ylabel('件数', fontsize=12)

# x軸のラベルを読みやすいように回転
plt.xticks(rotation=45, ha='right')

# レイアウトを自動調整して、ラベルが見切れないようにする
plt.tight_layout()

# グリッド線を追加
plt.grid(axis='y', linestyle='--', alpha=0.7)


# --- 画像ファイルとして保存 ---
plt.savefig(output_image_path)

print(f"グラフを '{output_image_path}' として保存しました。")

# (オプション) グラフを画面に表示する場合
# plt.show()