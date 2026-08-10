"""EchoType - Python entry point.

Usage:
    python main.py
    python main.py --text "custom practice sentence"
    python main.py --file words.txt --rate 190 --no-flash
"""

import argparse
import sys
from pathlib import Path

from src import constants as C
from src.session import split_words


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="echotype",
        description="Vocalized typing practice: listen to a word, type it, press SPACE.",
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--text", help="practice text to dictate")
    source.add_argument("--file", type=Path, help="read practice text from a file")
    parser.add_argument("--rate", type=int, default=C.SPEECH["DEFAULT_RATE"],
                        help="speech rate in words per minute (default: %(default)s)")
    parser.add_argument("--no-flash", action="store_true",
                        help="start with the on-screen word flash disabled")
    parser.add_argument("--speech-backend", choices=["pyttsx3", "say"],
                        help="force a text-to-speech backend instead of auto-detecting")
    return parser.parse_args(argv)


def resolve_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.file:
        if not args.file.is_file():
            raise SystemExit(f"error: no such file: {args.file}")
        text = args.file.read_text(encoding="utf-8")
        if not split_words(text):
            raise SystemExit(f"error: {args.file} contains no words")
        return text
    return C.DEFAULT_PARAGRAPH


def main(argv=None) -> int:
    args = parse_args(argv)
    text = resolve_text(args)

    try:
        from src.echotype_window import run
    except ImportError as exc:
        print(f"error: missing dependency ({exc}).", file=sys.stderr)
        print("install with: pip install -r requirements.txt", file=sys.stderr)
        return 1

    run(
        paragraph=text,
        rate=args.rate,
        flash=not args.no_flash,
        speech_backend=args.speech_backend,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
