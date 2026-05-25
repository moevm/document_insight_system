def make_file_info(path_str):
    if path_str.endswith(('.pptx', '.ppt')):
        from app.main.presentations.pptx.presentation_pptx import PresentationPPTX
        file_obj = PresentationPPTX(path_str)
    elif path_str.lower().endswith('.odp'):
        from app.main.presentations.odp.presentation_odp import PresentationODP
        file_obj = PresentationODP(path_str)
    else:
        from app.main.presentations.presentation_basic import PresentationBasic
        file_obj = PresentationBasic(path_str)
    return {'file': file_obj, 'filename': path_str, 'pdf_id': None, 'file_type': None}


def verdict_str(result):
    return ' '.join(str(v) for v in result['verdict'])