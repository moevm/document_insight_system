import argparse
from app.main.mse22.converter_to_docx.converted_parser import main as converter


def parse_args():
    parser = argparse.ArgumentParser(description="File parser")
    subparser = parser.add_subparsers(description="Concrete file extension")
    doc_loading_parser = subparser.add_parser("convert", help="Convert file to docx")
    doc_loading_parser.add_argument("--filename", type=str, required=True, help="path to file")
    doc_loading_parser.set_defaults(func=converter)
    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
