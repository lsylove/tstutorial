import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import trec.docids
import trec.formatter
import trec.seed
import db.word_to_vector
import db.doc_to_dir
import db.attachment_type
import directories.general
import directories.author
import documents.attachment
import documents.general
import documents.message
import core.batch
import core.trec_batch
import core.model
