import argparse
from doc_parser import main as doc


def parse_args():
    parser = argparse.ArgumentParser(description="File parser")
    subparser = parser.add_subparsers(description="Concrete file extension")
    doc_loading_parser = subparser.add_parser("doc")
    doc_loading_parser.add_argument("--filename", type=str, required=True, help="path to .doc file")
    doc_loading_parser.set_defaults(func=doc)
    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
