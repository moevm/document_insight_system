import filetype

def check_file(file, file_extension, allowed_extensions, check_mime=True):
    if not file_extension in allowed_extensions:
        return "not_allowed_extension"
    
    # Проверяем MIME тип (библиотека автоматически умеет переводить MIME в реальное расширение файла).
    if check_mime and file_extension != filetype.guess_extension(file):
        return "mime_type_does_not_match_extension"
    
    return "ok"