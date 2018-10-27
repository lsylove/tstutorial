import documents.attachment
import documents.general
from typing import *


def is_message(doc_id: str) -> bool:
    return not documents.attachment.is_attachment(doc_id)


def process(message: Iterable[str]) -> List[str]:
    long_message = "".join(message)
    long_message, k, v = documents.general.datetime_head(long_message)
    long_message = documents.general.drop_headers(long_message)
    long_message = documents.general.drop_tags(long_message)
    text = documents.general.simplify(long_message)
    text = documents.general.drop_stopwords(text)
    text = documents.general.drop_url(text)
    text = documents.general.remove_period(text)
    text = documents.general.drop_weirdos(text)
    text = documents.general.recover_datetime(text, {k: v})
    text = documents.general.lemmatize(text)
    return text
