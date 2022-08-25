import re
from html import unescape


class ElmaError(RuntimeError):
    def __init__(self, message):
        try:
            text = re.findall("<Text.*?>(?P<text>.*?)</Text>", message)[0]
            parts = re.findall(
                "<Message.*?>(?P<message>.*?)</Message>.*?<StackTrace.*?>(?P<traceback>.*?)</StackTrace>",
                message,
                re.DOTALL,
            )
            messages = [x[0].rstrip(".") + "\n" + unescape(x[1].replace("&#xD;", "")) for x in parts]
            message = text + "\n" + "\n\n".join(messages)
        except IndexError:
            ...
        super().__init__(message)
