import os
import subprocess
from os.path import dirname, basename, splitext

from utils.latex_project_unarchiver import LatexProjectUnarchiver


def run_process(cmd: str, cwd: str = None):
    return subprocess.run(cmd.split(' '), cwd=cwd)


def run_process_list(cmd_list: list):
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

    elif extension == '.zip' and target_format == 'pdf':
        unarchiver = LatexProjectUnarchiver(filepath)
        if unarchiver.check_project_validity():
            unarchived_dir = unarchiver.save_files_to_folder(outdir)

            main_latex_file = f'{unarchived_dir}/main.tex'
            result_dir = f'{unarchived_dir}/result'

            run_process(f'chmod -R 777 {unarchived_dir}')
            run_process(
                'latexmk -xelatex -shell-escape -synctex=1 -interaction=nonstopmode -file-line-error '
                f'-outdir={result_dir} -aux-directory={result_dir} {main_latex_file}',
                unarchived_dir
            )

            move_and_clean_cmd = [
                f'cp {result_dir}/main.pdf {outdir}/{filename}.pdf',
                f'rm -rf {unarchived_dir}'
            ]
            if run_process_list(move_and_clean_cmd).returncode == 0:
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
