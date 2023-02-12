import sys
import os
import logging
import argparse
import zipfile
from typing import IO
import img2pdf


class ZipImageFileProxy:
    @staticmethod
    def is_image_file(path: str) -> bool:
        if path.endswith("/"):
            # Directory
            return False
        return path.lower().endswith((".png", ".jpg", ".jpeg"))

    def __init__(self, src_zip: zipfile.ZipFile, path: str) -> None:
        if not ZipImageFileProxy.is_image_file(path):
            raise Exception(f"{path} is not an image file.")
        self.src_zip: zipfile.ZipFile = src_zip
        self.path: str = path

    def read(self):
        logging.info(f"Reading {self.path}")
        return self.src_zip.open(self.path).read()


def zip2pdf(zip_path: str, outstream: IO):
    with zipfile.ZipFile(zip_path) as src_zip:
        zipFileProxyList = []
        for img in sorted(src_zip.namelist()):
            try:
                zipFileProxyList.append(ZipImageFileProxy(src_zip, img))
            except Exception as e:
                logging.warning(f"Skipping {img} ({e})")
        outstream.write(img2pdf.convert(zipFileProxyList))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_path", metavar="zip_path", type=zip_file)
    parser.add_argument(
        "-o",
        "--output",
        metavar="out",
        type=argparse.FileType("wb"),
        default=sys.stdout.buffer,
    )
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    zip2pdf(args.zip_path, args.output)


def zip_file(path: str):
    if os.path.isfile(path) and zipfile.is_zipfile(path):
        return path
    raise argparse.ArgumentTypeError(f"{path} is not a valid zip file.")


if __name__ == "__main__":
    main()
