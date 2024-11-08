#
# 計算機科学実験及演習 4「音響信号処理」
# サンプルソースコード
#
# 簡易カラオケシステム
#
# mp3ファイルを別スレッドで再生しつつ
# マイクからの音声入力に対してスペクトログラムとパワーを計算して表示する
# 上記をリアルタイムで逐次処理を行う
#

# ライブラリの読み込み
import sounddevice as sd
import numpy as np
import threading
import time

# matplotlib関連
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

# GUI関連
import tkinter
from matplotlib.backends.backend_tkagg import (
	FigureCanvasTkAgg, NavigationToolbar2Tk)

# mp3ファイルを読み込んで再生
from pydub import AudioSegment
from pydub.utils import make_chunks

# サンプリングレート
SAMPLING_RATE = 16000

# フレームサイズ
FRAME_SIZE = 2048

# サイズシフト
SHIFT_SIZE = int(SAMPLING_RATE / 20)	# 今回は0.05秒

# スペクトルをカラー表示する際に色の範囲を正規化するために
# スペクトルの最小値と最大値を指定
# スペクトルの値がこの範囲を超えると，同じ色になってしまう
SPECTRUM_MIN = -5
SPECTRUM_MAX = 1

# 音量を表示する際の値の範囲
VOLUME_MIN = -120
VOLUME_MAX = -10

# log10を計算する際に，引数が0にならないようにするためにこの値を足す
EPSILON = 1e-10

# ハミング窓
hamming_window = np.hamming(FRAME_SIZE)

# グラフに表示する縦軸方向のデータ数
MAX_NUM_SPECTROGRAM = int(FRAME_SIZE / 2)

# グラフに表示する横軸方向のデータ数
NUM_DATA_SHOWN = 100

# GUIの開始フラグ（まだGUIを開始していないので、ここではFalseに）
is_gui_running = False

#
# (1) GUI / グラフ描画の処理
#

# ここでは matplotlib animation を用いて描画する
# 毎回 figure や ax を初期化すると処理時間がかかるため
# データを更新したら，それに従って必要な部分のみ再描画することでリアルタイム処理を実現する

# matplotlib animation によって呼び出される関数
# ここでは最新のスペクトログラムと音量のデータを格納する
# 再描画はmatplotlib animationが行う
def animate(frame_index):

	ax1_sub.set_array(spectrogram_data)

	# この上の処理を下記のようにすれば楽曲のスペクトログラムが表示される
	# ax1_sub.set_array(spectrogram_data_music)
	
	ax2_sub.set_data(time_x_data, volume_data)
	
	return ax1_sub, ax2_sub

# GUIで表示するための処理（Tkinter）
root = tkinter.Tk()
root.wm_title("EXP4-AUDIO-SAMPLE")

# スペクトログラムを描画
fig, ax1 = plt.subplots(1, 1)
canvas = FigureCanvasTkAgg(fig, master=root)

# 横軸の値のデータ
time_x_data = np.linspace(0, NUM_DATA_SHOWN * (SHIFT_SIZE/SAMPLING_RATE), NUM_DATA_SHOWN)
# 縦軸の値のデータ
freq_y_data = np.linspace(8000/MAX_NUM_SPECTROGRAM, 8000, MAX_NUM_SPECTROGRAM)

# とりあえず初期値（ゼロ）のスペクトログラムと音量のデータを作成
# この numpy array にデータが更新されていく
spectrogram_data = np.zeros((len(freq_y_data), len(time_x_data)))
volume_data = np.zeros(len(time_x_data))

# 楽曲のスペクトログラムを格納するデータ（このサンプルでは計算のみ）
spectrogram_data_music = np.zeros((len(freq_y_data), len(time_x_data)))

# スペクトログラムを描画する際に横軸と縦軸のデータを行列にしておく必要がある
# これは下記の matplotlib の pcolormesh の仕様のため
X = np.zeros(spectrogram_data.shape)
Y = np.zeros(spectrogram_data.shape)
for idx_f, f_v in enumerate(freq_y_data):
	for idx_t, t_v in enumerate(time_x_data):
		X[idx_f, idx_t] = t_v
		Y[idx_f, idx_t] = f_v

# pcolormeshを用いてスペクトログラムを描画
# 戻り値はデータの更新 & 再描画のために必要
ax1_sub = ax1.pcolormesh(
	X,
	Y,
	spectrogram_data,
	shading='nearest',	# 描画スタイル
	cmap='jet',			# カラーマップ
	norm=Normalize(SPECTRUM_MIN, SPECTRUM_MAX)	# 値の最小値と最大値を指定して，それに色を合わせる
)

# 音量を表示するために反転した軸を作成
ax2 = ax1.twinx()

# 音量をプロットする
# 戻り値はデータの更新 & 再描画のために必要
ax2_sub, = ax2.plot(time_x_data, volume_data, c='y')

