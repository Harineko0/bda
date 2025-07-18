import pandas as pd
import os

# 統合するCSVファイルのパスをリストにまとめます
file_paths = [
    'dataset_modified/uicrit_public_with_id.csv',
    'dataset_modified/uicrit_id_task_category.csv',
    'dataset_modified/uicrit_id_comments_category.csv',
    'dataset_for_bda/comments_extracted.csv',
    'dataset_for_bda/tasks_extracted.csv'
]

# 出力先のディレクトリが存在しない場合に作成します
output_dir = 'dataset_for_bda'
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'merged2.csv')

try:
    # 最初のCSVファイルをベースとして読み込みます
    merged_df = pd.read_csv(file_paths[0])

    # 残りのCSVファイルを順番にマージします
    for file in file_paths[1:]:
        try:
            df_to_merge = pd.read_csv(file)
            # 'id'カラムをキーとして、左結合（left merge）でマージします
            # これにより、ベースのDataFrameの全レコードが保持されます
            merged_df = pd.merge(merged_df, df_to_merge, on='id', how='left')
        except FileNotFoundError:
            print(f"警告: ファイルが見つかりません {file}。このファイルはスキップされます。")
        except Exception as e:
            print(f"ファイル処理中にエラーが発生しました {file}: {e}")
            
    # id,rico_id,task_x,aesthetics_rating,learnability,efficency,usability_rating,design_quality_rating,comments_source,comments,task_category,comments_category,comment1_type,comment1_text,comment2_type,comment2_text,comment3_type,comment3_text,comment4_type,comment4_text,comment5_type,comment5_text,comment6_type,comment6_text,comment7_type,comment7_text,task_y,verb,obj
    merged_df = merged_df.drop(columns=['rico_id', 'task_x', 'comments_source', 'comments', 'comment1_type', 'comment1_text', 'comment2_type', 'comment2_text', 'comment3_type', 'comment3_text', 'comment4_type', 'comment4_text', 'comment5_type', 'comment5_text', 'comment6_type', 'comment6_text', 'comment7_type', 'comment7_text', 'task_y'], errors='ignore')
    merged_df['task_category'] = pd.factorize(merged_df['task_category'])[0]
    merged_df['comments_category'] = pd.factorize(merged_df['comments_category'])[0]
    merged_df['verb'] = pd.factorize(merged_df['verb'])[0]
    merged_df['obj'] = pd.factorize(merged_df['obj'])[0]

    # マージしたDataFrameを新しいCSVファイルとして保存します
    merged_df.to_csv(output_path, index=False)

    print(f"ファイルの統合が完了しました: {output_path}")
    print("\n統合後のファイルの先頭5行:")
    print(merged_df.head())

except FileNotFoundError:
    print(f"エラー: ベースファイルが見つかりません {file_paths[0]}。処理を続行できません。")
except Exception as e:
    print(f"エラーが発生しました: {e}")