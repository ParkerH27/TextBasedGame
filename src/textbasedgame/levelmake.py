"""Connected component labeling—img to level."""
from PIL import Image


def image_to_binary(image_path, location):
    # Open the image file
    image = Image.open(image_path)

    # Convert the image to black and white
    image = image.convert("1")

    # Get the pixel data as a list of tuples
    pixel_data = list(image.getdata())

    # Get the image size
    width, height = image.size

    # Convert the pixel data to a 2D array of 1s and 0s
    binary_data = []
    for y in range(height):
        row = []
        for x in range(width):
            pixel = pixel_data[y * width + x]
            row.append(int(pixel == 0))
        binary_data.append(row)

    # Write the binary data to a file
    with open(location, "w", encoding="utf-8") as f:
        for row in binary_data:
            for pixel in row:
                f.write("┃" if pixel == 1 else ".")
            f.write("\n")

    # Return the binary data as a 2D array
    return binary_data


image_to_binary("img.jpg", "level2.txt")
print("Finished!")
