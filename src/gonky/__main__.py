"""Entry point for `python -m gonky`."""

from gonky.app import GonkyApp


def main() -> None:
    app = GonkyApp()
    app.run()


if __name__ == "__main__":
    main()
