from contextlib import suppress
from html import unescape
import re


def process_text(message: str) -> str:
    with suppress(IndexError):
        text = re.findall("<Text.*?>(?P<text>.*?)</Text>", message)[0]
        parts = re.findall(
            "<Message.*?>(?P<message>.*?)</Message>.*?<StackTrace.*?>(?P<traceback>.*?)</StackTrace>",
            message,
            re.DOTALL,
        )
        messages = [x[0].rstrip(".") + "\n" + unescape(x[1].replace("&#xD;", "")) for x in parts]
        message = text + "\n" + "\n\n".join(messages)
    return message


class ElmaError(RuntimeError):
    def __init__(self, message, plain: bool = False):
        super().__init__(message if plain else process_text(message))
