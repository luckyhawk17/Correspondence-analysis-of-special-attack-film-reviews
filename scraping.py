from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

options = Options()
options.add_argument('--headless')

start = time.time()

# ブラウザの起動
service = webdriver.ChromeService() 
driver = webdriver.Chrome(service=service)

film_title = "映画タイトル"
url = "映画タイトルURL"
driver.get(url)

# レビューを格納するリスト
reviews = []

i = 0
is_continue = True
duplicate = False
while(is_continue):
    i = i + 1

    # レビューの抽出
    elements = driver.find_elements(By.CLASS_NAME, "p-mark")
    for e in elements:

        # レビュワー一人分の取得データ（タイトル・レビュワー名・投稿日時・レビュー本文）  
        review = []        

        # 映画のタイトル
        review.append(film_title)

        # レビュワー名の取得
        reviewer_e = e.find_element(By.CLASS_NAME, "c2-user-m__heading")
        reviewer = reviewer_e.find_element(By.CSS_SELECTOR, "a").text.replace("の感想・評価", "")
        # 要素内の文字列を取得
        # 不要な文字列を削除
        
        print(reviewer)

        review.append(reviewer)            

        # 投稿日時の取得
        date = e.find_element(By.CSS_SELECTOR, "time").text
        review.append(date)

        # 評価の取得
        rating = e.find_element(By.CLASS_NAME, "c2-rating-s__text").text
        review.append(rating)
        print(rating)

        # レビュー本文の取得        
        text_e = e.find_element(By.CLASS_NAME, "p-mark-review")  
        # "p-mark__review"が"p-mark-review"に書き替わっている（2025/05/06現在） 
        
        try: # レビュー本文に続きがある場合
            a_tag = text_e.find_element(By.CSS_SELECTOR, "a")
            a_tag_text = a_tag.get_attribute("textContent")
            print(a_tag_text)

            if a_tag_text == ">>続きを読む": 

                read_more_url = a_tag.get_attribute("href")
                # 別タブで開く
                driver.execute_script("window.open();")
                # 別タブをインスタンスウィンドウにする
                driver.switch_to.window(driver.window_handles[1])
                # 別タブで「続き」のURLに移動
                driver.get(read_more_url)
                
                # 本文の続きを取得
                read_more_e = driver.find_element(By.CLASS_NAME, "p-mark-review")
                text = read_more_e.get_attribute("textContent") 
                text = text.replace("\n", "")
                # 改行コードと不要な文字列を削除

                print(text)
                review.append(text)

                # 別タブを閉じる
                driver.close()
                # 元のタブに戻る
                driver.switch_to.window(driver.window_handles[0])
            
            else: # 「続きを読む」以外のリンクが貼ってある場合、そのまま本文を取得
                text = text_e.get_attribute("textContent")
                
                # 要素内の文字列を取得
                text = text.replace("\n", "")
                print(text)
                review.append(text)

        except:
            text = text_e.get_attribute("textContent")
            text = text.replace("\n", "")
            print(text)
            review.append(text)

        reviews.append(review)

    if i > 100: # ページ数の上限

        end = time.time()
        elapsed = end - start
        hour = elapsed // 3600
        minute = (elapsed % 3600) // 60
        second = (elapsed % 3600 % 60)
        elapsed_text = "処理時間：%d時間%d分%d秒" % (hour, minute, second)
        print(elapsed_text)
        break 

    # 最後のページまで来たら終了
    if driver.find_elements(By.CLASS_NAME, "c2-pagination__next.c2-pagination__next--disabled"):

        end = time.time()
        # print(end)
        elapsed = end - start
        hour = elapsed // 3600
        minute = (elapsed % 3600) // 60
        second = (elapsed % 3600 % 60)
        elapsed_text = "処理時間：%d時間%d分%d秒" % (hour, minute, second)
        print(elapsed_text)
        break
    
    else:
        # 次のページがあればクリックして作業を続ける
        next_button = driver.find_element(By.CLASS_NAME, "c2-pagination__next")
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(2) # 読み飛ばしを防止するため、すべての要素が読み込まれるのを待つ    


df = pd.DataFrame(reviews, columns=['映画タイトル', '投稿者', '投稿日時', '評価', 'レビュー'])
df.index = df.index + 1
df.index.name = 'インデックス'
REVIEWS_PATH = "../reviews/"
df.to_csv("{}".format(REVIEWS_PATH) + film_title + "のレビュー・感想・評価.csv", encoding="utf-8_sig") 

driver.quit()

input()
