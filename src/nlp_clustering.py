"""
problem, solution verb, solution object の CSV の正規化を行う
"""

import re
import pandas as pd
import numpy as np
import spacy
from sklearn.cluster import AgglomerativeClustering
from collections import Counter
import warnings

# --- 設定項目 ---
# ユーザーのspacyコードで生成されたCSVファイルを指定
INPUT_CSV = 'dataset_for_bda/comments_extracted.csv'
# 正規化後の結果を保存するファイル名を指定
OUTPUT_CSV = 'dataset_for_bda/comments_clustered.csv'
# spaCyのベクトル付きモデル
SPACY_MODEL = 'en_core_web_md'
# クラスタリングの閾値（0に近いほど厳しく、1に近いほど緩やかになる。0.2~0.4あたりで調整）
DISTANCE_THRESHOLD = 0.3

# FutureWarningを非表示にする
warnings.simplefilter(action='ignore', category=FutureWarning)

def clean_text(text: str) -> str:
    """抽出後のテキストをクリーニングする"""
    if not isinstance(text, str):
        return ""
    # 改行以降を削除
    text = text.split('\n')[0]
    # 文末の句до点や不要な記号を削除
    text = re.sub(r'[.,;!?-]$', '', text.strip())
    # ハイフン前後のスペースを削除
    text = re.sub(r'\s*-\s*', '-', text)
    # 連続するスペースを一つに
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def create_normalization_map(phrases: list[str], nlp: spacy.language.Language) -> dict[str, str]:
    """
    フレーズのリストを受け取り、クラスタリングして正規化マッピング辞書を返す
    """
    print(f"合計 {len(phrases)} 個のユニークなフレーズを処理します...")

    # フレーズをベクトル化
    vectors = []
    valid_phrases = []
    for phrase in phrases:
        doc = nlp(phrase)
        word_vectors = [token.vector for token in doc if token.has_vector and not token.is_stop]
        if word_vectors:
            vectors.append(np.mean(word_vectors, axis=0))
            valid_phrases.append(phrase)

    if not valid_phrases:
        print("有効なベクトルを持つフレーズが見つかりませんでした。")
        return {}

    vectors = np.array(vectors)

    # 階層的クラスタリング
    print("フレーズをクラスタリングしています...")
    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=DISTANCE_THRESHOLD,
        metric='cosine', # scikit-learn 1.2以降はmetric, それ以前はaffinity
        linkage='average'
    ).fit(vectors)

    # 元のフレーズとクラスターラベルを対応付ける
    original_phrase_to_label = {phrase: clustering.labels_[i] for i, phrase in enumerate(valid_phrases)}

    # 各クラスターで最も頻繁に出現するフレーズを代表語とする
    label_to_phrases = {}
    for phrase, label in original_phrase_to_label.items():
        if label not in label_to_phrases:
            label_to_phrases[label] = []
        label_to_phrases[label].append(phrase)

    print("\n--- 作成されたクラスターの例 ---")
    for i, (label, cluster_phrases) in enumerate(label_to_phrases.items()):
        if i >= 5: # 表示しすぎないように最初の5件のみ
            print("...")
            break
        print(f"クラスター {label}: {cluster_phrases}")


    # 正規化マッピング辞書を作成
    mapping = {}
    for label, cluster_phrases in label_to_phrases.items():
        # クラスター内で最も頻繁に出現するものを代表語に
        most_common_phrase = Counter(cluster_phrases).most_common(1)[0][0]
        for phrase in cluster_phrases:
            mapping[phrase] = most_common_phrase

    return mapping


def main():
    """
    メイン処理
    """
    print(f"spaCyモデル '{SPACY_MODEL}' をロードしています...")
    try:
        nlp = spacy.load(SPACY_MODEL)
    except OSError:
        print(f"エラー: spaCyモデル '{SPACY_MODEL}' が見つかりません。")
        print(f"ターミナルで `python -m spacy download {SPACY_MODEL}` を実行してください。")
        return

    print(f"入力ファイル '{INPUT_CSV}' を読み込んでいます...")
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"エラー: {INPUT_CSV} が見つかりません。")
        return

    # 正規化対象のカラムを特定（_problem と _objで終わる列）
    target_columns = [col for col in df.columns if col.endswith('_problem') or col.endswith('_verb') or col.endswith('_obj')]
    if not target_columns:
        print("エラー: 正規化対象のカラム（_problem, _obj）が見つかりませんでした。")
        return

    # 全てのユニークなフレーズを収集・クリーニング
    all_phrases = pd.unique(df[target_columns].values.ravel('K'))
    cleaned_phrases = {clean_text(p) for p in all_phrases if isinstance(p, str) and p != 'unknown' and clean_text(p)}

    # 正規化マッピングを作成
    normalization_map = create_normalization_map(list(cleaned_phrases), nlp)

    if not normalization_map:
        print("正規化マッピングが作成されなかったため、処理を終了します。")
        return
        
    print("\n正規化マッピングをデータに適用しています...")
    # クリーニング関数と正規化マッピングを適用
    for col in target_columns:
        # 1. 各値をクリーニング
        cleaned_series = df[col].apply(clean_text)
        # 2. クリーニングされた値にマッピングを適用
        df[col] = cleaned_series.map(normalization_map).fillna(cleaned_series)


    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n処理が完了しました。正規化されたデータを '{OUTPUT_CSV}' に保存しました。")


if __name__ == '__main__':
    main()