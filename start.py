import argparse
from pcmain import main as pc
from rpimain import main as rpi

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rpi", help="starts rpimain.py script")
    parser.add_argument("--pc", help="starts pcmain.py script")
    args = parser.parse_args()
    if args.rpi:
        rpi()
    if args.pc:
        pc()

