import argparse

from .pdf_document_manager import main as pdf_document_main


def parse_args():
    parser = argparse.ArgumentParser(description="File parsers")
    subparsers = parser.add_subparsers(description="Concrete file formats")
    odt_loading_parser = subparsers.add_parser("text_from_pages", help="PDF Document")
    odt_loading_parser.add_argument("--filename", type=str, required=True, help="path to file")
    odt_loading_parser.set_defaults(func=pdf_document_main)
    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
