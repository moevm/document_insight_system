import subprocess
import tempfile
import os

def run_process(cmd: str): return subprocess.run(cmd.split(' '))

def convert_to_pdf(presentation_file):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(presentation_file.read())
    temp_file.close()
    presentation_file.seek(0)

    cmd_timeout = 20
    converted_file = None
    convert_cmd = "unoconv --timeout {} -f pdf {}".format(cmd_timeout, temp_file.name)
    if run_process(convert_cmd).returncode == 0:
        # success conversion
        new_filename = "{}.pdf".format(temp_file.name)
        converted_file = open(new_filename, 'rb')
        os.remove(new_filename)

    os.remove(temp_file.name)
    return converted_file
