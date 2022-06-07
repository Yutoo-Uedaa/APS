import os
import time
import datetime
import pandas as pd
import streamlit as st
import numpy as np
import pickle
from config import *

conf = config() #設定ファイルから読み込み

kyouji = """本実験は、雑音抑制機能の性能評価として、雑音の「大きさ」、音声の「大きさ」、「自然さ」を評価するものです。
                    \n提示された基準音と評価音を聴いて、相対的評価を以下の3つの観点から7段階で評価してください。
                    \n・雑音の大きさ 　　 ・・・雑音が大きいか、うるさいか
                    \n・音声の大きさ 　　 ・・・音声部分の音量感があるか（SNRでなく音声のみで評価）
                    \n・音声の自然さ 　 　・・・音声が自然にきこえるか、滑らかであるか
                    \n本実験では雑音の評価をおこなった後、雑音下音声の評価をしていただきます。
                    \n音は何度聞き返してもかまいません。評価がおわりましたら「次の試験音へ」のボタンを押してください""" #教示文

# 試行回数のカウンター
def inc_count():
    st.session_state.count += 1
    # print(st.session_state.count)
    # ページの更新
    st.experimental_rerun()

# 一度だけ実行
@st.cache
def deyTimeCheck(alpha, beta):
    dt_now = str(datetime.date.today())
    return str(alpha + beta + dt_now)

# スライドバーから、数値を返す
def format_func1(option):
    return CHOICES1[option]

def format_func2(option):
    return CHOICES2[option]

def format_func3(option):
    return CHOICES3[option]

# ここの変数だけは保存されていく
if 'count' not in st.session_state: #ページ番号をつかさどっている
    st.session_state.count = -2
if 'group' not in st.session_state:
    st.session_state.group = -1
if 'key' not in st.session_state:
    st.session_state.key = 'value'
if 'time' not in st.session_state:
    st.session_state.time = 0
if 'time2' not in st.session_state:
    st.session_state.time2 = 0


f = open(conf.exp_folder_path + "/speech_list.txt","rb")
speech_list = pickle.load(f) #音声の再生順の読み出し

f = open(conf.exp_folder_path + "/noise_list.txt","rb") #雑音の再生順の読み出し
noise_list = pickle.load(f)



st.title('聴覚心理実験')
# 画面 1ページ目
if st.session_state.count == -2:
    
    explainBef = st.empty()
    with explainBef.expander("実験の説明", True):
        st.write(kyouji)

    sizi = st.empty()
    sizi.subheader('実験前のお願い')
    
    sizi2 = st.empty()
    sizi2.write('本実験はヘッドホンでの参加をお願い致します。'
                'こちらの音が聞きやすい大きさでPCの音量を調節し実験中はいじらないでください')
    
    testSound = st.empty()
    testSound.write('ボリューム調整用のサンプル音')
    audio_file_test = open(conf.csv_path + 'VOICEACTRESS100_007.wav', 'rb')
    audio_file_test_bytes = audio_file_test.read()
    testSound.audio(audio_file_test_bytes, start_time=0)

    # 名前と年代の入力
    sizi3 = st.empty()
    sizi3.write('名前と年代を入力してください')
    explain = st.empty()
    with explain.form("my_form"):

        sub_name = st.text_input("名前を入力してください   　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　"
                          "　　　　　 　　　　  　　　　　 "
                          "例：リオン太郎さんの場合 >>>　t_rion")
        sub_age = st.selectbox('年代を選択してください', ('20代', '30代', '40代', '50代', '60代', '非公表',))
        # Every form must have a submit button.
        submitted = st.form_submit_button("次へ")
    # 名前が入力され、開始ボタンが押された時
    if submitted and sub_name != "":
        # 画面 2ページ目
        # csvのname
        st.session_state.key = str(deyTimeCheck(str(sub_name), str(sub_age)))
        explainBef.empty()
        explain.empty()
        sizi.empty()
        sizi2.empty()
        sizi3.empty()
        testSound.empty()
        st.session_state.count = -1
        # result_csv内のcsvを数える
        csv_file = os.listdir(conf.exp_folder_path + '/result_each_subject')
        # csvの数を総実験パターン数で割り、出た余りを実験パターンに設定する
        st.session_state.group = len(csv_file) % conf.sub_num
        df = pd.DataFrame({'1': ["group" + str(st.session_state.group)], '2': ["main"], '3': ["compare"],
                           '4': ["main_num"], '5': ["compare_num"], '6': ["音量"], '7': ["自然"], '8': ["雑音"],
                           '9': ["wav_num"]})

        df.to_csv(conf.exp_folder_path + '/result_each_subject/'+str(st.session_state.group)+ '_' + st.session_state.key + '.csv', mode='a',
                  header=False, index=False,
                  encoding='utf_8_sig')

    elif submitted:
        st.warning('名前を入力して下さい')
        
