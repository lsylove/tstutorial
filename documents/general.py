import nltk
import re
from itertools import count
from datetime import datetime
from typing import *
from .attachment import SYMBOL


DT_PLACEHOLDER_PROTO = "__dt__placeholder__#"
DT_PLACEHOLDER_HEAD = DT_PLACEHOLDER_PROTO.replace("#", "h")

FOOTER = "***********\n" + SYMBOL


def datetime_head(message: str) -> Tuple[str, str, List[str]]:
    cut = message.find("From:")
    ret = " ".join([DT_PLACEHOLDER_HEAD, DT_PLACEHOLDER_HEAD, message[cut:]])
    dt = datetime.strptime(message[6:cut - 7], "%a, %d %b %Y %H:%M:%S %z")
    return ret, DT_PLACEHOLDER_HEAD, [dt.strftime("%d/%m/%Y"), dt.strftime("%H:%M:%S")]


def drop_headers(message: str) -> str:
    cut_b = message.find("X-SDOC:")
    cut_e = message.find(".eml")
    assert cut_b < cut_e
    message = message[:cut_b] + message[cut_e + 5:]
    cut_b = message.find("From:")
    cut_e = message.find("Subject:")
    while cut_b != -1:
        assert cut_b < cut_e
        message = message[:cut_b] + message[cut_e + 9:]
        cut_b = message.find("---")
        cut_e = message.find("Subject:")
    return message[:message.find(FOOTER)]


def drop_tags(message: str) -> str:
    length = len(message)
    match = re.search(r"<[^><]+>", message)
    while match:
        assert length > (match.end() - match.start()) * 20
        message = message[:match.start()] + message[match.end():]
        match = re.search(r"<[^><]+>", message)
    return message


def simplify(message: str) -> List[str]:
    message = message.lower().replace("-", "_")
    text = [re.sub(r"\d", "#", re.sub(r"[^A-Za-z0-9'_.]+", "", w)) for w in message.split() if w]
    return list(filter(lambda w: not re.match(r"^#+$", w), text))


def drop_stopwords(text: List[str]) -> List[str]:
    global sw
    return list(filter(lambda w: w not in sw, text))


def drop_url(text: List[str]) -> List[str]:
    return list(filter(lambda w: not (".com" in w or "www" in w or "co." in w or "http" in w or ".net" in w), text))


def remove_period(text: List[str]) -> List[str]:
    text = [w.split(".") for w in text if not re.match(r"^\.*$", w)]
    return [w for l in text for w in l if len(w) and not re.match(r"^[#_]+$", w)]


def recover_datetime(text: List[str], dt: Mapping[str, List[str]]) -> List[str]:
    dt = {k: (count(), v) for k, v in dt.items()}
    return [dt[w][1][next(dt[w][0])] if w in dt else w for w in text]


def lemmatize(text: List[str]) -> List[str]:
    global lz
    return [str(min(lz.lemmatize(w), lz.lemmatize(w, pos="v"), key=len)) for w in text]


sw = set(nltk.corpus.stopwords.words("english"))
lz = nltk.stem.WordNetLemmatizer()
