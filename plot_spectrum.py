#
# 計算機科学実験及演習 4「音響信号処理」
# サンプルソースコード
#
# 音声ファイルを読み込み，フーリエ変換を行う．
#

# ライブラリの読み込み
import matplotlib.pyplot as plt
import numpy as np
import librosa

# サンプリングレート
SR = 16000

# 音声ファイルの読み込み
x, _ = librosa.load('a.wav', sr=SR)

# 高速フーリエ変換
# np.fft.rfftを使用するとFFTの前半部分のみが得られる
fft_spec = np.fft.rfft(x)

# 複素スペクトルを対数振幅スペクトルに
fft_log_abs_spec = np.log(np.abs(fft_spec))

#
# スペクトルを画像に表示・保存
#

# 画像として保存するための設定
fig = plt.figure()

# スペクトログラムを描画
plt.xlabel('frequency [Hz]')		# x軸のラベルを設定
plt.ylabel('amplitude')				# y軸のラベルを設定
plt.xlim([0, SR/2])					# x軸の範囲を設定
# x軸のデータを生成（元々のデータが0~8000Hzに対応するようにする）
#x_data = np.linspace((SR/2)/len(fft_log_abs_spec), SR/2, len(fft_log_abs_spec))
x_data = np.fft.rfftfreq(len(x), d=1/SR)
plt.plot(x_data, fft_log_abs_spec)			# 描画
# 【補足】
# 縦軸の最大値はサンプリング周波数の半分 = 16000 / 2 = 8000 Hz となる

# 表示
plt.show()

# 画像ファイルに保存
fig.savefig('plot-spectrum-whole.png')

# 横軸を0~2000Hzに拡大
# xlimで表示の領域を変えるだけ
fig = plt.figure()
plt.xlabel('frequency [Hz]')
plt.ylabel('amplitude')
plt.xlim([0, 2000])
plt.plot(x_data, fft_log_abs_spec)

# 表示
plt.show()

# 画像ファイルに保存
fig.savefig('plot-spectrum-2000.png')
