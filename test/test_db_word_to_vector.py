import unittest
from .context import db


class ComposeTC(unittest.TestCase):
    def test_compose_datetime_vector(self):
        line = "31/01/2010"
        res = db.word_to_vector.compose_datetime_vector(line)
        self.assertAlmostEqual(res[0], 0.1)
        self.assertLess(0., res[1])
        self.assertLess(res[1], 0.25)
        for elt in res[2:]:
            self.assertAlmostEqual(elt, 0.)
        line = "31/08/2009"
        res = db.word_to_vector.compose_datetime_vector(line)
        self.assertAlmostEqual(res[0], 0.1)
        self.assertLess(-0.25, res[1])
        self.assertLess(res[1], 0.)
        for elt in res[2:]:
            self.assertAlmostEqual(elt, 0.)
        line = "23:25"
        res = db.word_to_vector.compose_datetime_vector(line)
        self.assertAlmostEqual(res[0], 0.2)
        self.assertLess(0., res[1])
        self.assertLess(res[1], 0.25)
        for elt in res[2:]:
            self.assertAlmostEqual(elt, 0.)


@unittest.skip
class WriterTC(unittest.TestCase):
    def tearDown(self):
        db.word_to_vector.destroy()

    def test_writer(self):
        model = db.word_to_vector.default_model()
        self.assertTrue("New_York" in model)

        lines = "new york hot dog enumeration lakjkljr pencil 31/08/2018 15:04 hot new york chicken 15:04".split(" ")
        with db.word_to_vector.Writer(model) as writer:
            writer.add(lines)
            self.assertEqual(len(writer.markerA), 9)
            self.assertEqual(len(writer.markerB), 2)
            self.assertEqual(len(writer.markerC), 1)
            self.assertEqual(writer.statA, 13)
            self.assertEqual(writer.statB, 3)
            self.assertEqual(writer.statC, 1)


class ReaderTC(unittest.TestCase):
    def tearDown(self):
        db.word_to_vector.destroy()

    def test_writer_and_reader(self):
        model = db.word_to_vector.default_model()
        lines = "Congressional hearing Washington Bureau Chief Peter Cook House subcommittees subpoenas 31/08/2018"\
            .split(" ")
        with db.word_to_vector.Writer(model) as writer:
            writer.add(lines)
            self.assertEqual(len(writer.markerA), 10)
            self.assertEqual(len(writer.markerB), 1)
            self.assertEqual(len(writer.markerC), 0)
            self.assertEqual(writer.statA, 10)
            self.assertEqual(writer.statB, 1)
            self.assertEqual(writer.statC, 0)
        with db.word_to_vector.Reader() as reader:
            print("**Congressional**")
            vector = reader.find("Congressional")
            self.assertEqual(len(vector), 1204)
            for elt in vector[slice(20)]:
                print(elt)
            print("**House**")
            vector = reader.find("House")
            self.assertEqual(len(vector), 1204)
            for elt in vector[slice(20)]:
                print(elt)
            print("**31/08/2018**")
            vector = reader.find("31/08/2018")
            self.assertEqual(len(vector), 1204)
            for elt in vector[slice(20)]:
                print(elt)


if __name__ == "__main__":
    unittest.main()
