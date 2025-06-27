import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import os
import re
import ast

def create_word_cloud(file_path='uicrit_public.csv', output_dir='plot_uicrit/'):
    """
    CSVファイルの 'comments' 列からテキストデータを抽出し、
    ワードクラウドを生成して画像として保存します。

    Args:
        file_path (str): 入力CSVファイルのパス。
        output_dir (str): プロット画像を保存するディレクトリ。
    """
    # --- 1. データの読み込み ---
    try:
        df = pd.read_csv(file_path)
        print("CSVファイルの読み込みに成功しました。")
    except FileNotFoundError:
        print(f"エラー: ファイル '{file_path}' が見つかりませんでした。")
        return
    except Exception as e:
        print(f"CSVファイルの読み込み中にエラーが発生しました: {e}")
        return

    if 'comments' not in df.columns:
        print("エラー: 'comments' 列がCSVファイルに存在しません。")
        return

    # --- 2. テキストデータの前処理 ---
    print("コメントデータを処理しています...")
    all_comments_text = ''
    
    # 'comments'列の各行を処理
    for index, row in df.iterrows():
        try:
            # 文字列形式のリストを実際のリストに変換
            comments_list = ast.literal_eval(row['comments'])
            # リスト内の各コメントを結合
            full_comment_for_row = ' '.join(comments_list)
            all_comments_text += ' ' + full_comment_for_row
        except (ValueError, SyntaxError):
            # 変換に失敗した場合はスキップ
            print(f"警告: 行 {index} のコメントを解析できませんでした。スキップします。")
            continue

    # テキストを小文字に変換
    all_comments_text = all_comments_text.lower()
    
    # 正規表現で不要な部分（'Comment X', 'Bounding Box', 数字, 記号）を削除
    all_comments_text = re.sub(r'comment \d+', '', all_comments_text)
    all_comments_text = re.sub(r'bounding box', '', all_comments_text)
    all_comments_text = re.sub(r'\[.*?\]', '', all_comments_text) # 括弧と中身を削除
    all_comments_text = re.sub(r'[^a-zA-Z\s]', '', all_comments_text) # アルファベットと空白以外を削除

    # --- 3. ストップワードの設定 ---
    # ストップワード（分析に不要な一般的な単語）を設定
    # デフォルトのストップワードに、このデータセット特有の不要語を追加
    custom_stopwords = {
        'make', 'use', 'fix', 'this', 'user', 'users', 'page', 'text', 'font',
        'expected', 'standard', 'current', 'design', 'should', 'easy', 'read',
        'difficult', 'better', 'good', 'bad', 'screen', 'information', 'element',
        'elements', 'layout', 'provide', 'change', 'increase', 'decrease'
    }
    stopwords = STOPWORDS.union(custom_stopwords)
    
    # --- 4. ワードクラウドの生成と保存 ---
    print("ワードクラウドを生成しています...")
    try:
        wordcloud = WordCloud(
            width=1200, 
            height=800, 
            background_color='white',
            stopwords=stopwords,
            colormap='viridis',
            min_font_size=10
        ).generate(all_comments_text)

        # 出力ディレクトリを作成
        os.makedirs(output_dir, exist_ok=True)

        # Matplotlibを使用してプロットを表示・保存
        plt.figure(figsize=(10, 7), facecolor=None)
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout(pad=0)
        
        # 画像を保存
        save_path = os.path.join(output_dir, 'comments_wordcloud.png')
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

        print(f"ワードクラウドを '{save_path}' に保存しました。")

    except Exception as e:
        print(f"ワードクラウドの生成中にエラーが発生しました: {e}")
        print("コメントデータが空か、処理後に単語が残らなかった可能性があります。")


if __name__ == '__main__':
    create_word_cloud()
