import re
from pymorphy3 import MorphAnalyzer
morph = MorphAnalyzer()


def get_unexplained_abbrev(text, title_page):
    abbreviations = find_abbreviations(text, title_page)
    
    if not abbreviations:
        return False, []
    
    unexplained_abbr = []
    for abbr in abbreviations:
        if not is_abbreviation_explained(abbr, text):
            unexplained_abbr.append(abbr)
    
    return  True, unexplained_abbr
            
def find_abbreviations(text: str, title_page: str):
    pattern = r'\b[А-ЯA-Z]{2,5}\b'
    abbreviations = re.findall(pattern, text)
    
    common_abbr = {
        'СССР', 'РФ', 'США', 'ВКР', 'ИТ', 'ПО', 'ООО', 'ЗАО', 'ОАО', 'HTML', 'CSS', 
        'JS', 'ЛЭТИ', 'МОЕВМ', 'ЭВМ', 'ГОСТ', 'DVD'
         
          'SSD', 'PC', 'HDD',
        'AX', 'BX', 'CX', 'DX', 'SI', 'DI', 'BP', 'SP',
        'AH', 'AL', 'BH', 'BL', 'CH', 'CL', 'DH', 'DL', 
        'CS', 'DS', 'ES', 'SS', 'FS', 'GS',
        'IP', 'EIP', 'RIP', 'URL',
        'CF', 'PF', 'AF', 'ZF', 'SF', 'TF', 'IF', 'DF', 'OF',
        'EAX', 'EBX', 'ECX', 'EDX', 'ESI', 'EDI', 'EBP', 'ESP',
        'RAX', 'RBX', 'RCX', 'RDX', 'RSI', 'RDI', 'RBP', 'RSP',
        'DOS', 'OS', 'BIOS', 'UEFI', 'MBR', 'GPT',
        'ASCII', 'UTF', 'UNICODE', 'ANSI',
        'ЭВМ', 'МОЭВМ',
        'CPU', 'GPU', 'APU', 'RAM', 'ROM', 'PROM', 'EPROM', 'EEPROM',
        'USB', 'SATA', 'PCI', 'PCIe', 'AGP', 'ISA', 'VGA', 'HDMI', 'DP',
        'LAN', 'WAN', 'WLAN', 'VPN', 'ISP', 'DNS', 'DHCP', 'TCP', 'UDP', 'IP',
        'HTTP', 'HTTPS', 'FTP', 'SSH', 'SSL', 'TLS',
        'API', 'GUI', 'CLI', 'IDE', 'SDK', 'SQL', 'NoSQL', 'XML', 'JSON', 'YAML',
        'MAC', 'IBM', 'ГОСТ', 'ООП', 'ЛР', 'КР', 'ОТЧЕТ'
    }
    filtered_abbr = {abbr for abbr in abbreviations if abbr not in common_abbr \
                     and abbr not in title_page and morph.parse(abbr.lower())[0].score != 0}
    
    return list(filtered_abbr)

def is_abbreviation_explained(abbr: str, text: str) -> bool:
    patterns = [
        rf'{abbr}\s*\(([^)]+)\)',         # АААА (расшифровка)
        rf'\(([^)]+)\)\s*{abbr}',         # (расшифровка) АААА
        rf'{abbr}\s*[—\-]\s*([^.,;!?]+)', # АААА — расшифровка
        rf'{abbr}\s*-\s*([^.,;!?]+)',     # АААА - расшифровка
        rf'([^.,;!?]+)\s*[—\-]\s*{abbr}', # расшифровка — АААА  
        rf'([^.,;!?]+)\s*-\s*{abbr}'      # расшифровка - АААА 
    ]

    
    for pattern in patterns:
        match =  re.search(pattern, text, re.IGNORECASE)
        if match and correctly_explained(abbr, match.group(1)):
            return True
    
    return False

def correctly_explained(abbr, explan):
    words = explan.split()
    
    first_letters = ""
    for word in words:
        if word:
            first_letters += word[0].upper()

    return first_letters == abbr.upper()

def main_check(text: str, title_page: str):
    try:
        continue_check = True
        res_str = ""
        if not text:
            continue_check, res_str = False, "Не удалось получить текст"
        
        abbr_is_finding, unexplained_abbr = get_unexplained_abbrev(text=text, title_page=title_page)
        
        if not abbr_is_finding:
            continue_check, res_str = False, "Аббревиатуры не найдены в представленном документе"
        
        if not unexplained_abbr:
            continue_check, res_str = False, "Все аббревиатуры правильно расшифрованы"

        return continue_check, res_str, unexplained_abbr
    
    except Exception as e:
        return False, f"Ошибка при проверке аббревиатур: {str(e)}", {}
    
def forming_response(unexplained_abbr_with_page, format_page_link):
    result_str = "Найдены нерасшифрованные аббревиатуры при первом использовании:<br>"      
    page_links = format_page_link(list(unexplained_abbr_with_page.values()))
    for index_links, abbr in enumerate(unexplained_abbr_with_page):
        result_str += f"- {abbr} на {page_links[index_links]} странице/слайде<br>"
    result_str += "Каждая аббревиатура должна быть расшифрована при первом использовании в тексте.<br>"
    result_str += "Расшифровка должны быть по первыми буквам, например, МВД - Министерство внутренних дел.<br>"
    return result_str
