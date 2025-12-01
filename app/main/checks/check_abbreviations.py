import re
from pymorphy2 import MorphAnalyzer
morph = MorphAnalyzer()


def get_unexplained_abbrev(text):
    abbreviations = find_abbreviations(text)
    
    if not abbreviations:
        return False, None
    
    unexplained_abbr = []
    for abbr in abbreviations:
        if not is_abbreviation_explained(abbr, text):
            unexplained_abbr.append(abbr)
    
    return  True, unexplained_abbr
            



def find_abbreviations(text: str):
    pattern = r'\b[А-ЯA-Z]{2,5}\b'
    abbreviations = re.findall(pattern, text)
    
    common_abbr = {
        'СССР', 'РФ', 'США', 'ВКР', 'ИТ', 'ПО', 'ООО', 'ЗАО', 'ОАО', 'HTML', 'CSS', 
        'JS', 'ЛЭТИ', 'МОЕВМ', 'ЭВМ', 'ГОСТ', 'DVD'
         
          'SSD', 'PC', 'HDD',
        'AX', 'BX', 'CX', 'DX', 'SI', 'DI', 'BP', 'SP',
        'AH', 'AL', 'BH', 'BL', 'CH', 'CL', 'DH', 'DL', 
        'CS', 'DS', 'ES', 'SS', 'FS', 'GS',
        'IP', 'EIP', 'RIP',
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
        'MAC', 'IBM', 'ГОСТ'
    }
    filtered_abbr = [abbr for abbr in abbreviations if abbr not in common_abbr and morph.parse(abbr.lower())[0].score != 0]
    
    return list(set(filtered_abbr))


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
    
    first_letter = ""
    for word in words:
        first_letter += word[0].upper()

    if(first_letter == abbr[len(first_letter)]):
        return True
    return False
