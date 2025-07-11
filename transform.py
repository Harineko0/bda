import pandas as pd
import os

def process_csv_data(input_file_path: str, output_dir: str):
    """
    CSVファイルを読み込み、IDカラムの追加とデータの分割を行う関数

    Args:
        input_file_path (str): 入力となるCSVファイルのパス
        output_dir (str): 出力ファイルを保存するディレクトリのパス
    """
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(output_dir, exist_ok=True)

    try:
        # CSVファイルをpandasのDataFrameとして読み込む
        print(f"'{input_file_path}' を読み込んでいます...")
        df = pd.read_csv(input_file_path)

        # --- 1. 連番IDカラムの追加 ---
        # DataFrameの左端(0列目)に1から始まる連番の'id'カラムを挿入
        df.insert(0, 'id', range(1, len(df) + 1))

        # ID追加後のデータをCSVファイルとして保存
        output_with_id_path = os.path.join(output_dir, 'uicrit_public_with_id.csv')
        df.to_csv(output_with_id_path, index=False, encoding='utf-8-sig')
        print(f"IDカラムを追加したデータを '{output_with_id_path}' に保存しました。")

        # --- 2. データの分割と保存 ---
        # idとcommentsカラムのみを抽出
        df_comments = df[['id', 'comments']]
        output_comments_path = os.path.join(output_dir, 'uicrit_id_comments.csv')
        df_comments.to_csv(output_comments_path, index=False, encoding='utf-8-sig')
        print(f"IDとコメントデータを '{output_comments_path}' に保存しました。")

        # idとtaskカラムのみを抽出
        df_task = df[['id', 'task']]
        output_task_path = os.path.join(output_dir, 'uicrit_id_task.csv')
        df_task.to_csv(output_task_path, index=False, encoding='utf-8-sig')
        print(f"IDとタスクデータを '{output_task_path}' に保存しました。")

        print("\nすべての処理が完了しました。")

    except FileNotFoundError:
        print(f"エラー: ファイル '{input_file_path}' が見つかりません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == '__main__':
    # 入力ファイルと出力ディレクトリを指定
    # このスクリプトを `dataset` ディレクトリと同じ階層に置いて実行することを想定しています。
    INPUT_CSV = 'dataset/uicrit_public.csv'
    OUTPUT_DIRECTORY = 'dataset_modified'

    process_csv_data(INPUT_CSV, OUTPUT_DIRECTORY)
