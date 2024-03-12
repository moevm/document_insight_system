import filetype

def check_file(file, file_extension, allowed_extensions, check_mime=True):
    if not file_extension in allowed_extensions:
        return "not_allowed_extension"

    if check_mime:
        if file_extension == 'md':
            if file.mimetype != 'text/markdown':
                return "mime_type_does_not_match_extension"
        else:
            if file_extension != filetype.guess_extension(file):
                return "mime_type_does_not_match_extension"

    return ""
