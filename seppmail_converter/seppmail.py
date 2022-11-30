import pathlib
import re

import requests
from bs4 import BeautifulSoup

from seppmail_converter.exceptions import InputError, AuthenticationError, ExportError


class Seppmail:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    @staticmethod
    def _validate(input_file: str):
        if "secmail" not in input_file:
            raise InputError(
                "The input file provided seems to be invalid",
            )
        return True

    @staticmethod
    def _build_value_map(soup: BeautifulSoup, **kwargs):
        return {
            node.attrs.get("name"): node.attrs.get("value")
            for node in soup.find_all("input")
        } | kwargs

    def convert(self, input_file: str, force: bool = False, stream: bool = False):
        if not force:
            self._validate(input_file)
        # Submit the created form to receive session
        soup = BeautifulSoup(input_file, "lxml")
        target_url = soup.find("form").attrs["action"]
        req = requests.post(
            target_url,
            data=self._build_value_map(soup),
        )
        if not req.ok:
            raise InputError(
                "Could not submit or find form details, check input file",
            )
        # Login with given credentials to export mail as .eml
        req = requests.post(
            target_url,
            data=self._build_value_map(
                BeautifulSoup(req.text, "lxml"),
                email=self.username,
                password=self.password,
            ),
        )
        if not req.ok:
            raise AuthenticationError("Failed to log in, check credentials")
        soup = BeautifulSoup(req.text, "lxml")
        if soup.find(id="inputConfirm"):
            raise AuthenticationError(
                "Failed to log in, unknown email create account manually"
            )
        value_map = {
            node.attrs.get("name"): node.attrs.get("value")
            for node in soup.find(id="inputSaveAs").parent.find_all("input")
        }
        del value_map["access"]
        req = requests.post(
            target_url,
            data={**value_map, "submit": "yes", "access": "raw"},
            stream=stream,
        )
        if not req.ok:
            raise ExportError("Could not retrieve export from SeppMail")
        return req

    @staticmethod
    def _get_valid_filename(name: str) -> str:
        s = str(name).strip().replace(" ", "_")
        s = re.sub(r"(?u)[^-\w.]", "", s)
        if s in ("", ".", ".."):
            raise ValueError("Invalid filename")
        return s

    def convert_file(
        self,
        input_file: pathlib.Path,
        force: bool = False,
        delete: bool = False,
        output: pathlib.Path = None,
    ):
        req = self.convert(input_file.read_text("utf-8"), force)

        if not output:
            filename = str(
                re.findall("filename=(.+)", req.headers["content-disposition"])[0]
            )[1:-1]
            output = pathlib.Path(
                str(
                    input_file.parent.joinpath(
                        self._get_valid_filename(filename)
                        or ".".join((input_file.stem, "eml"))
                    )
                )
            )
        output.write_bytes(req.content)
        if delete:
            input_file.unlink()
        return output