# ラベルの設定
ax1.set_xlabel('sec')				# x軸のラベルを設定
ax1.set_ylabel('frequency [Hz]')	# y軸のラベルを設定
ax2.set_ylabel('volume [dB]')		# 反対側のy軸のラベルを設定

# 音量を表示する際の値の範囲を設定
ax2.set_ylim([VOLUME_MIN, VOLUME_MAX])

# maplotlib animationを設定
ani = animation.FuncAnimation(
	fig,
	animate,		# 再描画のために呼び出される関数
	interval=100,	# 100ミリ秒間隔で再描画を行う（PC環境によって処理が追いつかない場合はこの値を大きくするとよい）
	blit=True		# blitting処理を行うため描画処理が速くなる（環境によってうまく動作しない場合はこれをFalseにしてみること）
)

# matplotlib を GUI(Tkinter) に追加する
toolbar = NavigationToolbar2Tk(canvas, root)
canvas.get_tk_widget().pack()

# 再生位置をテキストで表示するためのラベルを作成
text = tkinter.StringVar()
text.set('0.0')
label = tkinter.Label(master=root, textvariable=text, font=("", 30))
label.pack()

# 終了ボタンが押されたときに呼び出される関数
# ここではGUIを終了する
def _quit():
	root.quit()
	root.destroy()

# 終了ボタンを作成
button = tkinter.Button(master=root, text="終了", command=_quit, font=("", 30))
button.pack()


#
# (2) マイク入力のための処理
#

x_stacked_data = np.array([])

# フレーム毎に呼び出される関数
def input_callback(in_data, frames, time, status):
	
	# この関数は別スレッドで実行するため
	# メインスレッドで定義した以下の２つの numpy array を利用できるように global 宣言する
	# これらにはフレーム毎のスペクトルと音量のデータが格納される
	global x_stacked_data, spectrogram_data, volume_data

	# 現在のフレームの音声データをnumpy arrayに変換
	x_current_frame = np.frombuffer(in_data, dtype=np.float32)

	# 現在のフレームとこれまでに入力されたフレームを連結
	x_stacked_data = np.concatenate([x_stacked_data, x_current_frame])

	# フレームサイズ分のデータがあれば処理を行う
	if len(x_stacked_data) >= FRAME_SIZE:
		
		# フレームサイズからはみ出した過去のデータは捨てる
		x_stacked_data = x_stacked_data[len(x_stacked_data)-FRAME_SIZE:]

		# スペクトルを計算
		fft_spec = np.fft.rfft(x_stacked_data * hamming_window)
		fft_log_abs_spec = np.log10(np.abs(fft_spec) + EPSILON)[:-1]

		# ２次元配列上で列方向（時間軸方向）に１つずらし（戻し）
		# 最後の列（＝最後の時刻のスペクトルがあった位置）に最新のスペクトルデータを挿入
		spectrogram_data = np.roll(spectrogram_data, -1, axis=1)
		spectrogram_data[:, -1] = fft_log_abs_spec

		# 音量も同様の処理
		vol = 20 * np.log10(np.mean(x_current_frame ** 2) + EPSILON)
		volume_data = np.roll(volume_data, -1)
		volume_data[-1] = vol

# マイクからの音声入力にはsounddeviceを使用
# ここではsounddeviceの再生ストリームを作成
# 【注意】シフトサイズごとに指定された関数が呼び出される

stream = sd.InputStream(
        channels=1,
        dtype='float32',
        callback=input_callback,
		samplerate=SAMPLING_RATE,
		blocksize=SHIFT_SIZE
)
stream.start()


#
# (3) mp3ファイル音楽を再生する処理
#

# mp3ファイル名
# ここは各自の音源ファイルに合わせて変更すること
filename = './mp3/hotaru_no_hikari.mp3'

#
# 【注意】なるべく1チャネルの音声を利用すること
# ステレオ（2チャネル）の場合は SoX などでモノラルに変換できる
# sox stereo.wav -c 1 mono.wav
#

# pydubを使用して音楽ファイルを読み込む
audio_data = AudioSegment.from_mp3(filename)

# 音声ファイルの再生にはsounddeviceを使用
# ここではsounddeviceの再生ストリームを作成

# 【注意】音楽ファイルのサンプリングレートとチャンネル数を確認しておくこと
sampling_rate = audio_data.frame_rate
channels = audio_data.channels

stream_play = sd.OutputStream(
	samplerate=sampling_rate, 
    channels=channels,
    dtype='int16'
)
stream_play.start()

# 楽曲のデータを格納
x_stacked_data_music = np.array([])

