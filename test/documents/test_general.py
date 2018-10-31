import unittest
from test.context import db, documents


class TC(unittest.TestCase):
    def setUp(self):
        self.reader = db.doc_to_dir.Reader()

    def tearDown(self):
        self.reader.close()

    def test_datetime_head(self):
        head = " ".join([documents.general.DT_PLACEHOLDER_HEAD, documents.general.DT_PLACEHOLDER_HEAD, "From:"])
        with self.reader.open("3.819018.LKPJJANNJNBTQME0XJH0HVYKQBPA2C4LA") as file:
            message = "".join(file.readlines())
            message, k, v = documents.general.datetime_head(message)
            self.assertTrue(message.startswith(head))
            self.assertEqual(k, documents.general.DT_PLACEHOLDER_HEAD)
            self.assertEqual(v[0], "13/12/2000")
            self.assertEqual(v[1], "03:28:00")
        with self.reader.open("3.125295.N2OMLFG1ULOD4CIWIEISTSD2C3ZC0CW0B") as file:
            message = "".join(file.readlines())
            message, k, v = documents.general.datetime_head(message)
            self.assertTrue(message.startswith(head))
            self.assertEqual(k, documents.general.DT_PLACEHOLDER_HEAD)
            self.assertEqual(v[0], "19/11/2000")
            self.assertEqual(v[1], "13:23:00")

    def test_drop_headers(self):
        with self.reader.open("3.819721.J0YXAOF4CBT2VEST4U3YAG1HO0JUKY4XA") as file:
            message = "".join(file.readlines())
            message = documents.general.drop_headers(message)
            self.assertTrue(message.startswith("""Date: Thu, 26 Jul 2001 12:04:16 -0700 (PDT)
FW: FERC Order on Reporting CA gas sales


Janie,

Do you want to work with regulatory to make sure we can comply?


 FERC Order on Reporting CA gas sales

Phillip,  thought this might be of interest.  Ray

FERC Order on Reporting CA gas sales

Attached is the Commission's "Order Imposing Reporting Requirement on Natural Gas Sales to California Market,"""))
        with self.reader.open("3.1004808.GNQ3FZAYPENFA40WFPS4ITWD1SVT1KBSA") as file:
            message = "".join(file.readlines())
            message = documents.general.drop_headers(message)
            print(message)
            self.assertTrue(message.startswith("""Date: Fri, 21 Jul 2000 10:57:00 -0700 (PDT)
Project Summer Matrices; Update

Just so you had the latest matrices; although some of you directly received"""))

    @unittest.skip
    def test_simplify(self):
        with self.reader.open("3.125305.BFH2NDKIWE0TR4LTD35ONZ1I30LL4MSQA.2") as file:
            message = "".join(file.readlines())
            text = documents.general.simplify(message)
            text = list(filter(lambda w: w != "na", text))
            for word in text:
                print(word)

    def test_drop_stopwords(self):
        text = "I didn't live here for last several years before and after today".lower().split()
        text = documents.general.drop_stopwords(text)
        self.assertEqual(len(text), 5)
        self.assertCountEqual(text, {
            "live", "last", "several", "years", "today"
        })

    def test_remove_period(self):
        text = "She.. was.... .. ..so pretty.. ... .1.2.3.4.".lower().split()
        text = documents.general.remove_period(text)
        self.assertEqual(len(text), 5)
        self.assertCountEqual(text, {
            "she", "was", "so", "pretty", "1234"
        })

    def test_lemmatize(self):
        text = "I lived here for last several years before and after today".lower().split()
        text = documents.general.drop_stopwords(text)
        text = documents.general.lemmatize(text)
        self.assertEqual(len(text), 5)
        self.assertCountEqual(text, {
            "live", "last", "several", "year", "today"
        })

    def test_recover_datetime(self):
        with self.reader.open("3.1164307.DRMHD3OURILF32TCQ3HZEE4MOIISK2I2A") as file:
            message = "".join(file.readlines())
            message, k, v = documents.general.datetime_head(message)
            message = documents.general.drop_headers(message)
            message = documents.general.drop_tags(message)
            text = documents.general.simplify(message)
            text = documents.general.drop_stopwords(text)
            text = documents.general.drop_url(text)
            text = documents.general.remove_period(text)
            text = documents.general.drop_weirdos(text)
            text = documents.general.recover_datetime(text, {k: v})
            text = documents.general.lemmatize(text)
            for token in text:
                print(token)
            self.assertEqual(text[0], "01/01/2002")
            self.assertEqual(text[1], "07:25:34")


if __name__ == "__main__":
    unittest.main()
