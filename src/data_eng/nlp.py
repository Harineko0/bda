import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from spellchecker import SpellChecker
import inflect

# --- 設定 ---
# INPUT_CSV = 'dataset_modified/uicrit_id_task.csv'
# OUTPUT_CSV = 'dataset_for_bda/tasks_extracted_chunk.csv'
INPUT_CSV = 'dataset_modified/uicrit_id_task_corrected.csv'
OUTPUT_CSV = 'dataset_for_bda/tasks_extracted_chunk_corrected.csv'
STOP_VERBS = {'click', 'view', 'go'}
SIMPLIFICATION_METHOD = 'IDF'

def cleans(text):
    """
    テキストから引用符や不要な句読点を削除し、フォーマットを整える関数
    """
    if not isinstance(text, str):
        return text
    return text.replace('"', '').replace("'", "").replace(".", "").replace("&", " and ").replace("/", " or ").replace("  ", " ").capitalize().strip()

def singularize_nouns(text, nlp_processor, p_engine):
    """【新規追加】文中の複数形の名詞を単数形に変換する関数"""
    if not isinstance(text, str):
        return text
    
    doc = nlp_processor(text)
    new_sentence = []
    for token in doc:
        # 品詞が名詞(NOUN)または固有名詞(PROPN)の場合のみ処理
        if token.pos_ in ('NOUN', 'PROPN'):
            # inflectを使って単数形に変換 (変換できなければ元の単語を返す)
            singular = p_engine.singular_noun(token.text)
            new_sentence.append(singular or token.text)
        else:
            new_sentence.append(token.text)
    
    # 処理後のトークンを再度結合し、余分なスペースを削除
    return " ".join(new_sentence).replace(" 's", "'s")

def correct_spelling(text):
    spell = SpellChecker()
    # テキストを単語に分割
    words = text.split()
    # 未知の単語（=タイポの可能性）を見つける
    # misspelled = spell.unknown(words)
    
    corrected_text = []
    for word in words:
        # タイポがあれば修正し、なければ元の単語を使う
        corrected_text.append(spell.correction(word) or word)
        
    return " ".join(corrected_text)

def extract_verb_obj(text, nlp_processor):
    """
    テキストから主要な動詞と目的語の「フレーズ」を抽出する関数
    【再改善版】動詞句(xcomp)内の目的語も探索
    """
    if not isinstance(text, str):
        return None, None

    doc = nlp_processor(text)
    
    all_verbs = [token for token in doc if token.pos_ == 'VERB']
    num_verbs = len(all_verbs)
    # print("all_verbs", [v.lemma_ for v in all_verbs])
    
    verbs_to_check = []
    
    root = next((token for token in doc if token.dep_ == 'ROOT' and token.pos_ == 'VERB'), None)
    if not root:
        return None, None

    is_stop_verb = root.lemma_.lower() in STOP_VERBS

    if num_verbs == 1:
        verbs_to_check.append(root)
    elif is_stop_verb:
        xcomp_verb = next((child for child in root.children if child.dep_ == 'xcomp' and child.pos_ == 'VERB'), None)
        if xcomp_verb:
            verbs_to_check.append(xcomp_verb)
    else:
        verbs_to_check.append(root)

    # print("verbs_to_check", [v.lemma_ for v in verbs_to_check])
    
    for child in root.children:
        if child.dep_ == 'conj' and child.pos_ == 'VERB':
            if child not in verbs_to_check:
                verbs_to_check.append(child)

    for verb in verbs_to_check:
        # 1. 直接目的語(dobj)を探す
        dobj = next((child for child in verb.children if child.dep_ == 'dobj'), None)
        if dobj:
            return verb.lemma_, " ".join(t.text for t in dobj.subtree)
        
        # 2. 動詞句の補語(xcomp)の中の目的語を探す 【新規追加】
        xcomp = next((child for child in verb.children if child.dep_ == 'xcomp' and child.pos_ == 'VERB'), None)
        if xcomp:
            dobj_in_xcomp = next((child for child in xcomp.children if child.dep_ == 'dobj'), None)
            if dobj_in_xcomp:
                # 動詞はxcompの方(例: following)を採用する
                return xcomp.lemma_, " ".join(t.text for t in dobj_in_xcomp.subtree)

        # 3. (フォールバック) 前置詞の目的語(pobj)を探す
        prep = next((child for child in verb.children if child.dep_ == 'prep'), None)
        if prep:
            pobj = next((child for child in prep.children if child.dep_ == 'pobj'), None)
            if pobj:
                return verb.lemma_, " ".join(t.text for t in pobj.subtree)
    
    return None, None

