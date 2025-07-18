"""_summary_
ロングフォーマットのコメントデータと元のメタデータをマージするスクリプト
"""
import pandas as pd

# --- 設定項目 ---
# ロングフォーマットのコメントデータCSVファイル
LONG_FORMAT_CSV = 'dataset_for_bda/comments_long_clustered.csv'
# 元のメタデータが含まれるCSVファイル
ORIGINAL_DATA_CSV = 'dataset_modified/uicrit_public_with_id.csv'
# マージ後のデータを保存するファイル名
MERGED_OUTPUT_CSV = 'dataset_for_bda/merged_comments_with_ratings.csv'

def merge_datasets(long_format_file: str, original_data_file: str, output_file: str):
    """
    ロングフォーマットのコメントデータと元のメタデータをマージする。
    """
    print("ファイルを読み込んでいます...")
    try:
        # ロングフォーマットのコメントデータを読み込む
        df_long = pd.read_csv(long_format_file)
        print(f"'{long_format_file}' を読み込みました。 Shape: {df_long.shape}")

        # 元のメタデータを読み込む
        df_original = pd.read_csv(original_data_file)
        print(f"'{original_data_file}' を読み込みました。 Shape: {df_original.shape}")
    except FileNotFoundError as e:
        print(f"エラー: ファイルが見つかりません。 {e}")
        return

    # 2. 元データからマージに不要な列（元のワイドフォーマットコメント）を削除
    #    こうすることで、マージ後のデータがすっきりします。
    #    'comments' 列なども不要であればリストに追加してください。
    cols_to_drop = [col for col in df_original.columns if 'comment' in col.lower()]
    df_original_subset = df_original.drop(columns=cols_to_drop, errors='ignore')
    print(f"元のデータから {len(cols_to_drop)} 個のコメント関連列を削除しました。")


    # 3. 'id' をキーとして2つのデータフレームをマージ
    #    how='left' にすることで、全てのコメント行が保持されます。
    print(f"'{long_format_file}' と '{original_data_file}' を 'id' をキーにマージします...")
    merged_df = pd.merge(
        df_long,
        df_original_subset,
        on='id',
        how='left'
    )

    # 4. 結果を保存
    try:
        merged_df.to_csv(output_file, index=False)
        print("\n処理が完了しました。")
        print(f"マージ後のデータを '{output_file}' に保存しました。")
        print(f"最終的なデータのShape: {merged_df.shape}")
        print("\n最初の5行のプレビュー:")
        print(merged_df.head())
    except Exception as e:
        print(f"エラー: ファイルの保存中に問題が発生しました。 {e}")


if __name__ == '__main__':
    # 上記のファイル名を実際のファイル名に合わせて実行してください
    merge_datasets(LONG_FORMAT_CSV, ORIGINAL_DATA_CSV, MERGED_OUTPUT_CSV)