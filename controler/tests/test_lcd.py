
import random
import lib.tft_config as tft_config
import lib.st7789py as st7789


def main():
    """ main """
    print("Starting...")
    tft = tft_config.config(tft_config.WIDE)

    while True:
        print("loop...")
        color = st7789.color565(
            random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)
        )

        print("draw line")
        tft.line(
            random.randint(0, tft.width),
            random.randint(0, tft.height),
            random.randint(0, tft.width),
            random.randint(0, tft.height),
            color,
        )

        print("draw rect")
        width = random.randint(0, tft.width // 2)
        height = random.randint(0, tft.height // 2)
        col = random.randint(0, tft.width - width)
        row = random.randint(0, tft.height - height)
        tft.fill_rect(
            col,
            row,
            width,
            height,
            st7789.color565(
                random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)
            ),
        )


main()