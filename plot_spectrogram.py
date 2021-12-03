#
# 計算機科学実験及演習 4「音響信号処理」
# サンプルソースコード
#
# 音声ファイルを読み込み，スペクトログラムを計算して図示する．
#

# ライブラリの読み込み
import matplotlib.pyplot as plt
import numpy as np
import librosa

# サンプリングレート
SR = 16000

# 音声ファイルの読み込み
x, _ = librosa.load('aiueo.wav', sr=SR)

#
# 短時間フーリエ変換
#

# フレームサイズ
size_frame = 512			# 2のべき乗

# フレームサイズに合わせてハミング窓を作成
hamming_window = np.hamming(size_frame)

# シフトサイズ
size_shift = 16000 / 100	# 0.01 秒 (10 msec)

# スペクトログラムを保存するlist
spectrogram = []

# size_shift分ずらしながらsize_frame分のデータを取得
# np.arange関数はfor文で辿りたい数値のリストを返す
# 通常のrange関数と違うのは3つ目の引数で間隔を指定できるところ
# (初期位置, 終了位置, 1ステップで進める間隔)
for i in np.arange(0, len(x)-size_frame, size_shift):
	
	# 該当フレームのデータを取得
	idx = int(i)	# arangeのインデクスはfloatなのでintに変換
	x_frame = x[idx : idx+size_frame]
	
	# 【補足】
	# 配列（リスト）のデータ参照
	# list[A:B] listのA番目からB-1番目までのデータを取得

	# 窓掛けしたデータをFFT
	# np.fft.rfftを使用するとFFTの前半部分のみが得られる
	fft_spec = np.fft.rfft(x_frame * hamming_window)
	
	# np.fft.fft / np.fft.fft2 を用いた場合
	# 複素スペクトログラムの前半だけを取得
	#fft_spec_first = fft_spec[:int(size_frame/2)]

	# 【補足】
	# 配列（リスト）のデータ参照
	# list[:B] listの先頭からB-1番目までのデータを取得

	# 複素スペクトログラムを対数振幅スペクトログラムに
	fft_log_abs_spec = np.log(np.abs(fft_spec))

	# 低周波の部分のみを拡大したい場合
	# 例えば、500Hzまでを拡大する
	# また、最後のほうの画像描画処理において、
	# 	extent=[0, len(x), 0, 500], 
	# にする必要があることに注意
	# size_target = int(len(fft_log_abs_spec) * (500 / (SR/2)))
	# fft_log_abs_spec = fft_log_abs_spec[:size_target]

	# 計算した対数振幅スペクトログラムを配列に保存
	spectrogram.append(fft_log_abs_spec)


#
# スペクトログラムを画像に表示・保存
#

# 画像として保存するための設定
fig = plt.figure()

# スペクトログラムを描画
plt.xlabel('sample')					# x軸のラベルを設定
plt.ylabel('frequency [Hz]')		# y軸のラベルを設定
plt.imshow(
	np.flipud(np.array(spectrogram).T),		# 画像とみなすために，データを転置して上下反転
	extent=[0, len(x), 0, SR/2],			# (横軸の原点の値，横軸の最大値，縦軸の原点の値，縦軸の最大値)
	aspect='auto',
	interpolation='nearest'
)
plt.show()

# 【補足】
# 縦軸の最大値はサンプリング周波数の半分 = 16000 / 2 = 8000 Hz となる

# 画像ファイルに保存
fig.savefig('plot-spectogram.png')


