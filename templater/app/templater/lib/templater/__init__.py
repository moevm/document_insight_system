import csv
import xlrd
from docxtpl import DocxTemplate, RichText
from jinja2 import Environment, Template, meta
from .custom_exceptions import TemplateTypeNotSupported, OutputNameTemplateSyntax
from .custom_odt_renderer import CustomOdtRenderer
from .openoffice_renderer import OpenOfficeRenderer
from .pptx_renderer import PptxRenderer
from .xlsx_renderer import XlsxRenderer
import re
import io
import zipfile
# defining global variables

class RenderResult(object):
    def __init__(self):
        self.files = {}
        self.archive = None


class TemplateRenderer(object):

    MULTILINE_PREFIX = "&^<\\multiline>"

    def __init__(self):
        self.contexts = []
        self.fieldnames = []
        self.raw_table = []

    def _preprocess_value(self, value):
        if value.startswith(self.MULTILINE_PREFIX):
            value = RichText(value[len(self.MULTILINE_PREFIX):])
        return value

    # Load data from csv file
    def load_csv(self, csvfile, delimiter):
        # open csv file and prepare context array
        lines = csvfile.read().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(lines), delimiter=delimiter)
        self.fieldnames = reader.fieldnames
        self.raw_table.append(self.fieldnames)
        for row in reader:
            context = {}
            r = []
            for key, value in row.items():
                value = value.lstrip('\"').rstrip('\"')
                context[key] = self._preprocess_value(value)
                r.append(value)
            self.contexts.append(context)
            self.raw_table.append(r)

    def load_excel(self, excelfile):
        wb = xlrd.open_workbook(file_contents = excelfile.read()) 
        sh = wb.sheet_by_index(0)
        for col in range(sh.ncols):
            self.fieldnames.append(sh.cell_value(rowx=0, colx=col))
        self.raw_table.append(self.fieldnames)
        for row in range(1, sh.nrows):
            context = {}
            r = []
            for col in range(sh.ncols):
                value = str(sh.cell_value(rowx=row, colx=col))
                context[self.fieldnames[col]] = self._preprocess_value(value)
                r.append(value)
            self.contexts.append(context)
            self.raw_table.append(r)

    def load_data(self, datafile):
        if datafile.name.lower().endswith('.csv'):
            self.load_csv(datafile, ',')
        elif datafile.name.lower().endswith('.xls') or datafile.name.lower().endswith('.xlsx'):
            self.load_excel(datafile)
        else:
            raise TemplateTypeNotSupported

    # Looking for missing variables/fields used in csv file and template and print summary
    def verify_template_odt(self, template, renderer = CustomOdtRenderer()):
        # messages = []
        result = { 'in_template': [], 'in_csv' : []}
        test_string = "a"
        no_params = renderer.render_content_to_xml(template)
        # check if each of the fields in csv file exist in template
        for field in self.fieldnames:
            w_param = renderer.render_content_to_xml(template, **{field: test_string})
            if w_param == no_params:
                # messages.append("'{}' not defined in the template".format(field))
                result['in_template'].append(field)
        # check if any field(s) used in the template is not defined in the csv
        parse_content = Environment().parse(renderer.content_original)
        undeclared_template_variables = meta.find_undeclared_variables(parse_content)
        for variable in undeclared_template_variables:
            if variable not in self.fieldnames:
                # messages.append("'{}' not defined in the csv".format(variable))
                result['in_csv'].append(variable)
        return result

    # render the output files
    def render_output_odt(self, template, output_name_template, renderer = CustomOdtRenderer(), extension = '.odt'):
        r_result = RenderResult()
        for cont in self.contexts:
            # renderer = CustomOdtRenderer()
            output = io.BytesIO()
            doc = renderer.render(template, **cont)
            output.write(doc)
            r_result.files[re.sub(r'[\\/:*?\"<>|]','',Template(output_name_template).render(cont)) + extension] = output
        return r_result


    # Looking for missing variables/fields used in csv file and template and print summary
    def verify_template_docx(self, template):
        # messages = []
        result = { 'in_template': [], 'in_csv' : []}
        test_string = "a"
        doc = DocxTemplate(template)
        doc.render({})
        no_params = doc.get_xml()
        # check if each of the fields in csv file exist in template
        for field in self.fieldnames:
            doc = DocxTemplate(template)
            doc.render({field: test_string})
            if doc.get_xml() == no_params:
                # messages.append("'{}' not defined in the template".format(field))
                result['in_template'].append(field)
        # check if any field(s) used in the template is not defined in the csv
        doc = DocxTemplate(template)
        for variable in doc.get_undeclared_template_variables():
            if variable not in self.fieldnames:
                # messages.append("'{}' not defined in the csv".format(variable))
                result['in_csv'].append(variable)
        # return messages
        return result

    # render the output files
    def render_output_docx(self, template, output_name_template):
        r_result = RenderResult()
        for cont in self.contexts:
            output = io.BytesIO()
            doc = DocxTemplate(template)
            doc.render(cont)
            doc.save(output)
            r_result.files[re.sub(r'[\\/:*?\"<>|]','',Template(output_name_template).render(cont)) + ".docx"] = output
        return r_result


    def verify(self, template):
        if template.name.lower().endswith('.docx'):
            return self.verify_template_docx(template)
        elif template.name.lower().endswith('.odt'):
            return self.verify_template_odt(template)
        elif template.name.lower().endswith('.odp') or template.name.lower().endswith('.ods'):
            return self.verify_template_odt(template,OpenOfficeRenderer())
        elif template.name.lower().endswith('.pptx'):
            return self.verify_template_odt(template,PptxRenderer())
        elif template.name.lower().endswith('.xlsx'):
            return self.verify_template_odt(template,XlsxRenderer())
        else:
            raise TemplateTypeNotSupported

    
    def createArchive(self, result):
        archive = io.BytesIO()
        zf = zipfile.ZipFile(archive,mode='w',compression=zipfile.ZIP_DEFLATED)

        for filename in result.files:
            zf.writestr(filename, result.files[filename].getvalue())
        
        result.archive = archive

    def render(self, template, output_name_template):
        result = RenderResult()
        outname = (output_name_template if output_name_template is not None else '{{ ' + self.fieldnames[0] + ' }}')
        if template.name.lower().endswith('.docx'):
            result = self.render_output_docx(template, outname)
        elif template.name.lower().endswith('.odt'):
            result = self.render_output_odt(template, outname)
        elif template.name.lower().endswith('.odp'):
            result = self.render_output_odt(template, outname, OpenOfficeRenderer(), '.odp')
        elif template.name.lower().endswith('.ods'):
            result = self.render_output_odt(template, outname, OpenOfficeRenderer(), '.ods')
        elif template.name.lower().endswith('.pptx'):
            result = self.render_output_odt(template, outname, PptxRenderer(), '.pptx')
        elif template.name.lower().endswith('.xlsx'):
            result = self.render_output_odt(template, outname, XlsxRenderer(), '.xlsx')
        else:
            raise TemplateTypeNotSupported
        self.createArchive(result)
        return result

