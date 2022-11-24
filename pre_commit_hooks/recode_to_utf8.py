# -*- coding: utf-8 -*-

import argparse
import logging
from pathlib import Path
from typing import Optional, Sequence

import bs4
from bs4.dammit import UnicodeDammit


log = logging.getLogger(__name__)
logging.getLogger(bs4.__package__).setLevel(logging.ERROR)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames pre-commit believes are changed.",
    )

    args = parser.parse_args(argv)

    for file in (Path(f) for f in args.filenames):
        if file.is_file():
            data: bytes
            with open(file, "rb") as f:
                data = f.read()
            decoded = UnicodeDammit(data)
            encoding = decoded.original_encoding
            log.debug(
                "file {!r} tried encodings: {} ({})".format(
                    str(file),
                    decoded.tried_encodings,
                    tuple(decoded.detector.encodings),
                )
            )
            if decoded.contains_replacement_characters:
                log.debug(
                    "file {!r} was decoded with replacement characters, "
                    "skipping ...".format(str(file))
                )
                continue
            if encoding in (None, "ascii", "utf-8"):
                continue
            print(
                "file {!r} is encoded as {!r}, saving as UTF-8".format(
                    str(file), encoding
                )
            )
            with open(file, "w", encoding="utf-8", newline="") as f:
                f.write(decoded.unicode_markup)
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
