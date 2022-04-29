import subprocess


class Converter:
    def __init__(self, path_to_file, out_dir='app/main/mse22/converted_files/'):
        self._file = path_to_file
        self._out_dir = out_dir
        self._filename = path_to_file.split('/')[-1].split('.')[0]

    def convert(self):
        subprocess.call(['soffice', '--headless', '--convert-to', 'docx', '--outdir', self._out_dir, self._file])
        return self._out_dir + self._filename + '.docx'

    def convert_to_pdf(self):
        subprocess.call(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', self._out_dir, self._file])
        return self._out_dir + self._filename + '.pdf'
