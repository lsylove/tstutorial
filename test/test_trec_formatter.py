import unittest
import definitions
from .context import trec


class TC(unittest.TestCase):
    def test_format_attributes(self):
        line = trec.format_attributes(201, "abcdefg", 1, 0.5)
        self.assertEqual(line, "".join(["201 Q0 abcdefg 1 0.50 ", definitions.RUN_ID]))


if __name__ == "__main__":
    unittest.main()
