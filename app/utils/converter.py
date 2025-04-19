import os
import subprocess
from os.path import dirname, basename, splitext


def run_process(cmd: str): return subprocess.run(cmd.split(' '))


def run_process_list(cmd_list: str):
    for cmd in cmd_list:
        res = run_process(cmd)
        if res.returncode != 0:
            break
    return res


def convert_to(filepath, target_format='pdf'):
    new_filename, outdir = None, dirname(filepath)
    filename, extension = splitext(basename(filepath))
    if extension == '.tex' and target_format == 'pdf':
        convert_cmd = [
            f"mkdir -p {outdir}/tmp_latex",
            f"pdflatex -output-directory={outdir}/tmp_latex -interaction=nonstopmode {filepath}",
            f"mv {outdir}/tmp_latex/{filename}.pdf {outdir}",
            f"rm -rf {outdir}/tmp_latex"
        ]
        if run_process_list(convert_cmd).returncode == 0:
            # success conversion
            new_filename = "{}/{}.{}".format(outdir, filename, target_format)
    else:
        # if file is latex then convert to pdf -> convert to another ext
        if extension == '.tex':
            filepath = convert_to(filepath, 'pdf')
        convert_cmd = {
            'pdf': f"soffice --headless --convert-to pdf --outdir {outdir} {filepath}",
            'docx': f"soffice --headless --convert-to docx --outdir {outdir} {filepath}",
            'pptx': f"soffice --headless --convert-to pptx --outdir {outdir} {filepath}",
        }[target_format]

        if run_process(convert_cmd).returncode == 0:
            # success conversion
            new_filename = "{}/{}.{}".format(outdir, filename, target_format)

    return new_filename


def open_file(filepath, remove=False):
    file = open(filepath, 'rb')
    if remove: os.remove(filepath)
    return file
