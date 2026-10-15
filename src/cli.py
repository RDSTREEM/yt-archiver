import argparse

from pathlib import Path

from packer import pack_directory


def handle_pack(args) -> None:
    manifest = pack_directory(
        source=args.path,
        dest=args.dest,
        chunk_size=args.chunk_size,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="the cli version of the main thingi ig idkk"
    )

    commands = parser.add_subparsers(dest="cmds", required=True)

    pack_parser = commands.add_parser("pack", help="Pack a folder into a local archive")

    pack_parser.add_argument("src", help="Source directory")

    pack_parser.add_argument("--dest", default="./archive", help="Output folder")

    pack_parser.add_argument(
        "--chunk-size",
        type=int,
        default=1024 * 1024,
        help="Chunk size in bytes (default: 1 MiB)",
    )

    pack_parser.set_defaults(func=handle_pack)

    args = parser.parse_args()

    try:
        args.func(args)

    except Exception as e:
        parser.exit(1, str(e))


if __name__ == "__main__":
    main()