# pydubで読み込んだ音楽ファイルを再生する部分のみ関数化する
# 別スレッドで実行するため
def play_music():

	# この関数は別スレッドで実行するため
	# メインスレッドで定義した以下の２つの変数を利用できるように global 宣言する
	global stream_play, is_gui_running, audio_data, now_playing_sec, x_stacked_data_music, spectrogram_data_music

	# pydubのmake_chunksを用いて音楽ファイルのデータを切り出しながら読み込む
	# 第二引数には何ミリ秒毎に読み込むかを指定
	# ここでは10ミリ秒ごとに読み込む

	size_frame_music = 10	# 10ミリ秒毎に読み込む

	idx = 0

	# make_chunks関数を使用して一定のフレーム毎に音楽ファイルを読み込む
	#
	# なぜ再生するだけのためにフレーム毎の処理をするのか？
	# 音楽ファイルに対しても何らかの処理を行えるようにするため（このサンプルプログラムでは行っていない）
	# おまけに，再生位置も計算することができる
	for chunk in make_chunks(audio_data, size_frame_music):
		
		# GUIが終了してれば，この関数の処理も終了する
		if is_gui_running == False:
			break

		# pyaudioの再生ストリームに切り出した音楽データを流し込む
		# 再生が完了するまで処理はここでブロックされる
		#stream_play.write(chunk._data)
		#print(chunk._data)

		# チャンクをNumPy配列に変換
		samples = np.array(chunk.get_array_of_samples(), dtype=np.int16)
		
		# ステレオの場合、2次元配列に変換
		if channels == 2:
			samples = samples.reshape((-1, 2))
		
		stream_play.write(samples) # chunkの信号を書き込み
		
		# 現在の再生位置を計算（単位は秒）
		now_playing_sec = (idx * size_frame_music) / 1000.
		
		idx += 1

		#
		# 【補足】
		# 楽曲のスペクトログラムを計算する場合には下記のように楽曲のデータを受け取る
		# ただし，音声データの値は -1.0~1.0 ではなく，16bit の整数値であるので正規化を施している
		# また十分なサイズの音声データを確保してからfftを実行すること
		# 楽曲が44.1kHzの場合，44100 / (1000/10) のサイズのデータとなる
		# 以下では処理のみを行い，表示はしない．表示をするには animate 関数の中身を変更すること 
		
		# データの取得
		data_music = np.array(chunk.get_array_of_samples())
		
		# 正規化
		data_music = data_music / np.iinfo(np.int32).max	

		#
		# 以下はマイク入力のときと同様
		#

		# 現在のフレームとこれまでに入力されたフレームを連結
		x_stacked_data_music = np.concatenate([x_stacked_data_music, data_music])

		# フレームサイズ分のデータがあれば処理を行う
		if len(x_stacked_data_music) >= FRAME_SIZE:
			
			# フレームサイズからはみ出した過去のデータは捨てる
			x_stacked_data_music = x_stacked_data_music[len(x_stacked_data_music)-FRAME_SIZE:]

			# スペクトルを計算
			fft_spec = np.fft.rfft(x_stacked_data_music * hamming_window)
			fft_log_abs_spec = np.log10(np.abs(fft_spec) + EPSILON)[:-1]

			# ２次元配列上で列方向（時間軸方向）に１つずらし（戻し）
			# 最後の列（＝最後の時刻のスペクトルがあった位置）に最新のスペクトルデータを挿入
			spectrogram_data_music = np.roll(spectrogram_data_music, -1, axis=1)
			spectrogram_data_music[:, -1] = fft_log_abs_spec

# 再生時間の表示を随時更新する関数
def update_gui_text():

	global is_gui_running, now_playing_sec, text

	while True:
		
		# GUIが表示されていれば再生位置（秒）をテキストとしてGUI上に表示
		if is_gui_running:
			text.set('%.3f' % now_playing_sec)
		
		# 0.01秒ごとに更新
		time.sleep(0.01)

# 再生時間を表す
now_playing_sec = 0.0

# 音楽を再生するパートを関数化したので，それを別スレッドで（GUIのため）再生開始
t_play_music = threading.Thread(target=play_music)
t_play_music.setDaemon(True)	# GUIが消されたときにこの別スレッドの処理も終了されるようにするため

# 再生時間の表示を随時更新する関数を別スレッドで開始
t_update_gui = threading.Thread(target=update_gui_text)
t_update_gui.setDaemon(True)	# GUIが消されたときにこの別スレッドの処理も終了されるようにするため

#
# (4) 全体の処理を実行
#

# GUIの開始フラグをTrueに
is_gui_running = True

# 上記で設定したスレッドを開始（直前のフラグを立ててから）
t_play_music.start()
t_update_gui.start()

# GUIを開始，GUIが表示されている間は処理はここでストップ
tkinter.mainloop()

# GUIの開始フラグをFalseに = 音楽再生スレッドのループを終了
is_gui_running = False

# 終了処理
stream_play.stop()
stream_play.close()
# p_play.terminate()
