import sys
import os
import time
import numpy as np
import colorama

colorama.init()

def main():
    chunk_size = 2048
    sample_rate = 44100
    bars = 60
    max_height = 20

    print('\033[2J', end='')
    prev_levels = [0] * bars

    count = 0
    try:
        while count < 20:
            count += 1
            data = np.random.randn(chunk_size)
            
            fft_data = np.abs(np.fft.rfft(data))
            
            min_freq_idx = max(1, int(20 * chunk_size / sample_rate))
            max_freq_idx = int(8000 * chunk_size / sample_rate)
            
            indices = np.logspace(np.log10(min_freq_idx), np.log10(max_freq_idx), bars + 1)
            indices = [int(i) for i in indices]
            
            levels = []
            for i in range(bars):
                start = indices[i]
                end = indices[i+1]
                if start == end: end += 1
                
                val = np.mean(fft_data[start:end])
                val = (val * 150) ** 0.8
                
                h = prev_levels[i] * 0.5 + val * 0.5
                h = min(max(h, 0), max_height)
                
                levels.append(h)
                prev_levels[i] = h
            
            sys.stdout.write('\033[H')

            for y in range(max_height, 0, -1):
                line = ""
                for x in range(bars):
                    level = levels[x]
                    if level >= y:
                        if y > max_height * 0.8:
                            color = colorama.Fore.RED
                        elif y > max_height * 0.5:
                            color = colorama.Fore.YELLOW
                        else:
                            color = colorama.Fore.GREEN
                        line += color + "█" + colorama.Style.RESET_ALL
                    elif y - level > 0 and y - level < 1:
                        line += colorama.Fore.GREEN + "▄" + colorama.Style.RESET_ALL
                    else:
                        line += " "
                sys.stdout.write(line + "\n")
            
            sys.stdout.flush()
            time.sleep(0.05)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
