import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import japanize_matplotlib  # 日本語化ライブラリ
from wordcloud import WordCloud
import os

# --- 設定 ---
# CSVファイル名
CSV_FILE = 'dataset.csv'
# グラフの保存先ディレクトリ
OUTPUT_DIR = 'plot/'

# --- メイン処理 ---
def main():
    """
    UI/UXリサーチデータの基礎分析を行い、グラフを保存するメイン関数
    """
    # 0. 準備
    # --------------------------------------------------------------------------
    print("分析を開始します...")

    # 保存先ディレクトリがなければ作成
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"ディレクトリ '{OUTPUT_DIR}' を作成しました。")

    # データ読み込み
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print(f"エラー: {CSV_FILE} が見つかりません。")
        print("カレントディレクトリに dataset.csv を配置してください。")
        return

    # 分析対象の評価項目リスト
    evaluation_columns = [
        'Color Scheme', 'Visual Hierarchy', 'Typography',
        'Images and Multimedia', 'Layout'
    ]

    # 1. 1変量解析: 各項目の特徴を理解する
    # --------------------------------------------------------------------------
    print("\n[ステップ1/3] 各項目の特徴を分析中...")
    
    # 1.1 ユーザー属性: Age
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Age'], kde=True, bins=15)
    plt.title('ユーザーの年齢分布')
    plt.xlabel('年齢')
    plt.ylabel('人数')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '1_1_user_attribute_age_histogram.png'))
    plt.close()

    # 1.2 ユーザー属性: Gender
    plt.figure(figsize=(8, 6))
    sns.countplot(x='Gender', data=df, palette='viridis')
    plt.title('ユーザーの性別比')
    plt.xlabel('性別')
    plt.ylabel('人数')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '1_2_user_attribute_gender.png'))
    plt.close()

    # 1.3 ユーザー属性: Platform
    plt.figure(figsize=(10, 6))
    sns.countplot(y='Platform', data=df, order=df['Platform'].value_counts().index, palette='plasma')
    plt.title('利用プラットフォーム')
    plt.xlabel('人数')
    plt.ylabel('プラットフォーム')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '1_3_user_attribute_platform.png'))
    plt.close()
    
    # 1.4 各評価項目の全体傾向
    df_eval_melted = df.melt(value_vars=evaluation_columns, var_name='評価項目', value_name='評価スコア')
    plt.figure(figsize=(12, 8))
    sns.countplot(y='評価項目', hue='評価スコア', data=df_eval_melted, palette='coolwarm')
    plt.title('各デザイン項目の評価スコア分布')
    plt.xlabel('人数')
    plt.ylabel('')
    plt.legend(title='評価スコア', bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '1_4_evaluation_distribution_all.png'))
    plt.close()

    # 1.5 ユーザー体験（テキスト）の頻度
    plt.figure(figsize=(10, 7))
    sns.countplot(y='User_experience', data=df, order=df['User_experience'].value_counts().index)
    plt.title('ユーザー体験のカテゴリ別頻度')
    plt.xlabel('件数')
    plt.ylabel('ユーザー体験')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '1_5_user_experience_frequency.png'))
    plt.close()

    # 1.6 ユーザー体験のワードクラウド
    text = ' '.join(df['User_experience'].dropna())
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        # 日本語フォントパスは環境に合わせて変更が必要な場合がある
        # japanize-matplotlibがインストールされていれば不要なことが多い
        # font_path='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc' 
    ).generate(text)
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('ユーザー体験に関するワードクラウド')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '1_6_user_experience_wordcloud.png'))
    plt.close()

    # 2. 2変量解析: 項目間の関係性を探る
    # --------------------------------------------------------------------------
    print("[ステップ2/3] 項目間の関係性を分析中...")

    # 2.1 属性と評価の関係
    # 年齢層をカテゴリ化
    bins = [0, 29, 49, 100]
    labels = ['20代以下', '30-40代', '50代以上']
    df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
    
    for col in evaluation_columns:
        # 性別 vs 評価
        plt.figure(figsize=(8, 6))
        sns.boxplot(x='Gender', y=col, data=df, palette='viridis')
        plt.title(f'性別による「{col}」の評価')
        plt.xlabel('性別')
        plt.ylabel('評価スコア')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f'2_1_gender_vs_{col.replace(" ", "_")}.png'))
        plt.close()

        # 年齢層 vs 評価
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='Age Group', y=col, data=df, palette='magma')
        plt.title(f'年齢層による「{col}」の評価')
        plt.xlabel('年齢層')
        plt.ylabel('評価スコア')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f'2_2_age_group_vs_{col.replace(" ", "_")}.png'))
        plt.close()

        # プラットフォーム vs 評価
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='Platform', y=col, data=df, palette='plasma')
        plt.title(f'プラットフォームによる「{col}」の評価')
        plt.xlabel('プラットフォーム')
        plt.ylabel('評価スコア')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f'2_3_platform_vs_{col.replace(" ", "_")}.png'))
        plt.close()

    # 2.2 評価項目間の相関
    df_eval = df[evaluation_columns]
    # スピアマンの順位相関係数を計算
    corr = df_eval.corr(method='spearman')
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', vmin=-1, vmax=1)
    plt.title('評価項目間の相関ヒートマップ (スピアマン)')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '2_4_evaluation_correlation_heatmap.png'))
    plt.close()
    
    print("[ステップ3/3] 全ての分析が完了しました。")
    print(f"\nグラフは '{OUTPUT_DIR}' ディレクトリに保存されました。")
    
if __name__ == '__main__':
    main()