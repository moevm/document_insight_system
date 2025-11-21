import re
from ..base_check import BasePresCriterion, answer


class PresAbbreviationsCheck(BasePresCriterion):
    label = "Проверка расшифровки аббревиатур в презентации"
    description = "Все аббревиатуры должны быть расшифрованы при первом использовании"
    id = 'abbreviations_check_pres'

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        try:
            slides_text = self.file.get_text_from_slides()
            
            if not slides_text:
                return answer(False, "Не удалось получить текст презентации")

            full_text = " ".join(slides_text)
            
            abbreviations = self._find_abbreviations(full_text)
            
            if not abbreviations:
                return answer(True, "Аббревиатуры не найдены в презентации")
            
            unexplained_abbr_with_slides = []
            for abbr in abbreviations:
                slides_with_abbr = self._find_abbreviation_slides(abbr, slides_text)

                if not self._is_abbreviation_explained(abbr, full_text):
                    unexplained_abbr_with_slides.append({
                        'abbr': abbr,
                        'slides': slides_with_abbr
                    })
            

            if unexplained_abbr_with_slides:
                result_str = "Найдены нерасшифрованные аббревиатуры:<br>"

                for item in unexplained_abbr_with_slides:
                    slide_links = self.format_page_link(item['slides'])
                    result_str += f"- {item['abbr']} (слайды: {', '.join(slide_links)})<br>"
                    
                result_str += "<br>Каждая аббревиатура должна быть расшифрована при первом использовании в презентации."
                return answer(False, result_str)
            
            else:
                return answer(True, "Все аббревиатуры правильно расшифрованы")
                
        except Exception as e:
            return answer(False, f"Ошибка при проверке аббревиатур: {str(e)}")

    def _find_abbreviation_slides(self, abbr: str, slides_text: list) -> list:
        found_slides = []
        
        for slide_num, slide_text in enumerate(slides_text, 1):
            pattern = rf'\b{re.escape(abbr)}\b'
            if re.search(pattern, slide_text, re.IGNORECASE):
                found_slides.append(slide_num)
        
        return found_slides

    def _find_abbreviations(self, text: str):
        pattern = r'\b[А-ЯA-Z]{2,5}\b'
        abbreviations = re.findall(pattern, text)
        
        common_abbr = {
            'СССР', 'РФ', 'США', 'ВКР', 'ИТ', 'ПО', 'ООО', 'ЗАО', 'ОАО', 'HTML', 'CSS', 
            'JS', 'ЛЭТИ', 'МОЕВМ', 'ЭВМ', 'DVD', 'SSD', 'PC', 'HDD',
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
            'MAC', 'IBM'
        }
        filtered_abbr = [abbr for abbr in abbreviations if abbr not in common_abbr]
        
        return list(set(filtered_abbr))

    def _is_abbreviation_explained(self, abbr: str, text: str) -> bool:
        patterns = [
            rf'{abbr}\s*\([^)]+\)',  # АААА (расшифровка)
            rf'\([^)]+\)\s*{abbr}',  # (расшифровка) АААА
            rf'{abbr}\s*—\s*[^.,;!?]+',  # АААА — расшифровка
            rf'{abbr}\s*-\s*[^.,;!?]+',  # АААА - расшифровка
            rf'[^.,;!?]+\s*—\s*{abbr}',  # расшифровка — АААА  
            rf'[^.,;!?]+\s*-\s*{abbr}'  # расшифровка - АААА 
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        return False