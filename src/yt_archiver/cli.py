import argparse
from yt_archiver.config import CHUNK_SIZE

from pathlib import Path

from yt_archiver.packer import pack_directory
from yt_archiver.archive_ops import verify_archive, restore_archive
from yt_archiver.workflow import backup_directory, restore_video


def handle_archive(args) -> None:
    manifest = backup_directory(args.src, args.dest)
    total_bytes = sum(file.size for file in manifest.files)
    total_chunks = sum(len(file.chunks) for file in manifest.files)
    print("Video created successfully.")
    print(f"Files: {len(manifest.files)}")
    print(f"Total source bytes: {total_bytes}")
    print(f"Chunk references: {total_chunks}")
    print(f"Archive: {Path(args.dest).resolve()}")


def handle_extract(args) -> None:
    manifest = restore_video(args.src, args.dest)
    total_bytes = sum(file.size for file in manifest.files)
    total_chunks = sum(len(file.chunks) for file in manifest.files)
    print("Video created successfully.")
    print(f"Files: {len(manifest.files)}")
    print(f"Total source bytes: {total_bytes}")
    print(f"Chunk references: {total_chunks}")
    print(f"Archive: {Path(args.dest).resolve()}")


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


def handle_verify(args):
    manifest = verify_archive(Path(args.archive))

    print("Archive verification successful")
    print(f"Files verified: {len(manifest.files)}")


def handle_restore(args):
    manifest = restore_archive(
        Path(args.archive),
        Path(args.dest),
    )
    print("Archived restored sucessfully")
    print(f"Files restored: {len(manifest.files)}")
    print(f"Destination: {Path(args.dest).resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="the cli version of the main thingi ig idkk"
    )

    commands = parser.add_subparsers(dest="cmds", required=True)

    # ? Pack parser
    pack_parser = commands.add_parser("pack", help="Pack a folder into a local archive")
    pack_parser.add_argument("src", help="Source directory")
    pack_parser.add_argument("--dest", default="./archive", help="Output folder")
    pack_parser.add_argument(
        "--chunk-size",
        type=int,
        default=CHUNK_SIZE,
        help="Chunk size in bytes (default: 1 MiB)",
    )
    pack_parser.set_defaults(func=handle_pack)

    # ? Verify Parser
    verify_parser = commands.add_parser(
        "verify", help="Verify an archive and its checksums"
    )
    verify_parser.add_argument("archive")
    verify_parser.set_defaults(func=handle_verify)

    # ? Restore
    restore_parser = commands.add_parser(
        "restore", help="Restores files from a local archive"
    )
    restore_parser.add_argument("archive")
    restore_parser.add_argument("--dest", required=True)
    restore_parser.set_defaults(func=handle_restore)

    # ? Video
    archive_parser = commands.add_parser("archive", help="Gives the final video")
    archive_parser.add_argument("src", help="Source directory")
    archive_parser.add_argument("--dest", default="archive.mkv", help="Output video")
    archive_parser.set_defaults(func=handle_archive)

    # ? Extract
    extract_parser = commands.add_parser("extract", help="Gives the files from a video")
    extract_parser.add_argument("src", help="Source video")
    extract_parser.add_argument("--dest", default="archive/", help="Output folder")
    extract_parser.set_defaults(func=handle_extract)

    args = parser.parse_args()

    try:
        args.func(args)

    except Exception as e:
        parser.exit(1, str(e))


if __name__ == "__main__":
    main()
