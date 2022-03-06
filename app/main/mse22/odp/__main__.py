import argparse

from app.main.mse22.odp.odp_presentation import main as odt_pres_main


def parse_args():
    parser = argparse.ArgumentParser(description="File parsers")
    subparsers = parser.add_subparsers(description="Concrete file formats")
    odt_loading_parser = subparsers.add_parser("odp")
    odt_loading_parser.add_argument("--filename", type=str, required=True, help="path to .odp file")
    odt_loading_parser.set_defaults(func=odt_pres_main)
    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
