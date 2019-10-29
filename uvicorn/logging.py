import logging
import sys

import click


class ColourizedFormatter(logging.Formatter):
    level_name_colours = {
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="blue"),
        logging.INFO: lambda level_name: click.style(str(level_name), fg="green"),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="yellow"),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
        logging.CRITICAL: lambda level_name: click.style(
            str(level_name), fg="bright_red"
        ),
    }

    def __init__(self, fmt=None, datefmt=None, style="%"):
        self.colourize = self.should_colourize()
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def colourized_level_name(self, level_name, level_no):
        default = lambda level_name: str(level_name)
        func = self.level_name_colours.get(level_no, default)
        return func(level_name)

    def should_colourize(self):
        return True

    def formatMessage(self, record):
        if self.colourize:
            record.__dict__["levelname"] = self.colourized_level_name(
                record.levelname, record.levelno
            )
            if "colorized" in record.__dict__:
                record.msg = record.__dict__["colorized"]
                record.__dict__["message"] = record.getMessage()
        return super().formatMessage(record)


class ErrorFormatter(ColourizedFormatter):
    def should_colourize(self):
        return sys.stderr.isatty()


class AccessFormatter(ColourizedFormatter):
    status_code_colours = {
        1: lambda code: click.style(str(code), fg="bright_white"),
        2: lambda code: click.style(str(code), fg="green"),
        3: lambda code: click.style(str(code), fg="yellow"),
        4: lambda code: click.style(str(code), fg="red"),
        5: lambda code: click.style(str(code), fg="bright_red"),
    }

    def should_colourize(self):
        return sys.stdout.isatty()

    def get_client_addr(self, scope):
        client = scope.get("client")
        if not client:
            return ""
        return "%s:%d" % (client[0], client[1])

    def get_path(self, scope):
        return scope.get("root_path", "") + scope["path"]

    def get_full_path(self, scope):
        path = scope.get("root_path", "") + scope["path"]
        query_string = scope.get("query_string", b"").decode("ascii")
        if query_string:
            return path + "?" + query_string
        return path

    def get_status_code(self, record):
        status_code = record.__dict__["status_code"]
        if self.colourize:
            default = lambda code: str(codstatus_codee)
            func = self.status_code_colours.get(status_code // 100, default)
            return func(status_code)
        return str(status_code)

    def formatMessage(self, record):
        scope = record.__dict__["scope"]
        method = scope["method"]
        path = self.get_path(scope)
        full_path = self.get_full_path(scope)
        client_addr = self.get_client_addr(scope)
        status_code = self.get_status_code(record)
        http_version = scope["http_version"]
        request_line = "%s %s HTTP/%s" % (method, full_path, http_version)
        if self.colourize:
            request_line = click.style(request_line, bold=True)
        record.__dict__.update(
            {
                "method": method,
                "path": path,
                "full_path": full_path,
                "client_addr": client_addr,
                "request_line": request_line,
                "status_code": status_code,
                "http_version": http_version,
            }
        )
        return super().formatMessage(record)
