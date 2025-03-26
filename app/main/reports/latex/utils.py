def find_closing_brace(text, start_pos, open_char='{', close_char='}'):
    """
    Находит позицию закрывающей скобки с учётом вложенности.
    
    Args:
        text (str): Текст для поиска
        start_pos (int): Стартовая позиция поиска (после открывающей скобки)
        open_char (str, optional): Символ открывающей скобки. По умолчанию '{'.
        close_char (str, optional): Символ закрывающей скобки. По умолчанию '}'.
    
    Returns:
        tuple: (позиция закрывающей скобки, уровень вложенности)
    """
    brace_level = 1
    pos = start_pos
    
    while pos < len(text):
        if text[pos] == open_char:
            brace_level += 1
        elif text[pos] == close_char:
            brace_level -= 1
            if brace_level == 0:
                return pos, brace_level
        pos += 1
    
    return -1, brace_level