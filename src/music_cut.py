import os
import struct
import wave
import random
import datetime
import pandas as pd
import numpy as np
import librosa
import pickle
import itertools
from config import *

conf = config() #設定ファイルから読み込み

def audio_write(out, wavname):
    # 正規化をしないで音声書き出し
    outd = [int(x * 32767.0) for x in out]  # [-32768, 32767]の整数値に変換
    outd = struct.pack("h" * len(outd), *outd)  # バイナリデータに変換

    with wave.Wave_write(wavname) as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        w.writeframes(outd)

def cut_data(load_path, write_path, wav_path, start, end, win):
    """
    load_path:読みこむフォルダ, write_path:書き込むフォルダ, wav_path:wavのパス（読みでも書きでも共通の部分）,
    start: 切りだし始め, end: 切りだし終わり
    """
    data, fs = librosa.load(load_path + wav_path, sr=24000, mono=False, res_type='polyphase')
    data_short = data[int(fs * start): int(fs * end)]
    if not "speech" in wav_path:
        data_short *= 10 ** (conf.large_db / 20)
    
    #フェードインフェードアウトの処理
    data_short[:conf.fade] = data_short[:conf.fade] * win[:conf.fade]
    data_short[-conf.fade:] = data_short[-conf.fade:] * win[conf.fade:]
    
    audio_write(data_short, write_path + wav_path)

# フォルダ生成
if not os.path.exists(conf.exp_folder_path):
    os.makedirs(conf.exp_folder_path + '/eval_data')
    os.makedirs(conf.exp_folder_path + '/result_all')
    os.makedirs(conf.exp_folder_path + '/result_each_subject')
    for num0 in range(len(conf.sound_name)):
        os.makedirs(conf.exp_folder_path + '/eval_data/' + conf.sound_name[num0])
        os.makedirs(conf.exp_folder_path + '/eval_data/' + conf.sound_name[num0] + '/speech')
        os.makedirs(conf.exp_folder_path + '/eval_data/' + conf.sound_name[num0] + '/noise')
save_path = conf.exp_folder_path + '/eval_data/' #保存先の共通部分パス

# 切りだし時間が書いてあるcsvの読み込み
speech_csv = pd.read_csv(conf.csv_path + 'sample_cut_5second.csv')
noise_csv = pd.read_csv(conf.csv_path + 'sample_noise_cut_5second.csv')
cut_speech = speech_csv.values.tolist()
cut_noise = noise_csv.values.tolist()

for i in range(len(cut_speech)): #音声の切りだし及び保存
    name = cut_speech[i][1]
    cut_time = cut_speech[i][2]
    end_time = cut_speech[i][3]
    for j in range(conf.model_num):
        cut_data(conf.load_path+conf.sound_path[j], save_path+conf.sound_name[j]+'/speech/' , str(name), cut_time, end_time, conf.win)

for i in range(len(cut_noise)): #雑音の切りだし及び保存
    name = cut_noise[i][0]
    cut_time = cut_noise[i][2]
    for j in range(conf.model_num):
        cut_data(conf.load_path+conf.sound_path[j], save_path+conf.sound_name[j]+'/noise/' , str(name), cut_time, cut_time + 5, conf.win)


# 音声の呼び出しリストの作成
cut_speech = speech_csv["FileName"].values.tolist()
cut_noise = noise_csv["wav_name"].values.tolist()
# cut_speechからsn_list_del内のsnrを除去する
if len(conf.sn_list_del) > 0:
    i = 0
    count = 0
    while i < len(conf.sn_list_del):
        if conf.sn_list_del[i] in str(cut_speech[count]):
            del cut_speech[count]
        count += 1
        if count >= len(cut_speech):
            count = 0
            i += 1

# 提示音源の総数
speech_total = int(conf.speech_num * conf.comb_num)
noise_total = int(conf.pattern_num * conf.comb_num)

data_set = np.zeros((speech_total, 4))
data_noise_set = np.zeros((noise_total, 4))

# シャッフルした音源をソートするためのナンバリング
# あとで、[wav名,基準モデル,評価モデル]の配列を作るため
data_noise_set[:, 3] = np.arange(noise_total)
data_set[:, 3] = np.arange(speech_total) + noise_total

# combinationの組み合わせ
combi = np.array(list(itertools.combinations(range(conf.model_num), 2)))
for num0 in range(conf.pattern_num):
    data_noise_set[num0 * conf.comb_num:(num0 + 1) * conf.comb_num, 1:3] = combi
for num1 in range(conf.sn_num):
    data_set[num1 * noise_total:(num1 + 1) * noise_total, 1:3] = data_noise_set[:, 1:3]

# listに変換
data_set = data_set.astype(int).tolist()
data_noise_set = data_noise_set.astype(int).tolist()

# ノイズの呼び出す順番を決める
noise_set = random.sample(range(0, conf.pattern_num), k=conf.pattern_num)

# 音声の呼び出す順番を決める
# speech_choice : 音源をsnrごとに分け、snrごとに2つランダムに抽出する為の値を入れる配列
speech_choice = np.arange(conf.sn_num * conf.pattern_num)
speech_choice = speech_choice.reshape([conf.sn_num, conf.pattern_num], order='F')
for num2 in range(conf.sn_num):  # シャッフル一度tmpで取り出さないと各行が同じシャッフルのされ方になってしまう
    tmp = speech_choice[num2, :]
    np.random.shuffle(tmp)
    speech_choice[num2, :] = tmp
speech_set = speech_choice.reshape([conf.sn_num * conf.pattern_num], order='F')

# 総当たり分wavの名前を増やす
i = 0
for num3 in range(conf.speech_num):
    for num4 in range(conf.comb_num):
        data_set[i][0] = cut_speech[speech_set[num3]]
        i += 1
i = 0
for num5 in range(conf.pattern_num):
    for num6 in range(conf.comb_num):
        data_noise_set[i][0] = cut_noise[noise_set[num5]]
        i += 1

# 1被験者辺りのデータをシャッフルする
for num7 in range(conf.sub_num):
    tmp_data = data_set[conf.part_s_num * num7: conf.part_s_num * (num7 + 1)]
    random.shuffle(tmp_data)
    data_set[conf.part_s_num * num7: conf.part_s_num * (num7 + 1)] = tmp_data

    tmp_data = data_noise_set[conf.part_n_num * num7: conf.part_n_num * (num7 + 1)]
    random.shuffle(tmp_data)
    data_noise_set[conf.part_n_num * num7: conf.part_n_num * (num7 + 1)] = tmp_data

f = open(conf.exp_folder_path + '/speech_list.txt', 'wb')
pickle.dump(data_set, f)

f = open(conf.exp_folder_path + '/noise_list.txt', 'wb')
pickle.dump(data_noise_set, f)

df = pd.DataFrame(data_set, columns=['wav_name','model1','model2','sort'])
df.to_csv(conf.exp_folder_path + '/data_set.csv')

df = pd.DataFrame(data_noise_set, columns=['wav_name','model1','model2','sort'])
df.to_csv(conf.exp_folder_path + '/data_noise_set.csv')




