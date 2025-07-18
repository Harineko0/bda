"""
コメントとその他のデータをマージして、最終的なデータセットを作成する
"""

import pandas as pd

# --- 設定項目 ---
# 入力ファイルのパス
FILE_PATHS = {
    'long_comments': 'dataset_for_bda/comments_long_clustered.csv',
    'public_data': 'dataset_modified/uicrit_public_with_id.csv',
    'task_category': 'dataset_modified/uicrit_id_task_category.csv',
    'comments_category': 'dataset_modified/uicrit_id_comments_category.csv'
}

# マージ後のデータを保存するファイル名
OUTPUT_CSV = 'dataset_for_bda/merged_comments_with_ratings.csv'


def merge_all_csv_files(file_paths: dict, output_file: str):
    """
    複数のCSVファイルをidをキーとしてマージし、一つのファイルに保存する。
    """
    dataframes = []
    print("CSVファイルを読み込んでいます...")
    try:
        # ベースとなるロングフォーマットのコメントデータ
        df_long = pd.read_csv(file_paths['long_comments'])
        print(f"- '{file_paths['long_comments']}' を読み込みました。 Shape: {df_long.shape}")
        
        # public_dataから不要な 'comments' 列を削除して読み込み
        df_public = pd.read_csv(file_paths['public_data']).drop(columns=['comments'], errors='ignore')
        print(f"- '{file_paths['public_data']}' を読み込みました。 Shape: {df_public.shape}")

        # その他のカテゴリデータ
        df_task_cat = pd.read_csv(file_paths['task_category'])
        print(f"- '{file_paths['task_category']}' を読み込みました。 Shape: {df_task_cat.shape}")

        df_comments_cat = pd.read_csv(file_paths['comments_category'])
        print(f"- '{file_paths['comments_category']}' を読み込みました。 Shape: {df_comments_cat.shape}")

        # マージするデータフレームのリストを作成
        # ベースのdf_longはreduceの外に置き、他のデータフレームを順にマージする
        dfs_to_merge = [df_public, df_task_cat, df_comments_cat]

    except FileNotFoundError as e:
        print(f"\nエラー: ファイルが見つかりません。 {e}")
        print("ファイルパスが正しいか確認してください。")
        return
    except Exception as e:
        print(f"\nエラー: ファイルの読み込み中に問題が発生しました。 {e}")
        return

    # --- 複数のデータフレームを順次マージ ---
    print("\n'id' をキーにデータフレームをマージしています...")
    
    # df_longをベースに、他のデータフレームを左結合（left join）でマージしていく
    # これにより、全てのコメント行が保持される
    merged_df = df_long
    for df in dfs_to_merge:
        merged_df = pd.merge(merged_df, df, on='id', how='left')
        
    # drop rico_id, task, comments_source
    merged_df = merged_df.drop(columns=['rico_id', 'task', 'comments_source'], errors='ignore')

    print("マージが完了しました。")

    # --- 結果の保存 ---
    try:
        # カラムの順序を整える
        # idと主要なカテゴリを先頭に持ってくる
        first_cols = ['id', 'task_category', 'comments_category']
        comment_cols = ['comment_problem', 'comment_verb', 'comment_obj']
        rating_cols = [col for col in merged_df.columns if 'rating' in col]
        other_cols = [col for col in merged_df.columns if col not in first_cols + comment_cols + rating_cols]
        
        final_order = first_cols + comment_cols + rating_cols + other_cols
        merged_df = merged_df[final_order]

        merged_df.to_csv(output_file, index=False)
        
        print(f"\n処理が完了しました。統合されたデータを '{output_file}' に保存しました。")
        print(f"最終的なデータのShape: {merged_df.shape}")
        print("\n最初の5行のプレビュー:")
        print(merged_df.head())

    except Exception as e:
        print(f"\nエラー: ファイルの保存中に問題が発生しました。 {e}")


if __name__ == '__main__':
    merge_all_csv_files(FILE_PATHS, OUTPUT_CSV)