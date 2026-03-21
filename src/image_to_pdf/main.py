import argparse

from .app import ImageToPDFApp


def main():
    parser = argparse.ArgumentParser(description="Convert images to PDF")
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=75,
        help="PDF quality (1-100, default: 75)",
    )
    parser.add_argument(
        "-o",
        "--optimize",
        action="store_true",
        help="Optimize PDF file size",
    )
    args = parser.parse_args()

    app = ImageToPDFApp(quality=args.quality, optimize=args.optimize)
    app.run()


if __name__ == "__main__":
    main()
