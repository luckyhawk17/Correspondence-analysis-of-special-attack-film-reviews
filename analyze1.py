import glob
import pandas as pd
import scipy as sp
import scipy.stats as ss
import morphological_analysis as mp
import config
import mca
import matplotlib.pyplot as plt
import japanize_matplotlib
import time
from pathlib import Path
from adjustText import adjust_text
import math

start = time.time()

## レビューを用意する
REVIEWS_PATH = "../reviews/" # レビューの格納フォルダの相対パス
# レビューのcsvファイルをすべて取り出す
all_files = glob.glob("{}*.csv".format(REVIEWS_PATH))
number_of_all_titles = len(all_files) # タイトル数
if number_of_all_titles < 3:
   print("タイトルは3以上必要です。")
   exit()    

reviews = []
for file in all_files:
    # レビューファイルを開く
    opened_f = open(file, encoding="utf-8_sig")
    reviews.append(pd.read_csv(opened_f))
    opened_f.close()

df = pd.concat(reviews, sort = False) # レビューファイルの結合
df = df.reset_index(drop = True) # 新しく全体のインデックスを振り直す
df.index.name = "総合インデックス"
df.index = df.index + 1
n = len(df) # サンプル数

## データの読み込み   

## 形態素解析

# 映画タイトルリストの作成
titles = df['映画タイトル']
title_list = [] # 映画タイトルリスト
title_list.append("") 

# データの映画タイトル欄から映画タイトルのリストを作成
flag = False
for title in titles:

    for e in title_list:
        if title == e:
            flag = True
            break

    if flag == True:
        flag = False
    else:        
        title_list.append(title)
    
del title_list[0:1]

# 全タイトルの分析
all_review = df['レビュー']
# 全タイトルのレビューを結合
all_review = "".join(all_review) 

# 全タイトルの形態素解析

# 各タイトルの形態素解析
morphoed_review_list = [] # 形態素解析した各タイトルのレビューのリスト
number_of_sentences_list = []
for title in title_list:
    
    review = df[df['映画タイトル'] == title]
    review = review['レビュー']
    review = "".join(review) # 文字列リストの要素を結合して一つの文字列に変換
    
    morphoed_review, number_of_sentences = mp.morphological_analysis.morpho(review)
    # 形態素解析したレビューをリストに加える
    morphoed_review_list.append(morphoed_review)
    # 全タイトルの文の数
    config.number_of_all_sentences += number_of_sentences
    # 各タイトルの文の数
    number_of_sentences_list.append(number_of_sentences)

# 形態素解析した各タイトルのレビューから全タイトルの単語度数リストをつくる
morphoed_all_review = []
for morphoed_review in morphoed_review_list:
    morphoed_all_review += morphoed_review # 形態素解析した各タイトルのレビューを結合

# 全タイトルの単語リスト
all_word_list = mp.morphological_analysis.generate_word_list(morphoed_all_review)
# 全タイトルの単語リストの長さ
config.length = len(all_word_list)

# 全タイトルの単語度数リスト
all_freq_list = mp.morphological_analysis.generate_freq_list(morphoed_all_review)
# 多い順に並べ替え
all_freq_list = mp.morphological_analysis.bubble_sort(all_freq_list) 

# 全タイトルの単語リストを全タイトルの単語度数リストからつくる
all_word_list = []
for word in all_freq_list:
    all_word_list.append(word[0])

# 全タイトルの単語リストから品詞を除外
all_word_list_l = []
for w in all_word_list:
    all_word_list_l.append(w[0])

# 各タイトルごとに単語の度数を調べる
word_freq_list = []
for morphoed_review in morphoed_review_list:
   
   # 全単語リストの単語の当該レビューにおける度数を調べる
   freq_list = mp.morphological_analysis.count_text_freq(morphoed_review, all_word_list)

   row = []

   for e in freq_list: # 各単語の度数をクロス表に加える
       row.append(e[1])

   word_freq_list.append(row)

# タイトル別単語度数リストのDataFrameの作成
word_df = pd.DataFrame(data=word_freq_list, columns=all_word_list_l)
word_df.insert(loc=0, column="映画タイトル", value=title_list)
word_df.to_csv("word_list.csv", encoding="utf-8_sig")

