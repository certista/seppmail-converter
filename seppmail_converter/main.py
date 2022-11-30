import pathlib

import click
from click_default_group import DefaultGroup

from seppmail_converter.seppmail import Seppmail
from seppmail_converter.server import app


@click.group(cls=DefaultGroup, default="convert", default_if_no_args=True)
def cli():
    pass


@click.command()
@click.argument(
    "input_file",
    type=click.Path(
        exists=True, readable=True, resolve_path=True, path_type=pathlib.Path
    ),
)
@click.option(
    "--output",
    "-o",
    type=click.Path(
        file_okay=True,
        writable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    prompt=True,
    prompt_required=False,
)
@click.option("--username", "-u", prompt=True, envvar="SEPPMAIL_USERNAME")
@click.password_option(
    "--password", "-p", confirmation_prompt=False, envvar="SEPPMAIL_PASSWORD"
)
@click.option(
    "--force",
    "-f",
    help="Skip SEPPMail input file validation",
    type=click.BOOL,
    is_flag=True,
)
@click.option(
    "--delete",
    "-d",
    help="Delete input file after conversion",
    type=click.BOOL,
    is_flag=True,
)
def convert(
    input_file: pathlib.Path,
    output: pathlib.Path,
    username: str,
    password: str,
    force: bool,
    delete: bool,
):
    # Extract key-value pairs from form
    sepp = Seppmail(username, password)
    output = sepp.convert_file(input_file, force, delete, output)
    click.echo(
        f"Decoded {click.format_filename(input_file.absolute())} to {click.format_filename(output.absolute())}"
    )


@click.command()
@click.option("--username", "-u", prompt=True, envvar="SEPPMAIL_USERNAME")
@click.password_option(
    "--password", "-p", confirmation_prompt=False, envvar="SEPPMAIL_PASSWORD"
)
@click.option('--port', '-p', default=3000, type=click.INT)
def serve(username, password, port):
    app.config["SEPPMAIL_USERNAME"] = username
    app.config["SEPPMAIL_PASSWORD"] = password
    app.run(port=port or 3000)


def entry():
    cli.add_command(convert)
    cli.add_command(serve)
    cli()


if __name__ == "__main__":
    entry()
