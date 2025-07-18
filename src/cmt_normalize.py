import pandas as pd
import re
import os

# --- 設定値 ---
INPUT_CSV = 'dataset_modified/uicrit_id_comments.csv'
OUTPUT_CSV = 'dataset_for_bda/comments_normalized.csv'
# 抽出するコメントの最大数
MAX_COMMENTS = 7

# --- メイン処理 ---
try:
    # 1. CSVファイルをDataFrameとして読み込む
    df = pd.read_csv(INPUT_CSV)

    # 2. コメント文字列をパースして分割する関数を定義
    def parse_comments(comment_string):
        """
        'comments'カラムの文字列から各コメントを抽出し、
        タイプとテキストに分割してSeriesオブジェクトとして返す。
        """
        pattern = r"((?:LLM\s)?Comment\s\d.*?(?:Bounding Box:.*?\]))"
        comments = re.findall(pattern, str(comment_string), re.DOTALL)
        
        extracted_data = {}
        for i, comment_text in enumerate(comments):
            if i >= MAX_COMMENTS:
                break
            
            cleaned_comment = comment_text.strip().strip("'\"").strip()
            parts = cleaned_comment.split('\\n', 1)
            
            print("parts", parts)
            
            # --- ここからが修正箇所 ---
            raw_type_header = parts[0].strip()
            comment_body = parts[1].strip() if len(parts) > 1 else ""
            
            # コメントのタイプを 'human' または 'llm' に分類
            if raw_type_header.startswith("LLM"):
                comment_type = "llm"
            else:
                comment_type = "human"
            # --- ここまでが修正箇所 ---
            
            extracted_data[f'comment{i+1}_type'] = comment_type
            extracted_data[f'comment{i+1}_text'] = comment_body
            
        return pd.Series(extracted_data)

    # 3. 'comments'カラムの各行に関数を適用し、新しいDataFrameを作成
    comments_df = df['comments'].apply(parse_comments)

    # 4. 新しいカラム名を定義
    new_columns = []
    for i in range(1, MAX_COMMENTS + 1):
        new_columns.append(f'comment{i}_type')
        new_columns.append(f'comment{i}_text')

    # 不足しているカラムをNaNで埋める
    comments_df = comments_df.reindex(columns=new_columns)

    # 5. 元の'id'カラムと、新しく作成したコメントのDataFrameを結合
    result_df = pd.concat([df['id'], comments_df], axis=1)

    # 6. 出力先のディレクトリが存在しない場合は作成
    output_dir = os.path.dirname(OUTPUT_CSV)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 7. 結果を新しいCSVファイルに保存
    result_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')

    print(f"✅ 処理が正常に完了しました。")
    print(f"出力ファイル: {OUTPUT_CSV}")
    print("\n--- 出力データの先頭5行 (id=3 のタイプが 'llm' になっています) ---")
    print(result_df.head())
    print("\n-------------------------------------------------------------")


except FileNotFoundError:
    print(f"❌ エラー: 入力ファイルが見つかりません。パスを確認してください: {INPUT_CSV}")
except Exception as e:
    print(f"❌ エラー: 処理中に問題が発生しました。")
    print(e)