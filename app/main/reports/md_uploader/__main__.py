import argparse

from .md_uploader import main as md_uploader_main


def parse_args():
    parser = argparse.ArgumentParser(description='File md parser')
    subparsers = parser.add_subparsers()
    md_parser = subparsers.add_parser('md_parser', help='md document')
    md_parser.add_argument('--mdfile', type=str, required=True, help='path to md file')
    md_parser.set_defaults(func=md_uploader_main)
    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()