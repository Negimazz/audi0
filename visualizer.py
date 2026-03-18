import sys
import sys
import os
import time
import numpy as np
import warnings
import pyaudiowpatch as pyaudio
import colorama

warnings.filterwarnings("ignore")

# WindowsのネイティブANSI（VT100）を有効化し、coloramaの遅いフックを無効化することで完全なチカチカ防止を実現
os.system('')

# ソフト名のアスキーアート
ASCII_ART = r"""
 █████╗ ██╗   ██╗██████╗ ██╗ ██████╗ 
██╔══██╗██║   ██║██╔══██╗██║██╔═══██╗
███████║██║   ██║██║  ██║██║██║   ██║
██╔══██║██║   ██║██║  ██║██║██║   ██║
██║  ██║╚██████╔╝██████╔╝██║╚██████╔╝
╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝ ╚═════╝ 
           A U D I 0
"""

def print_intro():
    os.system('cls' if os.name == 'nt' else 'clear')
    colors = [colorama.Fore.CYAN, colorama.Fore.MAGENTA, colorama.Fore.BLUE]
    lines = ASCII_ART.strip().split('\n')
    for i, line in enumerate(lines):
        print(colors[i % len(colors)] + line)
        time.sleep(0.1)
    
    # 作者名「yyy was here.」をいい感じに追加
    print("\n" + " " * 15 + colorama.Fore.YELLOW + colorama.Style.BRIGHT + "yyy was here." + colorama.Style.RESET_ALL)
    print("\n" + " " * 10 + colorama.Fore.GREEN + "Windows System Audio Visualizer" + colorama.Style.RESET_ALL)
    print(" " * 10 + "Initializing audio capture...\n")
    time.sleep(1.5)

