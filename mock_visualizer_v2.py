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
    peak_levels = [0] * bars

    count = 0
    try:
        while count < 40:
            count += 1
            # Mock audio data
            data = np.random.randn(chunk_size) * 0.5
            # Add some spikes
            if count % 5 == 0:
                data += np.sin(np.linspace(0, 100, chunk_size)) * 5
            
            fft_data = np.abs(np.fft.rfft(data))
            
            min_freq_idx = max(1, int(20 * chunk_size / sample_rate))
            max_freq_idx = int(8000 * chunk_size / sample_rate)
            
            indices = np.logspace(np.log10(min_freq_idx), np.log10(max_freq_idx), bars + 1)
            indices = [int(i) for i in indices]
            
            raw_levels = []
            for i in range(bars):
                start = min(indices[i], len(fft_data)-1)
                end = min(indices[i+1], len(fft_data))
                if start >= end: end = start + 1
                
                val = np.mean(fft_data[start:end]) if end > start else 0
                val = (val * 80) ** 0.7  # Reduced sensitivity
                
                h = prev_levels[i] * 0.75 + val * 0.25  # Increased temporal smoothing
                h = min(max(h, 0), max_height)
                
                raw_levels.append(h)
                prev_levels[i] = h
                
            # Frequency smoothing (spatial)
            levels = []
            for i in range(bars):
                left = raw_levels[i-1] if i > 0 else raw_levels[i]
                right = raw_levels[i+1] if i < bars-1 else raw_levels[i]
                smoothed = 0.2 * left + 0.6 * raw_levels[i] + 0.2 * right
                levels.append(smoothed)
                
            # Peak hold update
            for i in range(bars):
                # slow fall
                peak_levels[i] = max(levels[i], peak_levels[i] - 0.5)
            
            sys.stdout.write('\033[H')

            for y in range(max_height, 0, -1):
                line = ""
                for x in range(bars):
                    level = levels[x]
                    peak = peak_levels[x]
                    
                    # Colors
                    if y > max_height * 0.7:
                        color = colorama.Fore.MAGENTA
                    elif y > max_height * 0.4:
                        color = colorama.Fore.CYAN
                    else:
                        color = colorama.Fore.BLUE
                        
                    # Peak drawing
                    if y - peak > 0 and y - peak <= 1:
                        line += colorama.Fore.WHITE + "v" + colorama.Style.RESET_ALL
                    elif level >= y:
                        # Solid body
                        line += color + "│" + colorama.Style.RESET_ALL
                    elif y - level > 0 and y - level <= 1:
                        # Top of the bar
                        line += color + "╽" + colorama.Style.RESET_ALL
                    else:
                        line += " "
                sys.stdout.write(line + "\n")
            
            sys.stdout.flush()
            time.sleep(0.05)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
