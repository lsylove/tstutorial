import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import trec.docids
import trec.formatter
import trec.seed
import db.word_to_vector
import db.doc_to_dir
import directories.general
import directories.author
