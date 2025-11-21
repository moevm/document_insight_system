import re
from ..base_check import BaseReportCriterion, answer


class AbbreviationsCheck(BaseReportCriterion):
    label = "Проверка расшифровки аббревиатур"
    description = "Все аббревиатуры должны быть расшифрованы при первом использовании"
    id = 'abbreviations_check'

    def __init__(self, file_info):
        super().__init__(file_info)


    def check(self):
        try:
            text = self._get_document_text()
            
            if not text:
                return answer(False, "Не удалось получить текст документа")

            abbreviations = self._find_abbreviations(text)
            
            if not abbreviations:
                return answer(True, "Аббревиатуры не найдены в документе")
            
            unexplained_abbr = []
            for abbr in abbreviations:
                if not self._is_abbreviation_explained(abbr, text):
                    unexplained_abbr.append(abbr)
            
            if unexplained_abbr:
                result_str = f"Найдены нерасшифрованные аббревиатуры: {', '.join(unexplained_abbr)}<br>"
                result_str += "Каждая аббревиатура должна быть расшифрована при первом использовании в тексте."
                return answer(False, result_str)
            else:
                return answer(True, "Все аббревиатуры правильно расшифрованы")
                
        except Exception as e:
            return answer(False, f"Ошибка при проверке аббревиатур: {str(e)}")


    def _get_document_text(self):

        if hasattr(self.file, 'pdf_file'):
            page_texts = self.file.pdf_file.get_text_on_page()
            return " ".join(page_texts.values())
        elif hasattr(self.file, 'paragraphs'):
            text_parts = []
            for paragraph in self.file.paragraphs:
                text = paragraph.to_string()
                if '\n' in text:
                    text = text.split('\n')[1]
                text_parts.append(text)
            return "\n".join(text_parts)
        return None

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
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
