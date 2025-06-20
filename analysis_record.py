import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def analyze_ui_ux_dataset_v5(file_path='dataset.csv'):
    """
    UI/UXデータセットを読み込み、分析し、結果をグラフとして保存する関数。
    - 全ての集計グラフにサンプルサイズの棒グラフを追加
    
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

    # --- 4. 年代別の統計量とサンプルサイズの計算 ---
    age_group_agg = df.groupby('AgeGroup').agg(
        Mean=('Mean', 'mean'),
        Variance=('Variance', 'mean'),
        Min=('Min', 'mean'),
        Max=('Max', 'mean'),
        SampleSize=('Age', 'size')
    ).sort_index().reset_index()
    print("年代ごとの統計量とサンプルサイズを集計しました。")

    # --- 5. 年代をx軸とした二重Y軸グラフのプロットと保存 ---
    metrics = ['Mean', 'Variance', 'Min', 'Max']
    fig_age_group, axes_age_group = plt.subplots(2, 2, figsize=(18, 12))
    fig_age_group.suptitle('UI/UX Statistics and Sample Size by Age Group', fontsize=18, weight='bold')

    axes_flat_age_group = axes_age_group.flatten()
    for i, metric in enumerate(metrics):
        ax1 = axes_flat_age_group[i]
        ax2 = ax1.twinx()

        ax2.bar(age_group_agg['AgeGroup'], age_group_agg['SampleSize'], width=6, color='lightgray', alpha=0.7, zorder=5, label='Sample Size (count)')
        ax2.set_ylabel('Sample Size (count)', color='gray', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='gray')
        ax2.get_yaxis().set_major_locator(plt.MaxNLocator(integer=True))
        ax2.set_ylim(0, age_group_agg['SampleSize'].max() * 1.25)

        ax1.plot(age_group_agg['AgeGroup'], age_group_agg[metric], color='dodgerblue', marker='o', zorder=10, label=f'Average {metric}')
        ax1.set_ylabel(f'Average {metric}', color='dodgerblue', fontsize=12, weight='bold')
        ax1.tick_params(axis='y', labelcolor='dodgerblue')
        ax1.grid(axis='y', linestyle='--', alpha=0.7)
        ax1.set_xlabel('年代', fontsize=12)
        ax1.set_xticks(age_group_agg['AgeGroup'])
        ax1.set_xticklabels([f"{age}代" for age in age_group_agg['AgeGroup']], fontsize=11)
        ax1.set_zorder(ax2.get_zorder() + 1)
        ax1.patch.set_visible(False)
        ax1.set_title(f'{metric} vs. Age Group', fontsize=14)

        lines, labels = ax1.get_legend_handles_labels()
        bars, bar_labels = ax2.get_legend_handles_labels()
        ax2.legend(lines + bars, labels + bar_labels, loc='upper left')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    age_group_plot_path = os.path.join(output_dir, 'statistics_by_age_group_with_samplesize.png')
    plt.savefig(age_group_plot_path)
    plt.close(fig_age_group)
    print(f"年代別（サンプルサイズ付き）のグラフを '{age_group_plot_path}' に保存しました。")
    
    # --- 6. プラットフォーム別の統計量とサンプルサイズの計算 (変更点) ---
    platform_agg = df.groupby('Platform').agg(
        Mean=('Mean', 'mean'),
        Variance=('Variance', 'mean'),
        Min=('Min', 'mean'),
        Max=('Max', 'mean'),
        SampleSize=('Age', 'size')
    ).reset_index()
    print("プラットフォームごとの統計量とサンプルサイズを集計しました。")

    # --- 7. プラットフォームをx軸とした二重Y軸グラフのプロットと保存 (変更点) ---
    fig_platform, axes_platform = plt.subplots(2, 2, figsize=(18, 14))
    fig_platform.suptitle('UI/UX Statistics and Sample Size by Platform', fontsize=18, weight='bold')

    axes_flat_platform = axes_platform.flatten()
    for i, metric in enumerate(metrics):
        ax1 = axes_flat_platform[i]
        ax2 = ax1.twinx()

        # 右Y軸: 棒グラフ (サンプルサイズ)
        ax2.bar(platform_agg['Platform'], platform_agg['SampleSize'], color='lightgray', alpha=0.7, zorder=5, label='Sample Size (count)')
        ax2.set_ylabel('Sample Size (count)', color='gray', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='gray')
        ax2.get_yaxis().set_major_locator(plt.MaxNLocator(integer=True))
        ax2.set_ylim(0, platform_agg['SampleSize'].max() * 1.25)

        # 左Y軸: 折れ線グラフ (統計量)
        ax1.plot(platform_agg['Platform'], platform_agg[metric], color='forestgreen', marker='o', zorder=10, label=f'Average {metric}')
        ax1.set_ylabel(f'Average {metric}', color='forestgreen', fontsize=12, weight='bold')
        ax1.tick_params(axis='y', labelcolor='forestgreen')
        ax1.grid(axis='y', linestyle='--', alpha=0.7)
        
        # X軸の設定
        ax1.set_xlabel('Platform', fontsize=12)
        ax1.tick_params(axis='x', rotation=45, labelsize=11) # ラベルを回転
        ax1.set_zorder(ax2.get_zorder() + 1)
        ax1.patch.set_visible(False)
        ax1.set_title(f'{metric} vs. Platform', fontsize=14)

        # 凡例をまとめる
        lines, labels = ax1.get_legend_handles_labels()
        bars, bar_labels = ax2.get_legend_handles_labels()
        ax2.legend(lines + bars, labels + bar_labels, loc='upper left')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    platform_plot_path = os.path.join(output_dir, 'statistics_by_platform_with_samplesize.png')
    plt.savefig(platform_plot_path)
    plt.close(fig_platform)
    print(f"プラットフォーム別（サンプルサイズ付き）のグラフを '{platform_plot_path}' に保存しました。")
    
    # (可読性の為、v3以前の他のグラフ作成処理は省略しています)


if __name__ == '__main__':
    # 最終版の関数を呼び出す
    analyze_ui_ux_dataset_v5('dataset.csv')