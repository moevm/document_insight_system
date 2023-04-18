import os


def get_file_len(file):
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0, 0)
    return file_length
