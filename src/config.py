import numpy as np
from scipy.special import comb

class config: # モードの選択
    def __init__(self):

        self.exp_folder_name = "20220217_SLoss_SNgauss" # 実験結果のメインフォルダ名   
        self.sound_name = ["NR", "AINR", "NR+AINR"] #実験対象の呼び名
        self.sound_path = ["NR/wav/", "20220215_limS_hrtf_mask_snr5_10/wav_copy/nomix/", "20220215_limS_hrtf_mask_snr5_10/wav_copy/mix0.5/"] #sound_nameと対応させてそれぞれのパス
            
        #音の前処理
        self.large_db = 5 #雑音の提示音圧を何dB上げるか
        self.fade = 240 #ここで指定したサンプル数分だけ窓をかけてフェードイン，フェードアウトする
        self.win = np.hanning(self.fade*2)
        
        # 提示音源のsnr ['SNR-10', 'SNR-5', 'SNR0', 'SNR5', 'SNR10'] を　sn_list と sn_list_delに分ける
        self.sn_list = ['SNR-5', 'SNR0', 'SNR5', 'SNR10']
        # 今回の実験で使わないsnr 
        self.sn_list_del = ['SNR-10']
        
        # 雑音パターン数
        self.pattern_num = 36
        # 1被験者あたりの雑音パターン数
        self.part_num = 2 
        
        #以下は変更のない変数たち
        self.csv_path = '../../data/sub_eval/' #csvのパス
        self.load_path = "../../../svdata/学習結果/" #sound_path前の共通パス
        self.exp_folder_path = '../result/' + self.exp_folder_name #実験結果のメインフォルダパス
        
        self.model_num = len(self.sound_name)
        self.sn_num = len(self.sn_list)
        self.speech_num = self.pattern_num * self.sn_num #雑音下音声のパターン数
        self.comb_num = comb(self.model_num, 2, exact=True) #1音源当たりのモデルの組み合わせパターン数
        
        self.part_s_num = self.part_num * self.comb_num * self.sn_num # 1被験者あたりの雑音下音声の試行回数
        self.part_n_num = self.part_num * self.comb_num # 1被験者あたりの雑音の試行回数
        self.trials = self.part_s_num + self.part_n_num # 1被験者辺りの試行回数
        
        '''
        ↓この変数はどんな値になるか要確認，割り切れないとコード上手く動かないかも
        '''
        self.sub_num = int(self.pattern_num / self.part_num) # 全音源が実験に使用されるのに必要な被験者数
