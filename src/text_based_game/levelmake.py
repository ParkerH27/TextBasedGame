"""Connected component labeling—img to level."""

import logging
import os
import pathlib
from argparse import ArgumentParser, Namespace

import trio
from PIL import Image
from rich import traceback
from rich.logging import RichHandler

log = logging.getLogger("level_make")


async def image_to_binary(
    image_path: pathlib.Path,
    location: trio.Path,
) -> list[list[bool]]:
    """Convert an image to a binary array."""
    log.info("Opening image...")
    image = await trio.to_thread.run_sync(Image.open, image_path)

    log.info("Converting image to black and white...")
    image = await trio.to_thread.run_sync(image.convert, "1")

    # Get the pixel data as a list of tuples
    pixel_data: list[int] = list(image.getdata())

    # Get the image size
    width, height = image.size

    # Convert the pixel data to a 2D array of 1s and 0s
    binary_data: list[list[bool]] = []
    log.info("Converting image to binary...")
    for y in range(height):
        row: list[bool] = []
        for x in range(width):
            pixel = pixel_data[y * width + x]
            row.append(pixel == 0)
        binary_data.append(row)

    log.info("Writing to file...")
    async with await location.open("w", encoding="utf-8") as f:
        for row in binary_data:
            for pixel in row:
                await f.write("╋" if pixel == 1 else " ")
            await f.write("\n")

    log.info("Finished!")

    return binary_data  # Return the binary data as a 2D array


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


async def run_generator() -> None:
    """Run the generator."""
    parser_args: Namespace = build_parser()

    p = pathlib.Path(os.path.realpath(__file__)).parent

    img: pathlib.Path = p / parser_args.input
    level_file: pathlib.Path = p / parser_args.output

    await image_to_binary(img, trio.Path(level_file))


def main() -> None:
    """Run the generator."""
    trio.run(run_generator, strict_exception_groups=True)


if __name__ == "__main__":
    traceback.install(suppress=[trio])
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
    main()
