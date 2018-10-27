import re
from typing import *

SYMBOL = "EDRM Enron Email Data Set has been produced in EML, PST and NSF format by ZL Technologies, Inc."


def is_attachment(doc_id: str) -> bool:
    return re.match("^.*\d+$", doc_id) is not None


def parse_attachment_type(line: str) -> str:
    if not line.startswith("Attachment:"):
        raise TypeError("Attachment line invalid start: " + line)
    try:
        spl = line.split("=")
        v = spl[len(spl) - 1].strip()
        return v
    except IndexError:
        raise TypeError("Attachment line invalid '=' token: " + line)


def parse_attachment_types(message: Iterable[str]) -> List[str]:
    ret = []
    foot_check = False
    for line in message:
        if not foot_check and not line.startswith(SYMBOL):
            continue
        foot_check = True
        if line.startswith("Attachment:"):
            attachment_type = parse_attachment_type(line)
            ret.append(attachment_type)
    return ret
