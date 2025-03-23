import csv
from docxtpl import DocxTemplate
from jinja2 import Environment, Template, meta
import argparse
import sys
import os.path
from pathlib import Path
from exceptions import TemplateTypeNotSupported, OutputNameTemplateSyntax
from custom_odt_renderer import CustomOdtRenderer
import re
# defining global variables
contexts = []
fieldnames = []


# Load data from csv file
def load_csv(csv_path, delimiter):
    global contexts
    global fieldnames
    # open csv file and prepare context array
    if not os.path.isfile(csv_path):
        raise FileNotFoundError("File {} not found".format(csv_path))
    with open(csv_path, encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        fieldnames = reader.fieldnames
        for row in reader:
            context = {}
            for key, value in row.items():
                context[key] = value
            contexts.append(context)

                        
# Looking for missing variables/fields used in csv file and template and print summary
def verify_template_odt(template_path):
    if not os.path.isfile(template_path):
        raise FileNotFoundError("File {} not found".format(template_path))
    counter = 0
    test_string = "a"
    print("Verifying template...")
    renderer = CustomOdtRenderer()
    template = open(template_path, 'rb')
    no_params = renderer.render_content_to_xml(template)
    # check if each of the fields in csv file exist in template
    # print("Checking fields in csv")
    for field in fieldnames:
        # print("\tChecking '"+field + "'...")
        w_param = renderer.render_content_to_xml(template, **{field: test_string})
        if w_param == no_params:
            print("\t'{}' not defined in the template".format(field))
            counter+=1
        # else:
        #     print("\t\tOK")
    # check if any field(s) used in the template is not defined in the csv
    # print("Checking variables in template")
    parse_content = Environment().parse(renderer.content_original)
    undeclared_template_variables = meta.find_undeclared_variables(parse_content)
    for variable in undeclared_template_variables:
        # print("\tChecking '"+variable + "'...")
        if variable not in fieldnames:
            print("\t'{}' not defined in the csv".format(variable))
            counter+=1
        # else:
        #     print("\t\tOK")
    return counter

# render the output files
def render_output_odt(template_path, output_name_template,output_dir):
    if not os.path.isfile(template_path):
        raise FileNotFoundError("File {} not found".format(template_path))
    for cont in contexts:
        renderer = CustomOdtRenderer()
        output = open((output_dir if output_dir is not None else '.' )+'/'+re.sub(r'[\\/:*?\"<>|]','',Template(output_name_template).render(cont)) + ".odt", 'wb');
        result = renderer.render(template_path, **cont)
        output.write(result)


# Looking for missing variables/fields used in csv file and template and print summary
def verify_template_docx(template_path):
    if not os.path.isfile(template_path):
        raise FileNotFoundError("File {} not found".format(template_path))
    counter = 0
    test_string = "a"
    print("Verifying template...")
    doc = DocxTemplate(template_path)
    doc.render({})
    no_params = doc.get_xml()
    # check if each of the fields in csv file exist in template
    # print("Checking fields in csv")
    for field in fieldnames:
        doc = DocxTemplate(template_path)
        # print("\tChecking '"+field + "'...")
        doc.render({field: test_string})
        if doc.get_xml() == no_params:
            print("\t'{}' not defined in the template".format(field))
            counter+=1
        # else:
        #     print("\t\tOK")
    # check if any field(s) used in the template is not defined in the csv
    # print("Checking variables in template")
    doc = DocxTemplate(template_path)
    for variable in doc.get_undeclared_template_variables():
        # print("\tChecking '"+variable + "'...")
        if variable not in fieldnames:
            print("\t'{}' not defined in the csv".format(variable))
            counter+=1
        # else:
        #     print("\t\tOK")
    return counter

# render the output files
def render_output_docx(template_path, output_name_template,output_dir):
    if not os.path.isfile(template_path):
        raise FileNotFoundError("File {} not found".format(template_path))
    for cont in contexts:
        doc = DocxTemplate(template_path)
        doc.render(cont)
        doc.save((output_dir if output_dir is not None else '.' )+'/'+re.sub(r'[\\/:*?\"<>|]','',Template(output_name_template).render(cont)) + ".docx")


def verify(template_path):
    if template_path.lower().endswith('.docx'):
        if verify_template_docx(template_path)==0:
            print("\tOK")
    elif template_path.lower().endswith('.odt'):
        if verify_template_odt(template_path)==0:
            print("\tOK")
    else:
        raise TemplateTypeNotSupported


def process(template_path, output_name_template, output_dir):

    if output_dir is not None:
        print('Creating output folder...')
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        print("\tOK")
    if template_path.lower().endswith('.docx'):
        print('Rendering files...')
        render_output_docx(template_path, 
                        (output_name_template if output_name_template is not None else '{{ ' + fieldnames[0] + ' }}'),
                        output_dir)
        print("\tOK")
    elif template_path.lower().endswith('.odt'):
        print('Rendering files...')
        render_output_odt(template_path, 
                        (output_name_template if output_name_template is not None else '{{ ' + fieldnames[0] + ' }}'),
                        output_dir)
        print("\tOK")
    else:
        raise TemplateTypeNotSupported


def main():
    # processing parameter list
    parser = argparse.ArgumentParser(description="A tool that will automatically fill out document templates \
    (docx, odt) with data from the table (each column is a separate insertable field, each line is a new document).")
    parser.add_argument('csv_path',
                        help='The path to the csv file containing the data table')
    parser.add_argument('template_path',
                        help='The path to the template file (odt, docx)')
    parser.add_argument('--out-dir', '-D', dest='output_dir',
                        help="Path to output directory")
    parser.add_argument('--out-name', '-o', dest='output_name',
                        help="Template for the output file names (default = first column's header in csv)")
    parser.add_argument('--delimiter', '-d', dest='delimiter', default=',',
                        help="Delimiter used in the csv file (default = ',')")
    parser.add_argument('--verify-only', '-v', dest='is_verify_only', action='store_true',
                        help="Verify the template against the csv without creating the result files")
    if len(sys.argv) == 1:
        parser.print_help()
        # parser.print_usage() # for just the usage line
        exit()
    args = parser.parse_args()
    # print(args)

    try:
        if args.output_name is not None:
            try:
                Template(args.output_name)
            except Exception:
                raise OutputNameTemplateSyntax

        load_csv(args.csv_path, args.delimiter)

        verify(args.template_path)
        if not args.is_verify_only:
            process(args.template_path, args.output_name, args.output_dir)
    except TemplateTypeNotSupported:
        print("This template type is not supported")
    except FileNotFoundError as e:
        print(e)
    except OutputNameTemplateSyntax:
        print("Output file name is invalid")


if __name__ == '__main__':
    main()