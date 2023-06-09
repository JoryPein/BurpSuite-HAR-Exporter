import typer
import pathlib
from .functions import *


app = typer.Typer()

@app.command()
def main(filename: pathlib.Path):

    if not filename.exists():
        print(f"Filename not found: {filename}")
        typer.Exit(1)

    output_filename = filename.parent / (filename.stem + ".har")
    bpi2har_run(filename, output_filename)