# 各単語のタイトルごとのtf-idf
tf_idf_matrix = pd.DataFrame()
tf_idf_matrix["映画タイトル"] = title_list
line_sum = [] # 行ごとの合計値
word_list_len = len(all_word_list_l)

for i in range(0, len(title_list), 1):
    l_sum = 0
    for j in range(1 ,word_list_len, 1):
        l_sum += word_df.iloc[i, j]     
    
    line_sum.append(l_sum)

for i in range(1, word_list_len, 1):
    column = word_df.iloc[:, i] # 各単語の度数を抽出
    number_of_titles_contain_the_word = 0 # 当該単語を含んでいるタイトル数

    for j in range(0, len(title_list), 1):
        if column[j] > 0:
            number_of_titles_contain_the_word += 1

    idf = 1 + math.log(number_of_all_titles/number_of_titles_contain_the_word)

    tf_column = []

    for j in range(0, len(title_list), 1):
        tf = column[j]/line_sum[j]
        tf_idf = tf * idf
        tf_column.append(tf_idf)

    tf_idf_matrix[column.name] = tf_column

tf_idf_matrix.to_csv("tf_idf.csv", index=False, encoding="utf-8_sig")

# カイ二乗検定

# 上位語についてピアソンのカイ二乗検定（独立性の検定）を行う
top = 100 # 上位語の数

data = pd.DataFrame()
data["映画タイトル"] = title_list

for i in range(1, top, 1):
    column = word_df.iloc[:, i] # 各単語の度数を抽出
    crossed = []

    for j in range(0, len(title_list), 1):
        # 行の周辺度数は文とする
        one = column[j] # 出現を1、非出現を0に変換
        zero = number_of_sentences_list[j] - one
        row = []
        row.append(zero)
        row.append(one)
        crossed.append(row)

    x2, p, dof, expected = ss.chi2_contingency(crossed, correction=True)

    if p < 0.05:
        data[column.name] = column

    crossed.clear()

# Rによる対応分析用のcsvファイル
data.to_csv("data.csv", index=False, encoding="shift-jis") 

# pythonのmca用にもう一度読み込む
cor_df = pd.read_csv("data.csv", index_col=0, header=0, encoding="shift-jis")

# 対応分析
mca_counts = mca.MCA(cor_df, benzecri=False)
rows = mca_counts.fs_r(N=2)
cols = mca_counts.fs_c(N=2)

# グラフタイトル
plt.title('{0}, n={1}, 上位語数:{2}'.format(title_list, n, top))

# 固有値
plt.xlabel("成分1({:.4f}, {:.2f}%)".format(mca_counts.L[0], mca_counts.L[0]*100/sum(mca_counts.L)))
plt.ylabel("成分2({:.4f}, {:.2f}%)".format(mca_counts.L[1], mca_counts.L[1]*100/sum(mca_counts.L)))


plt.axvline(0, color="magenta", linewidth=0.5)
plt.axhline(0, color="magenta", linewidth=0.5) 

# テキストラベルのリスト
texts_title = [] 
texts_word = []

# 映画タイトルのプロット
plt.scatter(rows[:, 0], rows[:, 1], marker="None", color="blue")
labels = cor_df.index
for label,x,y in zip(labels, rows[:, 0], rows[:, 1]):
    plt_text = plt.annotate(label, xy = (x, y), xytext=(x, y), c="b")

# 単語のプロット
plt.scatter(cols[:, 0], cols[:, 1], marker="None", color="red")
labels = cor_df.columns
for label, x, y in zip(labels, cols[:, 0], cols[:, 1]):
    plt_text = plt.annotate(label, xy = (x, y), xytext=(x, y), c="r")
    texts_word.append(plt_text)

# 注釈用テキストの整列
adjust_text(texts_title)
adjust_text(texts_word)

i = 1
filename = "../Figures/{0}{1}.png".format(title_list, i)
p = Path(filename)
if p.exists():
    while i < 100:
        filename = "../Figures/{0}{1}.png".format(title_list, i)
        p = Path(filename)
        if p.exists():
            i += 1
        else:            
            break

# グラフの保存
plt.savefig(filename, dpi=300)
plt.show()

end = time.time()
elapsed = end - start
hour = elapsed // 3600
minute = (elapsed % 3600) // 60
second = (elapsed % 3600 % 60)
elapsed_text = "処理時間：%d時間%d分%d秒" % (hour, minute, second)
print(elapsed_text)










input()