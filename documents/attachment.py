import re
import documents.general
from typing import *


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
        if not foot_check and not line.startswith(documents.general.SYMBOL):
            continue
        foot_check = True
        if line.startswith("Attachment:"):
            attachment_type = parse_attachment_type(line)
            ret.append(attachment_type)
    return ret


def process(message: Iterable[str]) -> List[str]:
    long_message = "".join(message)
    long_message = documents.general.drop_tags(long_message)
    text = documents.general.simplify(long_message)
    text = documents.general.drop_stopwords(text)
    text = documents.general.drop_url(text)
    text = documents.general.remove_period(text)
    text = documents.general.lemmatize(text)
    text = documents.general.drop_weirdos(text)
    return text
