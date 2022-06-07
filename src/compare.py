# 評価用プログラム
import numpy as np
import pandas as pd
import math
import os
import itertools
from config import *

conf = config() #設定ファイルから読み込み

def cut_and_save(result,path):
    
    result = result[np.argsort(result[:, -1])] #ソート
    
    result_csv = pd.DataFrame(result) 
    result_csv.to_csv(path, header = False, index=False, encoding='utf_8_sig') #保存
    
    #結果値以外の列を削除            
    result = np.delete(result, np.s_[0:5], 1)
    result = np.delete(result, np.s_[3:4], 1)
    
    return result

def analysys(input,suhyo,name):
    # 音源サンプル数
    divideMusic = int(len(input) / conf.comb_num) #Nに相当でいいのか分からないけど今はそうしている

    list2 = np.zeros((conf.model_num,conf.model_num)) #表20.8の3*3行列に相当
    ai = np.zeros((len(list_hyoka),conf.model_num))

    res = []
    for i in range(len(list_hyoka)): #評価３つで回っている
        ai_sum = np.zeros((conf.model_num,)) #表20.9のxiの行に相当
        score_sum = np.zeros((conf.model_num,)) #表20.9の下三角の要素の値に相当
        Sab_bunshi = 0
        for ii in range(divideMusic): #音源数で回っている
            # 手順1 下三角にそのままの値，上三角に符号を反転したものを入れる
            alphas = input[ii*conf.comb_num:ii*conf.comb_num+conf.comb_num, i] #1組み合わせ分を取り出す
            list2[combi[:,0],combi[:,1]] = -alphas
            list2[combi[:,1],combi[:,0]] = alphas

            # 手順9Srを求める準備
            score_sum += alphas.astype(float)     

            # 手順2  (for文で何度もやることが手順3と同義 )
            tmp = np.sum(list2, axis=0) #表20.8のxiの行に相当
            ai_sum += tmp
            Sab_bunshi += np.dot(tmp,tmp) #表20.8 のxi^2の計の部分をひたすら足していく

        # 手順4 aiを推定する 手順5,6はなぜか無くても大丈夫
        ai[i,:] = ai_sum / (conf.model_num * divideMusic)

        # 手順7 Saを求める
        Sa = np.dot(ai_sum, ai_sum) / (conf.model_num * divideMusic) #分母は表20.9のxi^2の行の計に相当

        # 手順8 Sabを求める
        Sab = Sab_bunshi / conf.model_num - Sa

        # 手順9 Srを求める 表20.9を利用する方で求めている
        Sr = np.dot(score_sum,score_sum)  / divideMusic - Sa

        # 手順10 Stを求める      
        a = np.sum(np.abs(input[:,i]) == 1)
        b = np.sum(np.abs(input[:,i]) == 2)
        c = np.sum(np.abs(input[:,i]) == 3)
        St = 9 * c + 4 * b + a

        # 手順11 Seを求める
        Se = St - Sa - Sab - Sr

        # 手順12 誤差の不変分散を求める
        Sef = (conf.model_num - 1) * (conf.model_num - 2) * (divideMusic - 1) / 2

        # 手順13 ヤードスティックを求める 定数の4.60,6.97は比較対象と自由度で変化する（数表２２）
        if Sef > 120:
            yard = suhyo[114,conf.model_num-1]
        else:
            yard = suhyo[int(Sef-6),conf.model_num-1]
        y005 = yard * np.sqrt((Se / Sef) / (conf.model_num * divideMusic)) #3.82

        #手順14 信頼区間
        ai_custom = ai[i,combi[:,0]] - ai[i,combi[:,1]]
        ai_95plus = ai_custom + y005
        ai_95minus = ai_custom - y005
        for num13 in range(conf.comb_num):
            if ai_95minus[num13] * ai_95plus[num13] > 0:
                dd = list_hyoka[i] + "95%", conf.sound_name[combi[num13,0]], "-", conf.sound_name[combi[num13,1]]
                res.append(dd)

    # 結果の出力
    df = pd.DataFrame(
        {'1': [name], '2': ["音声の大きさ"], '3': ["音声の自然さ"], '4': ["雑音の大きさ"]})
    df.to_csv(save_path + '/result_all_subject.csv', mode='a', header=False, index=False, encoding='utf_8_sig')
    for i in range(conf.model_num):
        df = pd.DataFrame({'1': [conf.sound_name[i]], '2': [ai[0,i]], '3': [ai[1,i]], '4': [ai[2,i]]})
        df.to_csv(save_path + '/result_all_subject.csv', mode='a', header=False, index=False, encoding='utf_8_sig')
    for i in range(len(res)):
        df = pd.DataFrame(
            {'1': [res[i][0]], '2': [res[i][1]], '3': [res[i][2]], '4': [res[i][3]]})
        df.to_csv(save_path + '/result_all_subject.csv', mode='a', header=False, index=False, encoding='utf_8_sig')


# 評価項目
list_hyoka = ["音量", "自然", "雑音"]

# 被験者ごとの結果のパス
read_path = conf.exp_folder_path + "/result_each_subject"
# 分析結果の保存先
save_path = conf.exp_folder_path + "/result_all"

#ヤードスティックの固定値の数表
csv = pd.read_csv(conf.csv_path + 'suhyo.csv', header=0)
suhyo = csv.values

# 基準音と比較音の組み合わせ        
combi = np.array(list(itertools.combinations(range(conf.model_num), 2)))
   
# csvを読み込んで同じ配列を生成
rlt_files = os.listdir(read_path)
first_flag = True
for file in rlt_files:
    if ".csv" in file:
        # csvの読み込み
        csv = pd.read_csv(read_path + '/' + file, header=0)
        result = csv.values
        #雑音の結果を取り出す
        result_noise_tmp = result[0:conf.part_num*conf.comb_num,:]
        # 雑音を評価した配列を除外
        result_speech_tmp = np.delete(result, np.s_[0:conf.part_num*conf.comb_num], 0)
        if first_flag:
            result_speech = result_speech_tmp
            result_noise = result_noise_tmp
            first_flag = False
        else:
            result_speech = np.r_[result_speech,result_speech_tmp]
            result_noise = np.r_[result_noise,result_noise_tmp]     
result_speech = cut_and_save(result_speech,save_path + '/result_speech.csv')
result_noise = cut_and_save(result_noise,save_path + '/result_noise.csv')

#雑音下音声　全体
analysys(result_speech,suhyo,"全体")
rlt_reshape = np.zeros((0,conf.sn_num*len(list_hyoka)))
for i in range(int(len(result_speech)/conf.sn_num// conf.comb_num)):
    tmp = np.zeros((conf.comb_num,0))
    for ii in range(conf.sn_num):
        tmp = np.c_[tmp,result_speech[:conf.comb_num,:]]
        result_speech=np.delete(result_speech, np.s_[0:conf.comb_num], 0)
    rlt_reshape = np.r_[rlt_reshape,tmp]

#SN比ごと
for i in range(conf.sn_num):
    analysys(rlt_reshape[:,i*len(list_hyoka):(i+1)*3],suhyo,conf.sn_list[i])  

#雑音のみ
analysys(result_noise,suhyo,"雑音") 
        

