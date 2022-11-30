# SEPPMail Converter

This python tool allows you to convert [SEPPMail](https://www.seppmail.com/) encrypted email files (`html`) to `.eml` files.

## Usage

```
Usage: main.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  convert*
  serve 
```

### Convert

Convert an encrypted email file to a `.eml` file.

```
Usage: main.py convert [OPTIONS] INPUT_FILE

Options:
  -o, --output PATH
  -u, --username TEXT
  -p, --password TEXT
  -f, --force          Skip SEPPMail input file validation
  -d, --delete         Delete input file after conversion
  --help               Show this message and exit.
```

### Serve

Start a web server to convert encrypted email files to `.eml` files via a web interface.


Relevant environment variables:

| Name | Description |
| ---- | ----------- |
| `SEPPMAIL_USERNAME` | Email supplied during login |
| `SEPPMAIL_PASSWORD` | Password supplied during login|

Unless specified, the script will place the output file next to the input file and name it after the original file.
