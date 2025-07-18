"""
正規化したコメントから problem, solution verb, solution object を抽出する
"""

import spacy
import re
import pandas as pd


INPUT_CSV = 'dataset_for_bda/comments_normalized.csv'
OUTPUT_CSV = 'dataset_for_bda/comments_extracted.csv'
# INPUT_CSV = 'dataset_for_bda/comments_normalized_subset.csv'
# OUTPUT_CSV = 'dataset_for_bda/comments_extracted_subset.csv'

# spaCyの英語モデルをロードします
# 事前にターミナルでインストールが必要です:
# pip install spacy
# python -m spacy download en_core_web_sm
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCyモデル 'en_core_web_sm' が見つかりません。")
    print("ターミナルで `python -m spacy download en_core_web_sm` を実行してください。")
    nlp = None

def find_subject_verb_object(doc: spacy.tokens.doc.Doc) -> tuple[str, str, str]:
    """
    spaCyで解析済みのDocから、主語、動詞、目的語を抽出するヘルパー関数。
    """
    subject = "unknown"
    verb = "unknown"
    obj = "unknown"
    
    # 文のルート(ROOT)で品詞が動詞(VERB)のトークンを探す
    # print("---")
    for token in doc:
        # print("\t\ttoken", token.text, token.dep_, token.pos_)
        if token.dep_ == "ROOT" and ["VERB", "AUX"].count(token.pos_) > 0:
            verb = token.lemma_  # 動詞の原形を取得
            
            # 動詞に関連する主語(nsubj)と目的語(dobj, attr)を探す
            for child in token.children:
                # 主語を抽出
                if ["nsubj", "nsubjpass"].count(child.dep_) > 0:
                    # ADP 以降のトークンをフィルター
                    subtree = []
                    for t in child.subtree:
                        if t.pos_ == 'ADP':
                            break
                        subtree.append(t)
                    
                    # DET, PRON, PUNCT 以外のトークンの lemma_を抽出
                    subject = " ".join(t.lemma_ for t in subtree if ['DET', 'PRON'].count(t.pos_) == 0)
                # 目的語を抽出
                elif child.dep_ in ("dobj", "attr"):
                    # ADP 以降のトークンをフィルター
                    subtree = []
                    for t in child.subtree:
                        if t.pos_ == 'ADP':
                            break
                        subtree.append(t)

                    obj = " ".join(t.lemma_ for t in subtree if ['DET', 'PRON'].count(t.pos_) == 0)
            break
            
    return subject, verb, obj


def clean_extracted_text(text: str) -> str:
    """抽出後のテキストをクリーニングする"""
    if not isinstance(text, str):
        return "unknown"
    
    # 改行以降を削除
    text = text.split('\n')[0]
    
    # 文末の句読点や不要な記号を削除
    text = re.sub(r'[.,;!?-]$', '', text.strip())
    
    # ハイフン前後のスペースを削除
    text = re.sub(r'\s*-\s*', '-', text)
    
    # 連続するスペースを一つに
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text if text else "unknown"

