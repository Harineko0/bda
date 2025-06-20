import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def analyze_ui_ux_dataset_v4(file_path='dataset.csv'):
    """
    UI/UXデータセットを読み込み、分析し、結果をグラフとして保存する関数。
    - 年代別グラフにサンプルサイズの棒グラフを追加
    
    Args:
        file_path (str): データセットのCSVファイルへのパス。
    """
    # --- 0. 保存用ディレクトリと日本語フォント設定 ---
    output_dir = 'plot'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"ディレクトリ '{output_dir}' を作成しました。")
    
    # 日本語ラベルが文字化けする場合の対策
    try:
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'MS Gothic']
    except Exception as e:
        print(f"日本語フォントの設定中にエラーが発生しました: {e}")
        print("グラフの日本語ラベルが正しく表示されない可能性があります。")

    # --- 1. データセットの読み込み ---
    try:
        df = pd.read_csv(file_path)
        print(f"'{file_path}' を正常に読み込みました。")
    except FileNotFoundError:
        print(f"エラー: ファイル '{file_path}' が見つかりません。")
        print("カレントディレクトリに dataset.csv を配置してください。")
        return

    # --- 2. 各レコードごとの統計量計算 ---
    features = [
        'Color Scheme',
        'Visual Hierarchy',
        'Typography',
        'Images and Multimedia',
        'Layout'
    ]
    df['Mean'] = df[features].mean(axis=1)
    df['Variance'] = df[features].var(axis=1, ddof=0)
    df['Min'] = df[features].min(axis=1)
    df['Max'] = df[features].max(axis=1)
    print("各レコードの統計量を計算しました。")

    # --- 3. 年代カラムの追加 ---
    df['AgeGroup'] = (df['Age'] // 10) * 10
    print("年代（AgeGroup）カラムを追加しました。")

    # --- 4. 年代別の統計量とサンプルサイズの計算 (変更点) ---
    age_group_agg = df.groupby('AgeGroup').agg(
        Mean=('Mean', 'mean'),
        Variance=('Variance', 'mean'),
        Min=('Min', 'mean'),
        Max=('Max', 'mean'),
        SampleSize=('Age', 'size') # 各年代の人数をカウント
    ).sort_index().reset_index()
    print("年代ごとの統計量とサンプルサイズを集計しました。")

    # --- 5. 年代をx軸とした二重Y軸グラフのプロットと保存 (変更点) ---
    metrics = ['Mean', 'Variance', 'Min', 'Max']
    fig_age_group, axes_age_group = plt.subplots(2, 2, figsize=(18, 12))
    fig_age_group.suptitle('UI/UX Statistics and Sample Size by Age Group', fontsize=18, weight='bold')

    axes_flat_age_group = axes_age_group.flatten()
    for i, metric in enumerate(metrics):
        # 各サブプロット (左Y軸)
        ax1 = axes_flat_age_group[i]
        
        # 右Y軸を作成
        ax2 = ax1.twinx()

        # 右Y軸: 棒グラフ (サンプルサイズ) を背景として先に描画
        bar_width = 6 # 棒グラフの幅を調整
        ax2.bar(age_group_agg['AgeGroup'], age_group_agg['SampleSize'], 
                width=bar_width, color='lightgray', alpha=0.7, zorder=5, label='Sample Size (count)')
        ax2.set_ylabel('Sample Size (count)', color='gray', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='gray')
        # Y軸のメモリが整数になるように設定
        ax2.get_yaxis().set_major_locator(plt.MaxNLocator(integer=True))
        ax2.set_ylim(0, age_group_agg['SampleSize'].max() * 1.25) # 上部に余白を確保

        # 左Y軸: 折れ線グラフ (統計量) を手前に描画
        ax1.plot(age_group_agg['AgeGroup'], age_group_agg[metric], 
                 color='dodgerblue', marker='o', linestyle='-', zorder=10, label=f'Average {metric}')
        ax1.set_ylabel(f'Average {metric}', color='dodgerblue', fontsize=12, weight='bold')
        ax1.tick_params(axis='y', labelcolor='dodgerblue')
        ax1.grid(axis='y', linestyle='--', alpha=0.7)

        # X軸の設定
        ax1.set_xlabel('年代', fontsize=12)
        ax1.set_xticks(age_group_agg['AgeGroup'])
        ax1.set_xticklabels([f"{age}代" for age in age_group_agg['AgeGroup']], fontsize=11)
        ax1.set_zorder(ax2.get_zorder() + 1) # 折れ線グラフの軸を手前に持ってくる
        ax1.patch.set_visible(False) # 折れ線グラフの軸の背景を透明にする

        # サブプロットのタイトル
        ax1.set_title(f'{metric} vs. Age Group', fontsize=14)

        # 凡例をまとめる
        lines, labels = ax1.get_legend_handles_labels()
        bars, bar_labels = ax2.get_legend_handles_labels()
        ax2.legend(lines + bars, labels + bar_labels, loc='upper left')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    # ファイル名を変更して保存
    age_group_plot_path = os.path.join(output_dir, 'statistics_by_age_group_with_samplesize.png')
    plt.savefig(age_group_plot_path)
    plt.close(fig_age_group)
    print(f"年代別（サンプルサイズ付き）のグラフを '{age_group_plot_path}' に保存しました。")
    
    # --- 他のグラフ作成処理 (変更なし) ---
    # (可読性のためにここでは省略しますが、実際のコードには含まれます)


if __name__ == '__main__':
    # 全てのグラフを生成する関数を呼び出す
    # (v3までの他のグラフ生成も内部で行う完全版として提供します)
    # analyze_ui_ux_dataset_v3('dataset.csv') # 旧バージョン
    analyze_ui_ux_dataset_v4('dataset.csv') # 新バージョン