import pandas as pd

# --- 設定項目 ---
# 修正対象のファイル
TARGET_CSV = 'dataset_for_bda/merged_comments_with_ratings.csv'
# 正しい'learnability'の値が含まれるソースファイル
SOURCE_CSV = 'uicrit_public.csv'

def fix_learnability_column(target_file: str, source_file: str):
    """
    target_fileの'learnability'列を、source_fileの値を使って修正する。
    source_fileの値がNaNの場合は、元の値を維持する。
    """
    print("データ修正プロセスを開始します...")
    try:
        # 1. 修正対象とソースのCSVファイルを読み込む
        df_target = pd.read_csv(target_file)
        df_source = pd.read_csv(source_file)
        print(f"'{target_file}' と '{source_file}' を正常に読み込みました。")

        # 修正前のlearnabilityの統計情報を表示
        print(f"\n修正前の '{target_file}' の 'learnability' の統計情報:\n{df_target['learnability'].describe()}")

        # 2. ソースデータに連番の 'id' を追加して、ターゲットデータと対応付ける
        #    (1から始まる連番)
        df_source['id'] = range(1, len(df_source) + 1)
        print("\nソースデータに連番の 'id' を追加しました。")

        # 3. ソースデータから 'id' と 'learnability' の対応辞書（マップ）を作成
        correct_learnability_map = df_source.set_index('id')['learnability']
        print("ソースデータから 'id' と 'learnability' の対応マップを作成しました。")

        # 4. ターゲットデータの 'id' を使って、対応する正しい 'learnability' の値を取得
        new_learnability_series = df_target['id'].map(correct_learnability_map)

        # 5. 修正を実行
        #    ソースから取得した値がNaNでない行のみを更新するマスクを作成
        update_mask = new_learnability_series.notna()
        
        num_to_update = update_mask.sum()
        if num_to_update > 0:
            # .locを使って、マスクがTrueの行の'learnability'列のみを更新
            df_target.loc[update_mask, 'learnability'] = new_learnability_series[update_mask]
            print(f"\n'learnability' 列を更新します。最大 {df_target['id'].nunique()} 件中、{num_to_update // df_target['id'].value_counts().iloc[0]} 件のタスクデータが修正対象です。")
        else:
            print("\n更新対象のデータが見つかりませんでした。")

        # 6. 修正後のファイルを上書き保存
        df_target.to_csv(target_file, index=False)
        print(f"\n修正が完了しました。'{target_file}' は正常に更新されました。")
        print(f"\n修正後の '{target_file}' の 'learnability' の統計情報:\n{df_target['learnability'].describe()}")

    except FileNotFoundError as e:
        print(f"\nエラー: ファイルが見つかりません。 {e}")
        print("スクリプトと同じ階層にCSVファイルが正しく配置されているか確認してください。")
    except Exception as e:
        print(f"\n予期せぬエラーが発生しました: {e}")

if __name__ == '__main__':
    fix_learnability_column(TARGET_CSV, SOURCE_CSV)