def extract_critique_by_format(text: str) -> tuple[str, str, str]:
    """
    指定されたフォーマットに従い、UI批評から問題(S)、改善策の動詞(V)、目的語(O)を抽出する。
    
    フォーマット: "In the current design, S V O. To fix this, [S] V O ..."

    Args:
        text: UI批評のテキスト文字列。

    Returns:
        ('problem', 'solution_verb', 'solution_obj') の形式のタプル。
    """    
    problem = "unknown"
    solution_verb = "unknown"
    solution_obj = "unknown"

    if not nlp:
        print("spaCyのモデルがロードされていません。")
        return ("unknown", "unknown", "unknown")
    
    # if nan
    if not isinstance(text, str) or not text.strip():
        return ("unknown", "unknown", "unknown")

    # カッコの中身を削除
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\[[^)]*\]', '', text)
    text = re.sub(r'\'[^)]*\'', '', text)
    text = text.replace('"', '').replace('""', '').replace('  ', ' ').strip()
    # print(f"入力テキスト: {text}")
    
    # 指定された形式に基づいて、テキストを「問題部」と「解決策部」に分割する正規表現
    pattern = re.compile(
        r"In the current design,?(.*?)(?:To fix this,)(.*)",
        re.IGNORECASE | re.DOTALL
    )
    match = pattern.search(text)
    if not match:
        # print(f"フォーマットに合致しないテキスト: {text}")
        return ("unknown", "unknown", "unknown")

    problem_clause_text = match.group(1).strip().capitalize()
    solution_clause_text = match.group(2).strip().capitalize()

    # --- 1. "In the current design," に続く文の主語(S)を抽出 ---
    if problem_clause_text:
        doc_problem = nlp(problem_clause_text)
        problem_subject, _, _ = find_subject_verb_object(doc_problem)
        problem = problem_subject

    # --- 2. "To fix this," に続く文の動詞(V)と目的語(O)を抽出 ---
    if solution_clause_text:
        doc_solution = nlp(solution_clause_text)
        # 解決策の文では主語は不要なため、返り値のverbとobjのみ使用
        s_subject, s_verb, s_obj = find_subject_verb_object(doc_solution)
        solution_verb = s_verb
        # obj が存在しなければ subject を代わりに使用
        # print('\t', s_subject, s_obj)
        solution_obj = s_obj if s_obj != 'unknown' else s_subject

    # strip all
    problem = clean_extracted_text(problem)
    solution_verb = clean_extracted_text(solution_verb)
    solution_obj = clean_extracted_text(solution_obj)
    
    return ("unknown" if problem == "" else problem,
            "unknown" if solution_verb == "" else solution_verb,
            "unknown" if solution_obj == "" else solution_obj)

# --- テスト実行 ---
# text1 = "In the current design, the texts are too small and difficult to read. To fix this, increase font size and weight to make it easier to read."
# text2 = "In the current design, the login button appears twice with slightly different labels. To fix this, one button is labeled login and the other button has the Facebook logo and is labeled login"
# text3 = "In the current design, the back button is not visually prominent. To fix this, we can enlarge the back button."
# text4 = "In the current design, the element is disappearing at the bottom edge of the layout leaving no marginal space which is making it difficult for users to read the information properly. To fix this, redesign the UI to fit the elements within the page layout"
# text5 = "In the current design, the Duration 0:33 / 3 ch. text has no connection to any other element on the page. To fix this, the Duration 0:33 / 3 ch. text should be removed or connected to another element on the page."

# print("--- spaCyを使った抽出結果 ---")
# print(f"入力1: {text1}\n出力1: {extract_critique_by_format(text1)}")
# print(f"入力2: {text2}\n出力2: {extract_critique_by_format(text2)}")
# print(f"入力3: {text3}\n出力3: {extract_critique_by_format(text3)}")
# print(f"入力4: {text4}\n出力4: {extract_critique_by_format(text4)}")
# print(f"入力5: {text5}\n出力5: {extract_critique_by_format(text5)}")

def main():
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"エラー: {INPUT_CSV} が見つかりません。")
        return

    # 'comments' カラムから問題、動詞、目的語を抽出
    # comment1_text, comment2_text, comment3_text, comment4_text, comment5_text, comment6_text, comment7_text についてそれぞれ extract_critique_by_format を実行し, comment1_problem, comment1_solution_verb, comment1_solution_obj などの新しいカラムを作成
    for i in range(1, 8):
        comment_col = f'comment{i}_text'
        if comment_col in df.columns:
            df[[f'comment{i}_problem', f'comment{i}_solution_verb', f'comment{i}_solution_obj']] = df[comment_col].apply(
                lambda text: pd.Series(extract_critique_by_format(text))
            )
        else:
            print(f"警告: {comment_col} カラムが見つかりません。スキップします。")

    # drop comment1_type, comment1_text, ..., comment7_type, comment7_text
    for i in range(1, 8):
        df.drop(columns=[f'comment{i}_type', f'comment{i}_text'], errors='ignore', inplace=True)

    # 結果を新しいCSVファイルに保存
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"抽出結果を {OUTPUT_CSV} に保存しました。")
    
if __name__ == '__main__':
    main()