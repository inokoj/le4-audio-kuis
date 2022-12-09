#
# 計算機科学実験及演習 4「音響信号処理」
# サンプルソースコード
#
# クロマベクトルを算出
#

import math
import numpy

# 周波数からノートナンバーへ変換（notenumber.pyより）
def hz2nn(frequency):
	return int (round (12.0 * (math.log(frequency / 440.0) / math.log (2.0)))) + 69

#
# スペクトルと対応する周波数ビンの情報を受け取り，クロマベクトルを算出
#
# 【周波数ビンの情報について補足】
# 例えば，サンプリング周波数が16000の場合は，spectrumは8000Hzまでの情報を保持していることになるため，
# spectrumのサイズが512だとすると，
# frequencies = [1 * (8000/512), 2 * (8000/512), ..., 511 * (8000/512), 8000] とすればよい
# このような処理をnumpyで実現するばらば，
# frequencies = np.linspace(8000/len(spectrum), 8000, len(spectrum)) などどすればよい
#
def chroma_vector(spectrum, frequencies):
	
	# 0 = C, 1 = C#, 2 = D, ..., 11 = B

	# 12次元のクロマベクトルを作成（ゼロベクトルで初期化）
	cv = numpy.zeros(12)
	
	# スペクトルの周波数ビン毎に
	# クロマベクトルの対応する要素に振幅スペクトルを足しこむ
	for s, f in zip (spectrum , frequencies):
		nn = hz2nn(f)
		cv[nn % 12] += abs(s)
	
	return cv