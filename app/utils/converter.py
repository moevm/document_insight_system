import subprocess
import tempfile
import os

def run_process(cmd: str): return subprocess.run(cmd.split(' '))

def convert_to(file, target_format='pdf'):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(file.read())
    temp_file.close()
    file.seek(0)
    new_filename = None

    convert_cmd = {
        'pdf': "soffice --headless --convert-to pdf --outdir /tmp {}".format(temp_file.name),
        'docx': "soffice --headless --convert-to docx --outdir /tmp {}".format(temp_file.name)
    }[target_format]

    if run_process(convert_cmd).returncode == 0:
        # success conversion
        new_filename = "{}.pdf".format(temp_file.name)
    os.remove(temp_file.name)

    return new_filename
