from ..base_check import BaseCheck, answer

class ReportNumberOfPages(BaseCheck):
    def __init__(self, file, minNumber = 0, maxNumber = None):
        super().__init__(file)
        self.minNumber = minNumber
        self.maxNumber = maxNumber

    def check(self):
        print(type(self.file.paragraphs[0]))
        count = 0
        for k, v in self.file.pdf_file.text_on_page.items():
            print(f"Страница №{k}", end='\n\n')
            if "приложение" in v.lower():
                break
            count += 1

        if count >= self.minNumber and (self.maxNumber is None or count <= self.maxNumber):
            return answer(True, f"Пройдена! {count} страниц")
        return answer(False, f'Неверное кол-во страниц в файле. ({count} страниц)')