def get_rarest_noun_by_idf(text, nlp_processor, idf_scores):
    """【IDF方式】与えられたテキストから、IDFスコアが最も高い名詞を一つ返す"""
    if not isinstance(text, str) or not idf_scores:
        return None
        
    doc = nlp_processor(text)
    rarest_word = None
    max_idf = -1.0
    nouns = [token for token in doc if token.pos_ in ('NOUN', 'PROPN')]
    
    if not nouns:
        return None

    for token in nouns:
        word = token.lemma_.lower()
        if word in idf_scores and idf_scores[word] > max_idf:
            max_idf = idf_scores[word]
            rarest_word = word
    
    if rarest_word is None:
        return nouns[-1].lemma_.lower()

    return rarest_word

def get_noun_chunk_root(text, nlp_processor):
    """【Noun Chunking方式】フレーズの主要な名詞句から中心単語を返す"""
    if not isinstance(text, str):
        return None
        
    doc = nlp_processor(text)
    for chunk in reversed(list(doc.noun_chunks)):
        return chunk.root.lemma_
    
    nouns = [token for token in doc if token.pos_ == 'NOUN']
    if nouns:
        return nouns[-1].lemma_
        
    return None

def main():
    try:
        nlp = spacy.load('en_core_web_sm')
        p = inflect.engine() # inflectエンジンを初期化
    except OSError:
        print("spaCyの英語モデル 'en_core_web_sm' が見つかりません。")
        return
    except ImportError:
        print("inflectライブラリが見つかりません。`pip install inflect`でインストールしてください。")
        return

    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"エラー: {INPUT_CSV} が見つかりません。")
        return

    df['task'] = df['task'].apply(cleans).apply(lambda text: singularize_nouns(text, nlp, p))
    
    print("--- ステップ1: 動詞と目的語フレーズの抽出開始 ---")
    df[['verb', 'obj']] = df['task'].apply(lambda text: pd.Series(extract_verb_obj(text, nlp)))
    print("抽出完了。")

    print(f"\n--- ステップ2: 目的語を '{SIMPLIFICATION_METHOD}' 方式で単純化します ---")
    if SIMPLIFICATION_METHOD == 'IDF':
        corpus = df['obj'].dropna().tolist()
        idf_scores = {}
        if corpus:
            vectorizer = TfidfVectorizer(use_idf=True)
            vectorizer.fit_transform(corpus)
            idf_scores = dict(zip(vectorizer.get_feature_names_out(), vectorizer.idf_))
            print("IDFスコアの計算が完了しました。")
        else:
            print("目的語が見つからなかったため、IDFの計算はスキップします。")
        df['obj'] = df['obj'].apply(lambda text: get_rarest_noun_by_idf(text, nlp, idf_scores))

    elif SIMPLIFICATION_METHOD == 'CHUNK':
        df['obj'] = df['obj'].apply(lambda text: get_noun_chunk_root(text, nlp))
        print("Noun Chunkingによる単純化が完了しました。")
        
    else:
        print(f"エラー: 無効な単純化方式です: '{SIMPLIFICATION_METHOD}'。'IDF' または 'CHUNK' を指定してください。")
        return
    
    print("\n--- 最終結果 (先頭15件) ---")
    print(df[['id', 'task', 'verb', 'obj']].head(15).to_string())

    df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"\n抽出結果を '{OUTPUT_CSV}' に保存しました。")

if __name__ == '__main__':
    main()