# 画面 2ページ目
if st.session_state.count == -1:
    sizi = st.empty()
    sizi.subheader('提示音サンプル')
    sizi2 = st.empty()
    sizi2.write('評価対象音源のサンプルをお聞きください．')
    sizi3 = st.empty()
    sizi3.write('※まだ実験は始まっていません')   
    
    #おやゆずりのムテッポウデを選んでみた
    testSound1 = st.empty()
    testSound1.write('モデル')
    audio_file_test = open(conf.exp_folder_path + '/eval_data/'+ conf.sound_name[0] +'/speech/speech2_0s-noise7-SNR0.wav', 'rb')
    audio_file_test_bytes = audio_file_test.read()
    testSound1.audio(audio_file_test_bytes, start_time=0)
    
    testSound2 = st.empty()
    testSound2.write('モデル')
    audio_file_test = open(conf.exp_folder_path + '/eval_data/'+ conf.sound_name[1] +'/speech/speech2_0s-noise7-SNR0.wav', 'rb')
    audio_file_test_bytes = audio_file_test.read()
    testSound2.audio(audio_file_test_bytes, start_time=0)
    
    testSound3 = st.empty()
    testSound3.write('モデル')
    audio_file_test = open(conf.exp_folder_path + '/eval_data/'+ conf.sound_name[2] +'/speech/speech2_0s-noise7-SNR0.wav', 'rb')
    audio_file_test_bytes = audio_file_test.read()
    testSound3.audio(audio_file_test_bytes, start_time=0)
    
    sizi4 = st.empty()
    sizi4.write('それでは準備が整いましたら以下のボタンを押して始めてください．')    
    
    start = st.empty()
    with start.form("my_form2"):
        start_button= st.form_submit_button("実験を始める")
    if start_button:
        sizi.empty()
        sizi2.empty()
        sizi3.empty()
        testSound1.empty()
        testSound2.empty()
        testSound3.empty()
        sizi4.empty()
        start.empty()
        st.session_state.count = 0  
    
