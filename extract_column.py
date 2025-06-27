import pandas as pd

def extract_column_to_csv(input_file='uicrit_public_task_category.csv', columns=['rico_id'], output_file='uicrit_public_task_category_id.csv'):
    """
    CSVファイルから指定された列を抽出し、新しいCSVファイルとして保存します。

    Args:
        input_file (str): 入力となるCSVファイル名。
        columns (list): 抽出する列のリスト。デフォルトは ['id', 'task']。
        output_file (str): 出力するCSVファイル名。
    """
    try:
        # 1. 元のCSVファイルを読み込む
        print(f"'{input_file}' を読み込んでいます...")
        df = pd.read_csv(input_file)
        
        # 2. 指定された列が存在するか確認する
        if not all(col in df.columns for col in columns):
            missing_cols = [col for col in columns if col not in df.columns]
            raise ValueError(f"指定された列 {missing_cols} がCSVファイルに存在しません。")
            
        # 3. 指定された列だけを抽出する
        task_columns = df[columns]
        
        
        # 4. 新しいCSVファイルとして保存する
        # index=False を指定して、行番号（インデックス）がファイルに書き出されるのを防ぐ
        task_columns.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"'{columns}' 列の抽出に成功しました。")
        print(f"'{output_file}' として保存されました。")

    except FileNotFoundError:
        print(f"エラー: 入力ファイル '{input_file}' が見つかりませんでした。")
    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")

if __name__ == '__main__':
    extract_column_to_csv()
