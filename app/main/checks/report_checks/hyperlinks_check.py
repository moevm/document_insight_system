import re

from docx.oxml import parse_xml
from docx.oxml.ns import nsmap, qn

from ..base_check import BaseReportCriterion, answer

REL_NS = nsmap['r']
REL_HYPERLINK = f'{REL_NS}/hyperlink'
REL_HEADER = f'{REL_NS}/header'
REL_FOOTER = f'{REL_NS}/footer'
REL_FOOTNOTES = f'{REL_NS}/footnotes'
REL_ENDNOTES = f'{REL_NS}/endnotes'
REL_COMMENTS = f'{REL_NS}/comments'
REL_IMAGE = f'{REL_NS}/image'

MD_LINK_RE = re.compile(r'<a\s[^>]*href=["\']([^"\']+)["\']', re.IGNORECASE)
ACTIVE_MD_SCHEMES = ('http://', 'https://', 'ftp://', 'mailto:')


class ReportHyperlinksCheck(BaseReportCriterion):
    label = "Проверка наличия активных гиперссылок во всей работе"
    _description = (
        "В работе не должно быть активных (внешних) гиперссылок -"
        + " ни в тексте, ни в таблицах, ни в колонтитулах, ни в сносках, ни на изображениях"
    )
    id = 'hyperlinks_check'
    warning = True

    def __init__(self, file_info):
        super().__init__(file_info)
        self._elements_cache = {}

    def check(self):
        try:
            links = self._collect_hyperlinks()
        except AttributeError:
            # загрузчики без docx-документа (например: mdUploader) - проверяем ссылки markdown
            links = self._collect_md_hyperlinks()
        except Exception as e:
            return answer(False, f"Ошибка при проверке гиперссылок: {e}")

        if not links:  # len(links) == 0
            return answer(True, "Проверка на гиперссылки пройдена")
        return answer(False, self._forming_response(links))

    def _collect_hyperlinks(self):
        """Возвращает список найденных активных (внешних) гиперссылок"""
        document = self.file.file
        found = {}

        for place, part, element in self._iter_sources(document):
            for item in self._iter_part_hyperlinks(part, element, place):
                found.setdefault((item['place'], item['url'], item['text']), item)

            for item in self._iter_external_images(part, element, place):
                found.setdefault((item['place'], item['url'], item['text']), item)

        pages = self._pdf_uri_pages()
        for item in found.values():
            item['pages'] = pages.get(item['url'], [])
        return list(found.values())

    def _iter_sources(self, document):
        """Генератор (место, часть пакета, корневой XML-элемент)"""
        yield 'текст', document.part, document.element

        wanted = {
            REL_HEADER: "колонтитул",
            REL_FOOTER: "колонтитул",
            REL_FOOTNOTES: "сноска",
            REL_ENDNOTES: "концевая сноска",
            REL_COMMENTS: "комментарий",
        }

        for rel in document.part.rels.values():
            if rel.is_external or rel.reltype not in wanted:
                continue
            element = self._part_element(rel.target_part)
            if element is not None:
                yield wanted[rel.reltype], rel.target_part, element

    def _part_element(self, part):
        """XML-элемент части: у XmlPart он уже разобран, у прочих частей разбираем blob"""
        if part in self._elements_cache:
            return self._elements_cache[part]
        element = getattr(part, 'element', None)
        if element is None:
            try:
                element = parse_xml(part.blob)
            except Exception:
                element = None
        self._elements_cache[part] = element
        return element

    def _iter_part_hyperlinks(self, part, element, place):
        """Ссылки внутри одной части: текстовые (w:hyperlink) и навешенные на изображения"""
        rels = part.rels
        for hyperlink in element.iter(qn('w:hyperlink')):
            r_id = hyperlink.get(qn('r:id'))
            if not r_id:
                continue  # w:anchor - внутренняя закладка (оглавление, перекрестные ссылки), игнорируем
            url = self._target_url(rels, r_id, REL_HYPERLINK)
            if url is None:
                continue
            text = ''.join(node.text or '' for node in hyperlink.iter(qn('w:t'))).strip()
            yield {'place': self._refine_place(hyperlink, place), 'url': url, 'text': text}

        for click in element.iter(qn('a:hlinkClick')):
            r_id = click.get(qn('r:id'))
            url = self._target_url(rels, r_id, REL_HYPERLINK) if r_id else None
            if url is None:
                continue
            yield {
                'place': f'{self._refine_place(click, place)}: изображение',
                'url': url,
                'text': self._shape_name(click),
            }

    def _iter_external_images(self, part, element, place):
        """Изображения, вставленные ссылкой на внешний файл (a:blip r:link)"""
        rels = part.rels
        for blip in element.iter(qn('a:blip')):
            r_id = blip.get(qn('r:link'))
            url = self._target_url(rels, r_id, REL_IMAGE) if r_id else None
            if url:
                yield {'place': f'{place}: изображение (внешний файл)', 'url': url, 'text': ''}

    @staticmethod
    def _target_url(rels, r_id, reltype):
        rel = rels.get(r_id)
        if rel is None or rel.reltype != reltype or not rel.is_external:
            return None
        return rel.target_ref

    @staticmethod
    def _refine_place(element, default_place):
        """Уточняет место ссылки внутри части: таблица или надпись/фигура"""
        node = element.getparent()
        while node is not None:
            if node.tag == qn('w:tbl'):
                return 'таблица' if default_place == 'текст' else f'{default_place}: таблица'
            if node.tag == qn('w:txbxContent'):
                return 'надпись/фигура' if default_place == 'текст' else f'{default_place}: надпись/фигура'
            node = node.getparent()
        return default_place

    @staticmethod
    def _shape_name(element):
        """Имя или alt-текст фигуры/изображения, на которое навешена ссылка"""
        node = element.getparent()
        while node is not None:
            if node.tag == qn('wp:docPr'):
                return (node.get('name') or node.get('descr') or '').strip()
            node = node.getparent()
        return ''

    def _pdf_uri_pages(self):
        """{url: [номера страниц]} по аннотациям ссылок в PDF-версии"""
        pages = {}
        pdf = getattr(self.file, 'pdf_file', None)
        if pdf is None:
            return pages
        for page_num in range(1, pdf.page_count_all + 1):
            for link in pdf.pages[page_num - 1].get_links():
                uri = link.get('uri')  # заполняется только для внешних URI-ссылок
                if uri:
                    pages.setdefault(uri, []).append(page_num)
        return pages

    def _forming_response(self, links):
        result_str = (
            f'Найдено активных гиперссылок: <b>{len(links)}</b>. В работе не должно быть кликабельных '
            'ссылок - ни в тексте, ни в таблицах, ни в колонтитулах, ни в сносках, ни на изображениях.<br>'
        )
        by_place = {}
        for item in links:
            by_place.setdefault(item['place'], []).append(item)
        for place, items in by_place.items():
            result_str += f'<b>{place.capitalize()} ({len(items)}):</b><ul>'
            result_str += ''.join(f'<li>{self._link_html(item)}</li>' for item in items)
            result_str += '</ul>'
        result_str += (
            'Удалите гиперссылку (контекстное меню - "Удалить гиперссылку"), оставив текст обычным. '
            'Ссылки на источники в списке литературы также должны быть оформлены обычным текстом.'
        )
        return result_str

    def _link_html(self, item):
        text = item['text'] or item['url']
        html = f'<i>{text}</i> &rarr; <span style="word-break: break-all">{item["url"]}</span>'
        if item['pages']:
            html += f' (стр. {self._pages_html(item["pages"])})'
        return html

    def _pages_html(self, pages):
        links = ', '.join(self.format_page_link(pages))
        return links

    def _collect_md_hyperlinks(self):
        """Ссылки в md-отчете: активны только ссылки вида <a href>"""
        found = {}
        for paragraph in getattr(self.file, 'paragraphs', []):
            text = paragraph if isinstance(paragraph, str) else getattr(paragraph, 'paragraph_text', '')
            for url in MD_LINK_RE.findall(text or ''):
                if url.lower().startswith(ACTIVE_MD_SCHEMES):
                    item = {'place': 'текст', 'url': url, 'text': '', 'pages': []}
                    found.setdefault(('текст', url, ''), item)
        return list(found.values())
