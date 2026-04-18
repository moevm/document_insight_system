import re

from ..nlp.is_passive_was_were_sentence import is_passive_was_were_sentece


class WasWereChecker:
    def __init__(self, file_info, threshold):
        self.file_type = file_info["file_type"]["type"]
        self.threshold = threshold

    def get_content_by_file(self, file):
        if self.file_type == "report":
            return file.pdf_file.get_text_on_page().items()
        elif self.file_type == "pres":
            return enumerate(file.get_text_from_slides())

    def generate_output_text(self, detected_senteces, format_page_link_fn=None):
        output = "Обнаружены конструкции (Был/Была/Было/Были), которые можно удалить без потери смысла:<br><br>"
        offset_index = 0
        if self.file_type == "pres":
            offset_index = 1

        for index, messages in detected_senteces.items():
            display_index = index + offset_index
            if format_page_link_fn:
                output += (
                    f"<b>Страница {format_page_link_fn([display_index])}:</b> <br>" + "<br>".join(messages) + "<br><br>"
                )
            else:
                output += f"<b>Страница №{display_index}:</b> <br>" + "<br>".join(messages) + "<br><br>"
        return output

    def get_was_were_sentences(self, file):
        detected = {}
        total_sentences = 0
        for page_index, page_text in self.get_content_by_file(file):
            lines = re.split(r"\n", page_text)
            non_empty_line_counter = 0
            for line_index, line in enumerate(lines):
                print(line_index, line)
                line = line.strip()
                if not line:
                    continue

                non_empty_line_counter += 1
                sentences = re.split(r"[.!?…]+\s*", line)

                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue

                    if is_passive_was_were_sentece(sentence):
                        total_sentences += 1
                        if page_index not in detected:
                            detected[page_index] = []
                        truncated_sentence = sentence[:50] + "..." if len(sentence) > 50 else sentence
                        if self.file_type == "pres":
                            err_str = f"Строка {non_empty_line_counter}: {truncated_sentence}"
                        elif self.file_type == "report":
                            err_str = f"Строка {line_index + 1}: {truncated_sentence}"
                        detected[page_index].append(err_str)

        return detected, total_sentences

    def get_result_msg_and_score(self, file, format_page_link):
        detected, total_sentences = self.get_was_were_sentences(file)
        result_msg = ""
        result_score = 1
        if total_sentences == 0:
            result_msg = "Пройдена!"
        else:
            result_msg = self.generate_output_text(detected, format_page_link)
            if total_sentences > self.threshold:
                result_msg = "Не пройдена!<br/>" + result_msg
                result_score = 0
            else:
                result_msg = "Пройдена!<br/>" + result_msg
        return result_msg, result_score
