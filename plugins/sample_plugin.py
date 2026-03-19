import colorama

def render(levels, peak_levels, term_cols, term_lines, max_height, draw_bars, args, THEMES, STYLES):
    """
    Custom rendering plugin example.
    This draws a simple waveform using only '*' and center-aligned amplitudes.
    """
    left_padding = max(0, (term_cols - draw_bars) // 2)
    top_padding = max(0, term_lines - max_height - 1)
    
    frame_str = '\033[H' + '\n' * top_padding
    
    for y in range(max_height, 0, -1):
        line = " " * left_padding
        for x in range(draw_bars):
            level = levels[x]
            if level >= y:
                line += colorama.Fore.CYAN + "*" + colorama.Style.RESET_ALL
            else:
                line += " "
        
        if y != 1:
            frame_str += line + "\n"
        else:
            frame_str += line
            
    return frame_str
