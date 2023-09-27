import logging

import colorlog
from colorlog.escape_codes import escape_codes


def setup_logging(level=logging.INFO, verbose: bool = False):
    reset = escape_codes["reset"]
    log_format = f"%(asctime)-15s [%(name)-36s] %(log_color)s%(levelname)-8s:{reset} %(message)s"

    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(log_format))

    logging.basicConfig(format=log_format, level=level, handlers=[handler])

    logging.getLogger("urllib3.connectionpool").setLevel(level)
