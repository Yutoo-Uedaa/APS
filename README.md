# SUBJECT-TEST	README

 - 主観評価実験を行うためのコード
 - 弐号機で動いている

## Folder Structure


	├── data
	│    └── sub_eval  
	│         ├── data_through_model           <- 各処理(AINRなど)後の音源 
	│         ├── sample_cut_5second.csv       <- 提示音源長さにカットするためのcsv
	│         ├── sample_noise_cut_5second.csv <- 提示音源長さにカットするためのcsv	
	│         └── VOICEACTRESS100_007.wav      <- 音量調節用のサンプル音源
	└── DNN-NR-SUBJECT-TEST                    <- 本リポジトリのメイン  			 
	     ├── result                            <- 実験結果が保存されていく
	     │    └── example                      <- これを1セットにしてフォルダがどんどん増えていく
	     │        ├── eval_data                <- 提示音源
	     │        ├── result_all               <- 総評価
	     │        └── result_each_subject      <- 被験者ごとの結果
	     └── src                               <- ソースコード
	          ├── compare.py                   <- 結果分析用
	          ├── main.py                      <- 実験プログラム
	          └── music_cut	                   <- 提示音源用意用       	          

#
![image](https://user-images.githubusercontent.com/66341369/152265286-2d6a7190-9e13-4b4b-86da-637805694370.png)
