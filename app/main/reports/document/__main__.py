import argparse

from .document import main as document_main


def parse_args():
    parser = argparse.ArgumentParser(description="File name")
    parser.add_argument("--filename", type=str, required=True, help="path to .docx file")
    parser.add_argument("--type", type=str, required=True, help="LR or FWQ")
    parser.set_defaults(func=document_main)
    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
