import MeCab
import re
import config

common_word_list = [] # 全タイトルの単語リスト

class morphological_analysis: # 形態素解析用の関数のクラス

    def __init__(self): # コンストラクタ
        pass
    

    def bubble_sort(list): # バブルソート

        for i in range(len(list)-1):

            for j in range(len(list)-2, i-1, -1):

                if list[j+1][1] > list[j][1]:
                    tmp = list[j]
                    list[j] = list[j+1]
                    list[j+1] = tmp
        
        return list
    

    def morpho(text): # テキストの形態素解析
            
        # 形態素解析
        tagger = MeCab.Tagger()
        parsed = tagger.parse(text)

        lines = parsed.split('\n')
        items = (re.split('[\t,、".．「」!！-－・?？【】()（）…/~～_]', line) for line in lines)
        
        # 単語と品詞を取り出す
        morphoed_text = []
        number_of_sentences = 0
        for item in items:            
            word = []
                
            if item[0] not in ('EOS', '') :
                match item[1]:
                    # 自立語のみ抽出
                    # 原形を加える
                    case '名詞':
                        word.append(item[0])
                        word.append(item[1])
                        morphoed_text.append(word)  

                    case '動詞':
                        word.append(item[8])
                        word.append(item[1]) 
                        morphoed_text.append(word) 
                    
                    case '形容詞':
                        word.append(item[8])
                        word.append(item[1]) 
                        morphoed_text.append(word)

                    case '補助記号':
                        if(item[2]=='句点'):
                            number_of_sentences += 1                       


        return morphoed_text, number_of_sentences
    

    def generate_word_list(morphoed_text): 
        # 単語リストの作成
        
        flag = False

        w_list = []

        # 初期値
        init_w = []
        init_w.append("") 
        init_w.append("") 
        w_list.append(init_w)        

        for word in morphoed_text:

            for w_list_e in w_list:                

                # 単語が単語リストにあった場合
                if word[0] == w_list_e[0] and word[1] == w_list_e[1]:
                    flag = True
                    break
            
            # 単語が単語リストにあった場合
            if flag == True:
                flag = False
                continue      

            # 単語が単語リストになかった場合
            w_list.append(word)

        
        del w_list[0:1]

        return w_list


    def generate_freq_list(morphoed_text): 
        # 解析したテキスト内の単語の出現度数のリスト（単語度数リスト）を作成する関数

        af_list = []

        # 初期値
        init_af = []
        init_w = []
        init_w.append("") 
        init_w.append("") 
        init_af.append(init_w)
        init_af.append(0)
        af_list.append(init_af)

        flag = False # 単語が単語度数リストにあることを示すフラグ

        for word in morphoed_text:

            for a_freq in af_list:

                # 単語が単語度数リストにあった場合
                if word[0] == a_freq[0][0] and word[1] == a_freq[0][1]:
                    a_freq[1] += 1
                    flag = True
                    break
            
            # 単語が単語度数リストにあった場合
            if flag == True:
                flag = False
                continue      

            # 単語が単語度数リストになかった場合
            a_freq = []
            a_freq.append(word)
            a_freq.append(1)
            af_list.append(a_freq)
        
        del af_list[0:1]

        return af_list

    
    def count_text_freq(morphoed_text, w_list): 
        # 単語リストの単語の形態素解析されたテキスト中での出現度数を数える関数

        freq_list = []

        for word in w_list:

            freq_list_e = []
            freq_list_e.append(word) 
            freq_list_e.append(0)

            for e in morphoed_text:

                if word[0] == e[0] and word[1] == e[1]:

                    freq_list_e[1] += 1

            
            freq_list.append(freq_list_e)


        return freq_list
    


    

 








    


        



           





    







    