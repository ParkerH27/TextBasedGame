"""Connected component labeling—img to level."""


import logging
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path

from PIL import Image
from rich.logging import RichHandler

log = logging.getLogger("level_make")


def image_to_binary(image_path: Path, location: Path) -> list[list[bool]]:
    """Convert an image to a binary array."""
    # Open the image file
    image = Image.open(image_path)

    # Convert the image to black and white
    image = image.convert("1")

    # Get the pixel data as a list of tuples
    pixel_data: list[int] = list(image.getdata())

    # Get the image size
    width, height = image.size

    # Convert the pixel data to a 2D array of 1s and 0s
    binary_data: list[list[bool]] = []
    for y in range(height):
        row: list[bool] = []
        for x in range(width):
            pixel = pixel_data[y * width + x]
            row.append(pixel == 0)
        binary_data.append(row)

    # Write the binary data to a file
    with location.open("w", encoding="utf-8") as f:
        for row in binary_data:
            for pixel in row:
                f.write("╋" if pixel == 1 else " ")
            f.write("\n")

    # Return the binary data as a 2D array
    return binary_data


def build_parser() -> Namespace:
    """Build up the argument parser."""
    parser = ArgumentParser(description="Convert an image to a level.")

    parser.add_argument(
        "--input",
        "-i",
        help="The image to convert.",
        type=str,
        default="img.jpg",
    )

    parser.add_argument(
        "--output",
        "-o",
        help="The file to write the level to.",
        type=str,
        default="level2.txt",
    )

    return parser.parse_args()


def run() -> None:
    """Run the generator."""
    parser_args: Namespace = build_parser()

    p = Path(os.path.realpath(__file__)).parent

    img = p / parser_args.input
    level_file = p / parser_args.output

    image_to_binary(img, level_file)
    log.info("Finished!")


if __name__ == "__main__":
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
            ),
        ],
    )
    run()
