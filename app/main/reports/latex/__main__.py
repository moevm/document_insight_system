import argparse

# from .docx_uploader import main as docx_uploader_main
from .latex_uploader import main as latex_uploader_main  # Импортируем LaTeX парсер

def parse_args():
    parser = argparse.ArgumentParser(description='File Uploaders')
    subparsers = parser.add_subparsers()
    
    # docx_parser = subparsers.add_parser('docx_parser', help='Upload file [docx_uploader]')
    # docx_parser.add_argument('--file', type=str, required=True, help='path to docx_uploader file')
    # docx_parser.set_defaults(func=docx_uploader_main)
    
    # Добавляем парсер для LaTeX
    latex_parser = subparsers.add_parser('latex_parser', help='Upload file [latex_uploader]')
    latex_parser.add_argument('--file', type=str, required=True, help='path to latex file')
    latex_parser.set_defaults(func=latex_uploader_main)
    
    return parser.parse_args()

def main():
    args = parse_args()
    args.func(args)

if __name__ == '__main__':
    main()