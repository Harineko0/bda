import pandas as pd

def process_id_column(input_file_path, output_file_path):
    """
    CSVファイルを読み込み、'id'カラムの2475以上の数字を1増加させて
    新しいCSVファイルとして保存します。

    Args:
        input_file_path (str): 入力CSVファイルのパス。
        output_file_path (str): 出力CSVファイルのパス。
    """
    try:
        # CSVファイルを読み込む
        df = pd.read_csv(input_file_path)

        # 'id'カラムが存在するか確認
        if 'id' not in df.columns:
            print(f"エラー: CSVファイルに 'id' カラムが見つかりません。")
            return

        # 2475以上の数字を1増加させる関数
        def increment_id_if_above_threshold(id_value):
            try:
                num = int(id_value)
                if num >= 2475:
                    return num + 1
                else:
                    return num
            except ValueError:
                # 数字でない場合はそのまま返す
                return id_value

        # 'id'カラムに適用
        df['id'] = df['id'].apply(increment_id_if_above_threshold)

        # 修正されたDataFrameを新しいCSVファイルとして保存
        df.to_csv(output_file_path, index=False)
        print(f"修正されたデータは '{output_file_path}' に保存されました。")

    except FileNotFoundError:
        print(f"エラー: 指定された入力ファイル '{input_file_path}' が見つかりません。")
    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")

# 使用例
input_csv_path = 'dataset_modified/uicrit_id_task_corrected.csv'
output_csv_path = 'dataset_modified/uicrit_id_task_corrected_incremented.csv'

process_id_column(input_csv_path, output_csv_path)