import sys
import os
import time
import numpy as np
import warnings
import argparse
import json
import importlib

try:
    import pyaudiowpatch as pyaudio
    HAS_WASAPI = True
except ImportError:
    import pyaudio
    HAS_WASAPI = False

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

THEMES = {
    'default': [colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.RED],
    'ocean': [colorama.Fore.BLUE, colorama.Fore.CYAN, colorama.Fore.LIGHTBLUE_EX],
    'fire': [colorama.Fore.RED, colorama.Fore.LIGHTRED_EX, colorama.Fore.YELLOW],
    'matrix': [colorama.Fore.GREEN, colorama.Fore.LIGHTGREEN_EX, colorama.Fore.GREEN],
}

STYLES = {
    'default': {'full': '│', 'half': '╽', 'peak': '_'},
    'block': {'full': '█', 'half': '▄', 'peak': '_'},
    'dot': {'full': '•', 'half': '·', 'peak': '*'}
}

def get_color(color_code, no_color):
    return "" if no_color else color_code

def hex_to_ansi(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        try:
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return f"\033[38;2;{r};{g};{b}m"
        except ValueError:
            pass
    return ""

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                custom_themes = data.get("custom_themes", {})
                for t_name, hex_list in custom_themes.items():
                    if isinstance(hex_list, list) and len(hex_list) >= 3:
                        THEMES[t_name] = [hex_to_ansi(h) for h in hex_list[:3]]
                return data
        except Exception as e:
            print(colorama.Fore.RED + f"Error loading config: {e}" + colorama.Style.RESET_ALL)
    return {}

def save_config(args):
    old_data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
        except Exception:
            pass
            
    config = {
        "bars": args.bars,
        "height": args.height,
        "theme": args.theme,
        "mic": args.mic,
        "device": args.device,
        "sensitivity": args.sensitivity,
        "auto_sens": getattr(args, 'auto_sens', False),
        "agc_speed": getattr(args, 'agc_speed', 0.05),
        "fps": args.fps,
        "style": args.style,
        "no_color": args.no_color,
        "plugin": getattr(args, 'plugin', None),
        "custom_themes": old_data.get("custom_themes", {})
    }
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        print(colorama.Fore.GREEN + "Configuration saved to config.json successfully." + colorama.Style.RESET_ALL)
    except Exception as e:
        print(colorama.Fore.RED + f"Error saving config: {e}" + colorama.Style.RESET_ALL)

def parse_args():
    config = load_config()
    parser = argparse.ArgumentParser(description="Terminal Audio Visualizer")
    parser.add_argument("--bars", type=int, default=80, help="Number of bars to display (default: 80)")
    parser.add_argument("--height", type=int, default=20, help="Maximum height of the visualizer (default: 20)")
    parser.add_argument("--theme", type=str, choices=list(THEMES.keys()), default='default', help="Color theme for the visualizer")
    parser.add_argument("--mic", action="store_true", help="Force listening to the default microphone instead of system audio")
    parser.add_argument("--device", type=int, default=None, help="Specific PyAudio device index to use (optional)")
    parser.add_argument("--sensitivity", type=float, default=1.0, help="Audio sensitivity multiplier (default: 1.0)")
    parser.add_argument("--auto-sens", action="store_true", help="Enable automatic sensitivity adjustment (AGC)")
    parser.add_argument("--agc-speed", type=float, default=0.05, help="Speed of auto-sensitivity adjustment (default: 0.05)")
    parser.add_argument("--fps", type=int, default=60, help="Target frames per second (default: 60)")
    parser.add_argument("--style", type=str, choices=list(STYLES.keys()), default='default', help="Display style mode")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--save", action="store_true", help="Save the current command-line arguments to config.json and exit")
    parser.add_argument("--menu", action="store_true", help="Open an interactive TUI to configure settings")
    parser.add_argument("--plugin", type=str, default=None, help="Name of a plugin script in the plugins/ folder to use")
    
    parser.set_defaults(**config)
    
    return parser.parse_args()

def print_intro(args):
    os.system('cls' if os.name == 'nt' else 'clear')
    colors = THEMES[args.theme]
    lines = ASCII_ART.strip().split('\n')
    for i, line in enumerate(lines):
        c = get_color(colors[i % len(colors)], args.no_color)
        print(c + line + get_color(colorama.Style.RESET_ALL, args.no_color))
        time.sleep(0.05)
    
    # 作者名「yyy was here.」をいい感じに追加
    c_yellow = get_color(colorama.Fore.YELLOW + colorama.Style.BRIGHT, args.no_color)
    c_green = get_color(colorama.Fore.GREEN, args.no_color)
    c_reset = get_color(colorama.Style.RESET_ALL, args.no_color)
    
    print("\n" + " " * 15 + c_yellow + "yyy was here." + c_reset)
    print("\n" + " " * 10 + c_green + "Audio Visualizer" + c_reset)
    print(" " * 10 + f"Theme: {args.theme} | Bars: {args.bars} | Height: {args.height} | FPS: {args.fps}")
    auto_txt = f"Auto (Speed: {getattr(args, 'agc_speed', 0.05)})" if getattr(args, 'auto_sens', False) else f"x{args.sensitivity}"
    print(" " * 10 + f"Style: {args.style} | Sensitivity: {auto_txt}")
    mode = "Microphone" if args.mic or not HAS_WASAPI else "System Loopback (WASAPI)"
    print(" " * 10 + f"Input Mode: {mode}" + (" (Monochrome)" if args.no_color else ""))
    print("\n" + " " * 10 + "Initializing audio capture...\n")
    time.sleep(1.0)

def input_menu(prompt, choices):
    while True:
        print(prompt)
        for idx, choice in enumerate(choices, 1):
            print(f"  [{idx}] {choice}")
        try:
            sel = input("Select number (or 0 to cancel): ").strip()
            if not sel: continue
            sel_int = int(sel)
            if sel_int == 0:
                return None
            if 1 <= sel_int <= len(choices):
                return choices[sel_int - 1]
        except ValueError:
            pass

def interactive_menu(args):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(colorama.Style.BRIGHT + colorama.Fore.CYAN + "=== audi0 Configuration Menu ===" + colorama.Style.RESET_ALL)
        print(f"1. Theme        : {args.theme}")
        print(f"2. Style        : {args.style}")
        print(f"3. Bars         : {args.bars}")
        print(f"4. Height       : {args.height}")
        print(f"5. FPS          : {args.fps}")
        auto_str = f"ON (Speed: {getattr(args, 'agc_speed', 0.05)})" if getattr(args, 'auto_sens', False) else f"OFF (Base: {args.sensitivity})"
        print(f"6. Sensitivity  : {auto_str}")
        print(f"7. Microphone   : {'Yes' if args.mic else 'No'}")
        print(f"8. Monochrome   : {'Yes' if args.no_color else 'No'}")
        print(f"9. Plugin       : {getattr(args, 'plugin', 'None') or 'None'}")
        print("-" * 32)
        print("A. Auto Sensitivity Toggle")
        print("S. Save Config to config.json")
        print("Q. Quit Menu")
        
        choice = input("\nSelect an option: ").strip().lower()
        
        if choice == '1':
            res = input_menu("\n-- Select Theme --", list(THEMES.keys()))
            if res: args.theme = res
        elif choice == '2':
            res = input_menu("\n-- Select Style --", list(STYLES.keys()))
            if res: args.style = res
        elif choice == '3':
            try: args.bars = int(input("\nEnter bars (e.g. 80): "))
            except ValueError: pass
        elif choice == '4':
            try: args.height = int(input("\nEnter maximum height (e.g. 20): "))
            except ValueError: pass
        elif choice == '5':
            try: args.fps = int(input("\nEnter target FPS (e.g. 60): "))
            except ValueError: pass
        elif choice == '6':
            if getattr(args, 'auto_sens', False):
                try: 
                    speed = input(f"\nEnter auto-sensitivity speed (current: {getattr(args, 'agc_speed', 0.05)}): ").strip()
                    if speed: setattr(args, 'agc_speed', float(speed))
                except ValueError: pass
            else:
                try: args.sensitivity = float(input("\nEnter sensitivity (e.g. 1.0): "))
                except ValueError: pass
        elif choice == '7':
            args.mic = not args.mic
        elif choice == '8':
            args.no_color = not args.no_color
        elif choice == '9':
            p = input("\nEnter plugin module name (or blank for none): ").strip()
            args.plugin = p if p else None
        elif choice == 'a':
            auto_sens = not getattr(args, 'auto_sens', False)
            setattr(args, 'auto_sens', auto_sens)
        elif choice == 's':
            save_config(args)
            input("Press Enter to continue...")
        elif choice == 'q':
            break

def main():
    args = parse_args()
    
    if args.save:
        save_config(args)
        return
        
    if getattr(args, 'menu', False):
        interactive_menu(args)
        return

    renderer_plugin = None
    if getattr(args, 'plugin', None):
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            plugin_module = importlib.import_module(f"plugins.{args.plugin}")
            if hasattr(plugin_module, 'render'):
                renderer_plugin = plugin_module.render
                print(colorama.Fore.CYAN + f"Loaded plugin '{args.plugin}' successfully!" + colorama.Style.RESET_ALL)
            else:
                print(colorama.Fore.RED + f"Plugin '{args.plugin}' missing 'render()' function." + colorama.Style.RESET_ALL)
        except Exception as e:
            print(colorama.Fore.RED + f"Error loading plugin '{args.plugin}': {e}" + colorama.Style.RESET_ALL)
            time.sleep(2)

    print_intro(args)

    try:
        if HAS_WASAPI and not args.mic:
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
            device_index = default_speakers["index"]
        else:
            # Mac/Linux または マイク入力モード
            p = pyaudio.PyAudio()
            default_input = p.get_default_input_device_info()
            channels = min(2, default_input.get("maxInputChannels", 1))
            sample_rate = int(default_input.get("defaultSampleRate", 44100))
            device_index = default_input["index"] if args.device is None else args.device
            
    except Exception as e:
        c_red = get_color(colorama.Fore.RED, args.no_color)
        c_reset = get_color(colorama.Style.RESET_ALL, args.no_color)
        print(c_red + f"音声デバイスの取得に失敗しました: {e}" + c_reset)
        return

    print("オーディオをリッスンしています... 終了するには Ctrl+C を押してください")
    c_yellow = get_color(colorama.Fore.YELLOW, args.no_color)
    c_cyan = get_color(colorama.Fore.CYAN, args.no_color)
    c_reset = get_color(colorama.Style.RESET_ALL, args.no_color)
    
    if HAS_WASAPI and not args.mic:
        print(c_yellow + "※注意: Windowsの仕様上、音が鳴っていないとここで待機状態（フリーズ）になります。" + c_reset)
        print(c_yellow + "ビジュアライザーを動かすには何か音楽や動画を再生してください。" + c_reset)
    else:
        print(c_cyan + "マイクからの入力を待機しています。" + c_reset)
    time.sleep(2)

    os.system('cls' if os.name == 'nt' else 'clear')

    fft_size = 4096
    # チャンクサイズをサンプリングレートと目標FPSに基づいて計算
    read_chunk = max(256, int(sample_rate / args.fps))
    bars = args.bars  # 引数からバーの数を取得
    max_height = args.height  # 引数から最大高さを取得
    
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
            input_device_index=device_index
        )
        stream.start_stream()
        
        last_time = time.time()
        fps_history = []
        dynamic_sensitivity = getattr(args, 'sensitivity', 1.0)
        
        while True:
            try:
                # 512サンプルごとに読み込み、高フレームレート化（約86FPS）
                in_data = stream.read(read_chunk, exception_on_overflow=False)
            except IOError as e:
                time.sleep(0.01)
                continue
                
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            if dt > 0:
                fps_history.append(1.0 / dt)
            if len(fps_history) > 20:
                fps_history.pop(0)
            avg_fps = sum(fps_history) / len(fps_history) if fps_history else 0
            
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
                val = (val * 20 * dynamic_sensitivity) ** 0.7  # 感度補正
                
                # アタック・リリースの非対称スムージング
                # 上下のガクガクをなくすため、上がる時（アタック）も少しゆっくり（0.2）にする
                if val > prev_levels[i]:
                    h = prev_levels[i] * 0.8 + val * 0.2
                else:
                    h = prev_levels[i] * 0.95 + val * 0.05
                    
                h = min(max(h, 0), max_height)
                
                raw_levels.append(h)
                prev_levels[i] = h
            
            # === 自動感度調整 (AGC) ===
            if getattr(args, 'auto_sens', False):
                current_peak = max(raw_levels) if raw_levels else 0
                target_peak = max_height * 0.6  # 全体の約60%付近の高さをキープ目標とする
                if current_peak > 0.5:
                    error = target_peak / current_peak
                    error = min(max(error, 0.5), 1.5)  # 急すぎる感度の変動を防止
                    speed = getattr(args, 'agc_speed', 0.05)
                    dynamic_sensitivity *= 1.0 + (error - 1.0) * speed
                else:
                    # 無音状態のときはゆっくりと基本の感度に戻していく
                    base_sens = getattr(args, 'sensitivity', 1.0)
                    dynamic_sensitivity = dynamic_sensitivity * 0.99 + base_sens * 0.01
                
                # 異常値を防ぐための制限
                dynamic_sensitivity = min(max(dynamic_sensitivity, 0.01), 30.0)
            else:
                dynamic_sensitivity = getattr(args, 'sensitivity', 1.0)
            # =======================
            
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
            top_padding = max(0, term_lines - max_height - 2)    # 波形をターミナルの最下部に配置するための空白行数 (ステータスバー分-1)

            if renderer_plugin:
                try:
                    frame_str = renderer_plugin(levels, peak_levels, term_cols, term_lines, max_height, draw_bars, args, THEMES, STYLES)
                except Exception as e:
                    frame_str = f"Plugin Render Error: {e}\n"
            else:
                frame_str = '\033[H'
                frame_str += '\n' * top_padding

                for y in range(max_height, 0, -1):
                    line = " " * left_padding  # 左側に空白を入れて波形全体を中央に押し出す
                    active_color = ""
                    
                    if y > max_height * 0.6:
                        row_color = THEMES[args.theme][2]
                    elif y > max_height * 0.3:
                        row_color = THEMES[args.theme][1]
                    else:
                        row_color = THEMES[args.theme][0]
                            
                    # ターミナルの横幅に収まる範囲のみ描画する
                    for x in range(draw_bars):
                        level = levels[x]
                        peak = peak_levels[x]
                        
                        target_color = ""
                        char = " "
                        
                        # ピークの描画
                        if y - peak > 0 and y - peak <= 1:
                            target_color = get_color(colorama.Fore.WHITE, args.no_color)
                            char = STYLES[args.style]['peak']
                        elif level >= y:
                            target_color = get_color(row_color, args.no_color)
                            char = STYLES[args.style]['full']
                        elif y - level > 0 and y - level < 1:
                            target_color = get_color(row_color, args.no_color)
                            char = STYLES[args.style]['half']
                        
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
            
            # ===== ステータスバーの描画 =====
            auto_txt = f"Auto({dynamic_sensitivity:.1f})" if getattr(args, 'auto_sens', False) else f"x{args.sensitivity:.1f}"
            status_text = f" FPS: {int(avg_fps):3d} | Theme: {args.theme} | Style: {args.style} | Sens: {auto_txt} "
            if not args.no_color:
                bar_color = colorama.Fore.LIGHTBLACK_EX  # 少し暗めのテキストに変更
                reset_color = colorama.Style.RESET_ALL
            else:
                bar_color = ""
                reset_color = ""
                
            padded_status = status_text.center(term_cols)[:term_cols]
            frame_str += f"\n{bar_color}{padded_status}{reset_color}"
            # ===============================
            
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
