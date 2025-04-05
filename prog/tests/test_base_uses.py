import unittest
from prog.bases import RecentUses, LastXEdits
import datetime
import logging

from prog.config import config

config.set_overrides(
    allow_insecure = True,
    auto_save_config = False,
    log_file = None,
    log_level = logging.DEBUG
)


class TestUses(unittest.TestCase):


    def test_add_use(self):
        u = RecentUses()
        self.assertEqual(int(u), 0)
        u.add()
        self.assertEqual(int(u), 1)
        u.add()
        self.assertEqual(int(u), 2)
        u.add()
        self.assertEqual(int(u), 3)
        u.add()
        self.assertEqual(int(u), 4)
        self.assertEqual(len(u), 1)

    def test_old_clearing(self):
        u = RecentUses()
        self.assertEqual(int(u), 0)
        t = datetime.date.today().toordinal()
        t = t - 9
        c = 0
        c2 = 0
        for i in range(1, 11):
            if c < 14:
                c2 += 1
                c += 2
            u.add(t)
            u.add(t)
            t += 1
            self.assertEqual(int(u), c)
            self.assertEqual(len(u), c2)

    def test_load_get_data(self):
        t = datetime.date.today().toordinal()
        t -= 9
        u = RecentUses()
        td = {}
        for i in range(1, 11):
            td[t] = 2
            t += 1
        u.load_data(td)
        self.assertEqual(int(u), 14)
        self.assertEqual(len(u), 7)

        tout = u.get_data()
        self.assertEqual(len(tout), 7)


class TestEdits(unittest.TestCase):
    def test_add_edit(self):
        e = LastXEdits()
        self.assertEqual(len(e), 0)
        e.add('t1')
        e.add('t2')
        e.add('t3')
        self.assertEqual(len(e), 3)
        self.assertEqual(e.last_edit_user, 't3')
        self.assertEqual(e.last_edit_date, datetime.date.today().toordinal())

    def test_edits_clean(self):
        t = datetime.date.today().toordinal() - 30
        e = LastXEdits()
        for i in range(1, 30):
            e.add('t'+str(i), t)
            if i > 20:
                self.assertEqual(len(e), 20)
            else:
                self.assertEqual(len(e), i)
            self.assertEqual(e.last_edit_date, t)
            self.assertEqual(e.last_edit_user, 't'+str(i))

            t += 1

        self.assertEqual(len(e), 20)
        self.assertEqual(e.last_edit_date, t-1)
        self.assertEqual(e.last_edit_user, 't29')

    def test_load_get_data(self):
        t = datetime.date.today().toordinal() - 30
        e = LastXEdits()
        timp = []
        for i in range(30):
            timp.append(('t'+str(i), t))
            t += 1

        e.load_data(timp)

        self.assertEqual(len(e), 20)
        self.assertEqual(e.last_edit_date, t-1)
        self.assertEqual(e.last_edit_user, 't29')

        tout = e.get_data()
        self.assertEqual(len(tout), 20)
        self.assertEqual(tout[-1][1], t-1)
        self.assertEqual(tout[-1][0], 't29')


if __name__ == '__main__':
    unittest.main()
