#
# 計算機科学実験及演習 4「音響信号処理」
# サンプルソースコード
#
# 音声ファイルを読み込みスペクトログラムを表示する
# その隣に時間を選択するスライドバーと選択した時間に対応したスペクトルを表示する
# GUIのツールとしてTkinterを使用する
#

# ライブラリの読み込み
import librosa
import numpy as np
import matplotlib.pyplot as plt
import tkinter

# MatplotlibをTkinterで使用するために必要
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

size_frame = 4096	# フレームサイズ
SR = 16000			# サンプリングレート
size_shift = 16000 / 100	# シフトサイズ = 0.001 秒 (10 msec)

# 音声ファイルを読み込む
x, _ = librosa.load('aiueo.wav', sr=SR)

# ファイルサイズ（秒）
duration = len(x) / SR

# ハミング窓
hamming_window = np.hamming(size_frame)

# スペクトログラムを保存するlist
spectrogram = []

# フレーム毎にスペクトルを計算
for i in np.arange(0, len(x)-size_frame, size_shift):
	
	# 該当フレームのデータを取得
	idx = int(i)	# arangeのインデクスはfloatなのでintに変換
	x_frame = x[idx : idx+size_frame]
	
	# スペクトル
	fft_spec = np.fft.rfft(x_frame * hamming_window)
	fft_log_abs_spec = np.log(np.abs(fft_spec))
	spectrogram.append(fft_log_abs_spec)

# Tkinterを初期化
root = tkinter.Tk()
root.wm_title("EXP4-AUDIO-SAMPLE")

# Tkinterのウィジェットを階層的に管理するためにFrameを使用
# frame1 ... スペクトログラムを表示
# frame2 ... Scale（スライドバー）とスペクトルを表示
frame1 = tkinter.Frame(root)
frame2 = tkinter.Frame(root)
frame1.pack(side="left")
frame2.pack(side="left")

# まずはスペクトログラムを描画
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=frame1)	# masterに対象とするframeを指定
plt.xlabel('sec')
plt.ylabel('frequency [Hz]')
plt.imshow(
	np.flipud(np.array(spectrogram).T),
	extent=[0, duration, 0, 8000],
	aspect='auto',
	interpolation='nearest'
)
canvas.get_tk_widget().pack(side="left")	# 最後にFrameに追加する処理

# スライドバーの値が変更されたときに呼び出されるコールバック関数
# ここで右側のグラフに
# vはスライドバーの値
def _draw_spectrum(v):

	# スライドバーの値からスペクトルのインデクスおよびそのスペクトルを取得
	index = int((len(spectrogram)-1) * (float(v) / duration))
	spectrum = spectrogram[index]

	# 直前のスペクトル描画を削除し，新たなスペクトルを描画
	plt.cla()
	x_data = np.fft.rfftfreq(size_frame, d=1/SR)
	ax2.plot(x_data, spectrum)
	ax2.set_ylim(-10, 5)
	ax2.set_xlim(0, SR/2)
	ax2.set_ylabel('amblitude')
	ax2.set_xlabel('frequency [Hz]')
	canvas2.draw()

# スペクトルを表示する領域を確保
# ax2, canvs2 を使って上記のコールバック関数でグラフを描画する
fig2, ax2 = plt.subplots()
canvas2 = FigureCanvasTkAgg(fig2, master=frame2)
canvas2.get_tk_widget().pack(side="top")	# "top"は上部方向にウィジェットを積むことを意味する

# スライドバーを作成
scale = tkinter.Scale(
	command=_draw_spectrum,		# ここにコールバック関数を指定
	master=frame2,				# 表示するフレーム
	from_=0,					# 最小値
	to=duration,				# 最大値
	resolution=size_shift/SR,	# 刻み幅
	label=u'スペクトルを表示する時間[sec]',
	orient=tkinter.HORIZONTAL,	# 横方向にスライド
	length=600,					# 横サイズ
	width=50,					# 縦サイズ
	font=("", 20)				# フォントサイズは20pxに設定
)
scale.pack(side="top")

# TkinterのGUI表示を開始
tkinter.mainloop()