def main():
    print_intro()

    try:
        p = pyaudio.PyAudio()
        wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        
        if not default_speakers["isLoopbackDevice"]:
            for loopback in p.get_loopback_device_info_generator():
                if default_speakers["name"] in loopback["name"]:
                    default_speakers = loopback
                    break
        
        channels = default_speakers["maxInputChannels"]
        sample_rate = int(default_speakers["defaultSampleRate"])
        
    except Exception as e:
        print(colorama.Fore.RED + f"システムオーディオの取得に失敗しました: {e}" + colorama.Style.RESET_ALL)
        return

    print("システムオーディオをリッスンしています... 終了するには Ctrl+C を押してください")
    print(colorama.Fore.YELLOW + "※注意: Windowsの仕様上、音が鳴っていないとここで待機状態（フリーズ）になります。" + colorama.Style.RESET_ALL)
    print(colorama.Fore.YELLOW + "ビジュアライザーを動かすには何か音楽や動画を再生してください。" + colorama.Style.RESET_ALL)
    time.sleep(3)

    os.system('cls' if os.name == 'nt' else 'clear')

    fft_size = 4096
    read_chunk = 1024
    bars = 80  # 全体の幅を少し短く調整
    max_height = 20
    
    print('\033[?25l', end='')  # カーソルを隠す
    print('\033[2J', end='')
    prev_levels = [0] * bars
    peak_levels = [0] * bars
    audio_buffer = np.zeros(fft_size, dtype=np.float32)

    try:
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=channels,
            rate=sample_rate,
            frames_per_buffer=read_chunk,
            input=True,
            input_device_index=default_speakers["index"]
        )
        stream.start_stream()
        
        while True:
            try:
                # 512サンプルごとに読み込み、高フレームレート化（約86FPS）
                in_data = stream.read(read_chunk, exception_on_overflow=False)
            except IOError as e:
                time.sleep(0.01)
                continue
                
            new_data = np.frombuffer(in_data, dtype=np.float32)
            if len(new_data) == 0:
                time.sleep(0.01)
                continue
                
            if channels > 1:
                # モノラルに変換
                new_data = new_data.reshape(-1, channels).mean(axis=1)

            # バッファをスライドさせ、最新の2048サンプルを保持（スライディングウィンドウ）
            audio_buffer = np.roll(audio_buffer, -len(new_data))
            audio_buffer[-len(new_data):] = new_data

            # ハニング窓をかけてFFTのノイズを抑える
            window = np.hanning(fft_size)
            windowed = audio_buffer * window

            fft_data = np.abs(np.fft.rfft(windowed))
            
            min_freq_idx = max(1, int(20 * fft_size / sample_rate))
            max_freq_idx = int(8000 * fft_size / sample_rate)
            
            indices = np.logspace(np.log10(min_freq_idx), np.log10(max_freq_idx), bars + 1)
            indices = [int(i) for i in indices]
            
            raw_levels = []
            for i in range(bars):
                start = min(indices[i], len(fft_data)-1)
                end = min(indices[i+1], len(fft_data))
                if start >= end: end = start + 1
                
                val = np.mean(fft_data[start:end]) if end > start else 0
                val = (val * 20) ** 0.7  # 感度補正
                
                # アタック・リリースの非対称スムージング
                # 上下のガクガクをなくすため、上がる時（アタック）も少しゆっくり（0.2）にする
                if val > prev_levels[i]:
                    h = prev_levels[i] * 0.8 + val * 0.2
                else:
                    h = prev_levels[i] * 0.95 + val * 0.05
                    
                h = min(max(h, 0), max_height)
                
                raw_levels.append(h)
                prev_levels[i] = h
            
            # 周波数方向のスムージング
            levels = []
            for i in range(bars):
                ll = raw_levels[max(0, i-2)]
                l  = raw_levels[max(0, i-1)]
                c  = raw_levels[i]
                r  = raw_levels[min(bars-1, i+1)]
                rr = raw_levels[min(bars-1, i+2)]
                smoothed = ll * 0.1 + l * 0.2 + c * 0.4 + r * 0.2 + rr * 0.1
                levels.append(smoothed)
                
            # ピークホールド
            for i in range(bars):
                peak_levels[i] = max(levels[i], peak_levels[i] - 0.35)
                # 無音時にvが消えたり点滅したりするのを防ぐため、最低値を0.9に固定する
                if peak_levels[i] < 0.9:
                    peak_levels[i] = 0.9
            
            # ターミナルの横幅より波形が長いと表示がバグるのを防ぐため、描画する最大幅を計算
            try:
                term_size = os.get_terminal_size()
                term_cols = term_size.columns
                term_lines = term_size.lines
            except Exception:
                term_cols = 100
                term_lines = 30
                
            draw_bars = min(bars, term_cols - 1)
            left_padding = max(0, (term_cols - draw_bars) // 2)  # 波形を真ん中に寄せるための空白数を計算
            top_padding = max(0, term_lines - max_height - 1)    # 波形をターミナルの最下部に配置するための空白行数

            frame_str = '\033[H'
            frame_str += '\n' * top_padding

            for y in range(max_height, 0, -1):
                line = " " * left_padding  # 左側に空白を入れて波形全体を中央に押し出す
                active_color = ""
                
                if y > max_height * 0.5:
                    row_color = colorama.Fore.RED
                elif y > max_height * 0.25:
                    row_color = colorama.Fore.YELLOW
                else:
                    row_color = colorama.Fore.GREEN
                        
                # ターミナルの横幅に収まる範囲のみ描画する
                for x in range(draw_bars):
                    level = levels[x]
                    peak = peak_levels[x]
                    
                    target_color = ""
                    char = " "
                    
                    # ピークの描画
                    if y - peak > 0 and y - peak <= 1:
                        target_color = colorama.Fore.WHITE
                        char = "v"
                    elif level >= y:
                        target_color = row_color
                        char = "│"
                    elif y - level > 0 and y - level < 1:
                        target_color = row_color
                        char = "╽"
                    
                    # 不要なANSIコードの連続出力を防ぎ、ターミナルのチカチカを防止する
                    if char == " ":
                        if active_color != "":
                            line += colorama.Style.RESET_ALL
                            active_color = ""
                        line += " "
                    else:
                        if active_color != target_color:
                            line += target_color
                            active_color = target_color
                        line += char

                if active_color != "":
                    line += colorama.Style.RESET_ALL
                
                # 最後の行は改行しない
                if y != 1:
                    frame_str += line + "\n"
                else:
                    frame_str += line
            
            # 一括で書き込むことでチカチカ（ティアリング）を完全に防ぐ
            sys.stdout.write(frame_str)
            sys.stdout.flush()
                
    except KeyboardInterrupt:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(colorama.Fore.CYAN + "ビジュアライザーを終了しました。" + colorama.Style.RESET_ALL)
    except Exception as e:
        print(colorama.Style.RESET_ALL + f"\nエラーが発生しました: {e}")
    finally:
        print('\033[?25h')  # カーソルを元に戻す
        print()             # プロンプトが崩れないように改行を入れる
        if 'stream' in locals() and stream.is_active():
            stream.stop_stream()
            stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
