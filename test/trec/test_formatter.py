import unittest
import definitions
from test.context import trec


class TC(unittest.TestCase):
    def test_format_attributes(self):
        line = trec.formatter.format_attributes(201, "3.D2M301CF_0449f042", 1, 0.5)
        expect = "".join(["201 Q0 3.D2M301CF_0449f042 1 0.50", " ", definitions.RUN_ID])
        self.assertEqual(line, expect)

    def test_format_object(self):
        obj = {
            "req_id": 201,
            "doc_id": "3.D2M301CF_0449f042",
            "estimate": 0.8
        }
        line = trec.formatter.format_object(obj, 25)
        expect = "".join(["201 Q0 3.D2M301CF_0449f042 25 0.80", " ", definitions.RUN_ID])
        self.assertEqual(line, expect)

    def test_format_object_array(self):
        lst = [{
            "req_id": 201,
            "doc_id": "3.D2M301CF_0449f042",
            "estimate": 0.8
        }, {
            "req_id": 201,
            "doc_id": "3.D2M301CF_58fb8794",
            "estimate": 0.5
        }, {
            "req_id": 201,
            "doc_id": "3.D4M301CF",
            "estimate": 0.
        }, {
            "req_id": 201,
            "doc_id": "3.D4M301CF_0449f042",
            "estimate": 1.
        }, {
            "req_id": 201,
            "doc_id": "3.D4M301CF_58fb8794",
            "estimate": 0.1
        }]
        formatted = trec.formatter.format_object_array(lst)
        line = "\n".join(formatted)
        expect = """201 Q0 3.D2M301CF_0449f042 2 0.80 {0}
201 Q0 3.D2M301CF_58fb8794 3 0.50 {0}
201 Q0 3.D4M301CF 5 0.00 {0}
201 Q0 3.D4M301CF_0449f042 1 1.00 {0}
201 Q0 3.D4M301CF_58fb8794 4 0.10 {0}""".format(definitions.RUN_ID)
        self.assertEqual(line, expect)


if __name__ == "__main__":
    unittest.main()
