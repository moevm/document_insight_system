import os
import subprocess
from os.path import dirname


def run_process(cmd: str): return subprocess.run(cmd.split(' '))


def convert_to(filepath, target_format='pdf'):
    new_filename, outdir = None, dirname(filepath)
    convert_cmd = {
        'pdf': f"soffice --headless --convert-to pdf --outdir {outdir} {filepath}",
        'docx': f"soffice --headless --convert-to docx --outdir {outdir} {filepath}",
        'pptx': f"soffice --headless --convert-to pptx --outdir {outdir} {filepath}",
    }[target_format]

    if run_process(convert_cmd).returncode == 0:
        # success conversion
        new_filename = "{}.{}".format(filepath.rsplit('.', 1)[0], target_format)

    return new_filename


def open_file(filepath, remove=False):
    file = open(filepath, 'rb')
    if remove: os.remove(filepath)
    return file
