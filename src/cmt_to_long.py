"""
コメントをロングフォーマットに変換する
"""

import pandas as pd
import sys
import re

# --- 設定 ---
# 変換したいCSVファイル名
INPUT_CSV = 'dataset_for_bda/comments_clustered.csv'
# 保存するCSVファイル名
OUTPUT_CSV = 'dataset_for_bda/comments_long_clustered.csv'
def transform_to_long_format(input_file: str, output_file: str):
    """
    ワイドフォーマットのCSVを読み込み、ロングフォーマットに変換して保存する。
    problem, verb, obj のいずれかが 'unknown' のコメントは除外する。
    """
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"エラー: 入力ファイル '{input_file}' が見つかりません。")
        return

    # 1. カラム名を wide_to_long が解釈できる形式にリネーム
    # 例: 'comment1_problem' -> 'problem_1'
    # 例: 'comment1_solution_verb' -> 'verb_1'
    # 例: 'comment1_solution_obj' -> 'obj_1'
    rename_map = {}
    for col in df.columns:
        # 正規表現でパターンに一致するかチェック
        match = re.match(r'comment(\d+)_(?:solution_)?(problem|verb|obj)', col)
        if match:
            comment_num = match.group(1)
            field_name = match.group(2)
            rename_map[col] = f"{field_name}_{comment_num}"
    
    df.rename(columns=rename_map, inplace=True)

    # 2. pd.wide_to_long を使ってデータを縦長に変換
    try:
        long_df = pd.wide_to_long(
            df,
            stubnames=['problem', 'verb', 'obj'], # 共通の接頭辞
            i='id',                             # 基準となるID列
            j='comment_number',                 # 元のコメント番号を保存する新しい列名
            sep='_',                            # 接頭辞と番号の区切り文字
            suffix=r'\d+'                       # 接尾辞のパターン（数字）
        ).reset_index()
    except ValueError as e:
        print(f"エラー: wide_to_longの変換に失敗しました。カラム名が期待通りでない可能性があります。")
        print(e)
        return

    # 3. problem, verb, obj のいずれかが 'unknown' の行を削除
    condition = (
        (long_df['problem'] != 'unknown') &
        (long_df['verb'] != 'unknown') &
        (long_df['obj'] != 'unknown')
    )
    filtered_df = long_df[condition].copy()

    # 4. 最終的なカラムを選択・リネームして保存
    final_df = filtered_df[['id', 'problem', 'verb', 'obj']]
    final_df.rename(columns={
        'problem': 'comment_problem',
        'verb': 'comment_verb',
        'obj': 'comment_obj'
    }, inplace=True)

    final_df.to_csv(output_file, index=False)
    print(f"処理が完了しました。ロングフォーマットのデータを '{output_file}' に保存しました。")
    print(f"変換前の有効なコメント数: {len(long_df)}, 'unknown'を除外した後のコメント数: {len(final_df)}")


if __name__ == '__main__':
    # 上記のINPUT_CSVとOUTPUT_CSVを実際のファイル名に書き換えて実行してください
    transform_to_long_format(INPUT_CSV, OUTPUT_CSV)