import argparse

from pathlib import Path

from packer import pack_directory


def handle_pack(args) -> None:
    manifest = pack_directory(
        source=args.src,
        dest=args.dest,
        chunk_size=args.chunk_size,
    )

    total_bytes = sum(file.size for file in manifest.files)
    total_chunks = sum(len(file.chunks) for file in manifest.files)
    print("Archive created successfully.")
    print(f"Files: {len(manifest.files)}")
    print(f"Total source bytes: {total_bytes}")
    print(f"Chunk references: {total_chunks}")
    print(f"Archive: {Path(args.dest).resolve()}")


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
