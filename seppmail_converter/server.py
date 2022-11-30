import re

from flask import (
    Flask,
    request,
    Response,
    make_response,
    render_template,
    send_from_directory,
    send_file,
)
from werkzeug.exceptions import BadRequest

from seppmail_converter.seppmail import Seppmail

app = Flask("seppmail_converter")


@app.errorhandler(404)
def not_found(e):
    return {
        "error": "Not Found",
        "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.",
    }, 404


@app.errorhandler(BadRequest)
def bad_request(e):
    return {
        "error": "Bad Request",
        "message": "The server could not understand the request due to invalid syntax.",
        "exception": str(e),
    }, 400


@app.get("/")
def main():
    return send_from_directory("templates", "index.html")


@app.post("/api/v1/convert")
def convert():
    if "file" not in request.files.keys():
        raise BadRequest("No file provided")
    file = request.files["file"].read().decode("utf-8")
    sepp = Seppmail(
        app.config.get("SEPPMAIL_USERNAME"), app.config.get("SEPPMAIL_PASSWORD")
    )
    try:
        req = sepp.convert(file, stream=True)
    except Exception as e:
        raise BadRequest(str(e))
    filename = str(re.findall("filename=(.+)", req.headers["content-disposition"])[0])[
        1:-1
    ]
    resp = send_file(req.raw, as_attachment=True, download_name=filename)
    resp.headers = {**req.headers}
    return resp
