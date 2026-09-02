import argparse
import chunker
import os

parser = argparse.ArgumentParser()

def get_files(path):
    out = []

def pack(args):
    cwd = os.getcwd()
    p = os.path.join(cwd, args.path)
    d = os.path.join(cwd, args.dest)
    files = get_files(p)

def get_args():
# the main parent parser
    parser = argparse.ArgumentParser(
        description="A command line version of the utility to save data in a yt video",
        # usage="%(prog)s [options]"
    )

    command = parser.add_subparsers(dest="cmd", required=True)

    pack_parser = command.add_parser("pack")
    pack_parser.add_argument("path", help="The path that is to be archived")
    pack_parser.add_argument("-dest", help="The path to save the arhive to", default="./archive")
    pack_parser.set_defaults(func = pack)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    get_args()