# 3ページ目以降　評価画面
if st.session_state.count >= 0:
    with st.expander('実験の説明', False):
        st.write(kyouji)

    sabato = st.empty()
    if st.session_state.count < conf.part_n_num:
        sabato.title('雑音フェーズ')
    if st.session_state.count >= conf.part_n_num:
        sabato.empty()
        st.title('雑音下音声フェーズ')

    # プログレスバー
    st.write('進捗' + str(st.session_state.count) + '/' + str(conf.trials))
    my_bar = st.progress(0)
    my_bar.progress(int(st.session_state.count * 100 / conf.trials))
    # 実験終了
    if st.session_state.count == conf.trials:
        print('subject_' + st.session_state.key + '_main.csv is close')
        my_bar.progress(100)
        st.title('実験は終了です。ご協力ありがとうございました。ブラウザを閉じてください')
        st.balloons()
        st.stop()
    # 音の呈示
    st.write('基準音')
    if st.session_state.count < conf.part_n_num:
        hairetu = st.session_state.group * conf.part_n_num + st.session_state.count
        audio_file = open(conf.exp_folder_path + '/eval_data/' +
                          str(conf.sound_name[noise_list[hairetu][1]]) +
                          '/noise/' + str(noise_list[hairetu][0]), 'rb')

    if st.session_state.count > conf.part_n_num - 1:
        hairetu = st.session_state.group * conf.part_s_num + st.session_state.count - conf.part_n_num
        audio_file = open(conf.exp_folder_path + '/eval_data/' +
                          str(conf.sound_name[speech_list[hairetu][1]]) +
                          '/speech/' + str(speech_list[hairetu][0]), 'rb')

    audio_bytes = audio_file.read()
    st.audio(audio_bytes, start_time=0)

    st.write('評価音')
    # 雑音の評価結果の保存
    if st.session_state.count < conf.part_n_num:
        hairetu = st.session_state.group * conf.part_n_num + st.session_state.count
        audio_file_b = open(conf.exp_folder_path + '/eval_data/' +
                            str(conf.sound_name[noise_list[hairetu][2]]) + "/noise/" +
                            str(noise_list[hairetu][0]), 'rb')
    # 雑音化音声の評価結果の保存
    if st.session_state.count > conf.part_n_num - 1:
        hairetu = st.session_state.group * conf.part_s_num + st.session_state.count - conf.part_n_num
        audio_file_b = open(conf.exp_folder_path + '/eval_data/' +
                            str(conf.sound_name[speech_list[hairetu][2]]) + "/speech/" +
                            str(speech_list[hairetu][0]), 'rb')

    audio_file_b_bytes = audio_file_b.read()
    st.audio(audio_file_b_bytes, start_time=0)

    st.subheader('基準音と評価音を比較して以下の項目を７段階で評価してください')
    # スライドバーを動かしたとき表示される
    CHOICES1 = {-3: "非常に小さい", -2: "小さい", -1: "やや小さい", 0: "どちらともいえない",
                1: "やや大きい", 2: "大きい", 3: "非常に大きい"}

    CHOICES2 = {-3: "非常に不自然", -2: "不自然", -1: "やや不自然", 0: "どちらともいえない",
                1: "やや自然", 2: "自然", 3: "非常に自然"}
    
    CHOICES3 = {3: "非常に小さい", 2: "小さい", 1: "やや小さい", 0: "どちらともいえない",
                -1: "やや大きい", -2: "大きい", -3: "非常に大きい"}

    # 評価項目
    noise1 = st.empty()
    noise1_label = st.empty
    # チャタリング防止
    st.session_state.time = time.time()
    # 雑音フェーズは「雑音」のみの評価バーを出す
    if st.session_state.count < conf.part_n_num:
        option3 = noise1.select_slider('雑音の大きさ', options=list(CHOICES3.keys()),
                                       format_func=format_func3, key=st.session_state.count + 3, value=0,
                                       help='非常に小さい--小さい--やや小さい--どちらともいえない--やや大きい--大きい--非常に大きい')
    # 雑音フェーズのバーを消す
    if st.session_state.count == conf.part_n_num:
        noise1.empty()
    # 雑音化音声フェーズの評価バーを出す
    if st.session_state.count >= conf.part_n_num:
        option3 = st.select_slider('雑音の大きさ', options=list(CHOICES3.keys()),
                                   format_func=format_func3, key=st.session_state.count + 3, value=0,
                                   help='非常に小さい--小さい--やや小さい--どちらともいえない--やや大きい--大きい--非常に大きい')
        st.write(' ')
        st.write(' ')
        option1 = st.select_slider('音声の大きさ', options=list(CHOICES1.keys()),
                                   format_func=format_func1, key=st.session_state.count + 1, value=0,
                                   help='非常に小さい--小さい--やや小さい--どちらともいえない--やや大きい--大きい--非常に大きい')
        st.write(' ')
        st.write(' ')
        option2 = st.select_slider('音声の自然さ', options=list(CHOICES2.keys()),
                                   format_func=format_func2, key=st.session_state.count + 2, value=0,
                                   help='非常に不自然--不自然--やや不自然--どちらともいえない--やや自然--自然--非常に自然')
    st.subheader("-3　　　-2　　　-1　　　　0　　　　1　　 　2　　  　3")

    # ダブルクリック防止  条件文
    if st.button('次の試験音へ') and (st.session_state.time - st.session_state.time2) > 2:
        st.session_state.time2 = time.time()
        # 雑音：csvに評価結果を保存　wav名,基準モデル名,評価モデル名,基準モデルラベル,評価モデルラベル,[音量感][自然さ][雑音]の評価値[-3:3]
        if st.session_state.count < conf.comb_num * conf.part_num:
            hairetu = st.session_state.group * conf.part_n_num + st.session_state.count
            df = pd.DataFrame(
                {'1': [noise_list[hairetu][0]],
                 '2': [conf.sound_name[noise_list[hairetu][1]]],
                 '3': [conf.sound_name[noise_list[hairetu][2]]],
                 '4': [noise_list[hairetu][1]],
                 '5': [noise_list[hairetu][2]],
                 '6': [0], '7': [0], '8': [option3],
                 '9': [noise_list[hairetu][3]]})

            df.to_csv(conf.exp_folder_path + '/result_each_subject/'+str(st.session_state.group)+ '_' + st.session_state.key + '.csv', mode='a',
                      header=False, index=False,
                      encoding='utf_8_sig')

        else:
            hairetu = st.session_state.group * conf.part_s_num + st.session_state.count - conf.part_n_num
            # 雑音化音声：csvに評価結果を保存　wav名,基準モデル名,評価モデル名,基準モデルラベル,評価モデルラベル,[音量感][自然さ][雑音]の評価値[-3:3]

            df = pd.DataFrame(
                {'1': [speech_list[hairetu][0]],
                 '2': [conf.sound_name[speech_list[hairetu][1]]],
                 '3': [conf.sound_name[speech_list[hairetu][2]]],
                 '4': [speech_list[hairetu][1]],
                 '5': [speech_list[hairetu][2]],
                 '6': [option1], '7': [option2], '8': [option3],
                 '9': [speech_list[hairetu][3]]})

            df.to_csv(conf.exp_folder_path + '/result_each_subject/'+str(st.session_state.group)+ '_' + st.session_state.key + '.csv', mode='a',
                      header=False, index=False,
                      encoding='utf_8_sig')
            # 音を変える,試行回数を数えるカウンター
        inc_count()
    # プログレスバー
    st.write('進捗' + str(st.session_state.count) + '/' + str(conf.trials))
    my_bar2 = st.progress(0)
    my_bar2.progress(int(st.session_state.count * 100 / conf.trials))
    
