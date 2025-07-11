import pandas as pd
import os
import re
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# --- 1. 定数定義: ファイルパスとディレクトリを設定 ---
INPUT_CSV_PATH = 'dataset_modified/uicrit_id_comments.csv'
OUTPUT_DIR = 'dataset_modified/'
OUTPUT_CSV_PATH = os.path.join(OUTPUT_DIR, 'uicrit_public_with_tfidf.csv')

# --- 2. クリーニング関数 ---
def clean_and_parse_comments(comment_str: str) -> list[str]:
    """
    不正な形式のリスト文字列をクリーニングし、文字列のPythonリストにパースします。
    `""...""` のような不正な引用符の問題を修正します。
    """
    # 文字列でない、またはリスト形式でない場合は空のリストを返す
    if not isinstance(comment_str, str) or not comment_str.startswith('[') or not comment_str.endswith(']'):
        return []
    
    my_list = ast.literal_eval(comment_str)
    # 2. リストの要素をスペースで結合
    result = ' '.join(my_list)
    pattern = r"Bounding Box:\s*\[(?:\s*-?\d+(?:\.\d+)?\s*,?){4}\]"
    result = re.sub(pattern, "", result).strip()
    print(f"クリーニング後のコメント: {result}")
    return result

# --- 3. メイン処理ロジック ---
def process_csv_and_add_tfidf(input_path, output_path):
    """
    CSVを読み込み、'comments'列をクリーニングし、TF-IDFを計算して新しい列として追加し、
    結果を保存します。
    """
    print(f"ファイルを読み込んでいます: {input_path}...")
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"エラー: 入力ファイルが見つかりません {input_path}")
        return

    print("'comments'列をクリーニングしています...")
    # クリーニング関数を 'comments' 列の各行に適用
    df['comments_cleaned'] = df['comments'].apply(clean_and_parse_comments)

    # print("TF-IDF処理のためにクリーニングされたコメントを結合しています...")
    # # TF-IDF計算のため、コメントのリストを一つの文字列に結合
    # df['comments_full_text'] = df['comments_cleaned'].apply(lambda comments: ' '.join(comments))

    # クリーニング後に空になった行を空文字列で埋める
    # df['comments_full_text'].fillna('', inplace=True)

    print("TF-IDFベクトルを計算しています...")
    # TF-IDF Vectorizerを初期化
    # stop_words='english': 英語の一般的な単語（ストップワード）を除外
    # max_features: 使用する単語数を制限（メモリ使用量を抑えるため）
    stopwords = [
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
        "you", "your", "yours", "yourself", "yourselves",
        "he", "him", "his", "himself", "she", "her", "hers", "herself",
        "it", "its", "itself", "they", "them", "theirs", "theirs", "themselves",
        "what", "which", "who", "whom", "this", "that", "these", "those",
        "am", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "having", "do", "does", "did", "doing",
        "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while",
        "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during",
        "before", "after", "above", "below", "to", "from", "up", "down",
        "in", "out", "on", "off", "over", "under",
        "again", "further", "then", "once", "here", "there", "when", "where", "why", "how",
        "all", "any", "both", "each", "few", "more", "most", "other", "some", "such",
        "no", "nor", "not", "only", "own",
        "same", "so", "than", "too", "very",
        # dataset specific stopwords
        "The", "the", "expected", "standard", "To", "fix", "current", "design", "LLM", "Comment",
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
       
        
    ]
    vectorizer = TfidfVectorizer(stop_words=stopwords, max_features=5000)

    # テキストデータにVectorizerを適合させ、TF-IDFベクトルに変換
    tfidf_matrix = vectorizer.fit_transform(df['comments_cleaned'])

    feature_names = vectorizer.get_feature_names_out()
    # 疎行列を密な配列に変換し、語彙を列名としてDataFrameを作成
    df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)
    
    # TF-IDFの列だと分かりやすいように、列名の先頭にプレフィックスを追加
    df_tfidf = df_tfidf.add_prefix('tfidf_')

    print("元のDataFrameとTF-IDFのDataFrameを結合しています...")
    # 元のDataFrameから、処理に使用した中間列と元の'comments'列を削除
    df_original = df.drop(columns=['comments', 'comments_cleaned'])

    # 元のデータとTF-IDFデータを列方向に結合
    df_final = pd.concat([df_original, df_tfidf], axis=1)

    print(f"変更後のデータを保存しています: {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_final.to_csv(output_path, index=False, encoding='utf-8')
    print("--- 全ての処理が完了しました ---")
    
    # 結果の確認
    print(f"\n処理後のDataFrameの形状 (行, 列): {df_final.shape}")
    # 表示する列が多すぎるため、最初の15列のみを表示
    print(f"\n処理後のDataFrameの先頭5行（一部の列）:\n{df_final.iloc[:, :15].head()}")
    print(f"\n出力ファイル '{output_path}' にTF-IDFベクトルが展開された列が追加されました。")

# --- 4. スクリプトの実行 ---
if __name__ == "__main__":
    process_csv_and_add_tfidf(INPUT_CSV_PATH, OUTPUT_CSV_PATH)
