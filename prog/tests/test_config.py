import unittest
import pprint
import cherrypy
import tempfile
from prog.config import config, log, Config
import logging, os
import unittest

logging.basicConfig(level=logging.DEBUG)

current_directory = os.getcwd()


class TypeHintClass():
    test_attr: str
    test_check = None

    def __getattr__(self, item):
        if item == 'test_attr':
            self.test_attr = 'found'
            return 'foobar'



class TesttypeHintsInClassMyTestCase(unittest.TestCase):
    def test_call(self):
        tc = TypeHintClass()
        r = tc.test_attr
        self.assertEqual(r, 'foobar')  # add assertion here


class TestConfigLoad(unittest.TestCase):

    def get_config(self, base_dir='', allow_insecure=True, auto_save_config=False, **kwargs):
        tmp_ret = Config(
            base_dir=base_dir,
            allow_insecure=allow_insecure,
            auto_save_config=auto_save_config,
            log_file=None,
            log_level=logging.DEBUG,
            **kwargs)
        return tmp_ret

    def test_no_file_load(self):
        c = self.get_config()
        self.assertFalse(c.config_loaded)

    def test_write_config_with_change(self):
        with tempfile.TemporaryDirectory(dir=current_directory) as tmpdirname:
            c = self.get_config(tmpdirname, port=80)
            self.assertFalse(c.config_loaded)
            self.assertEqual(c.port, 80)
            c.save_config()


            log.error('***************************************************************************')
            log.error('***************************************************************************')
            log.error('***************************************************************************')
            log.error('***************************************************************************')
            log.error('***************************************************************************')

            d = self.get_config(tmpdirname)

            # d.read_config()
            self.assertEqual(d.port, 80)
            self.assertTrue(d.config_loaded)

    def test_no_base_path(self):
        c = self.get_config(base_dir=None)
        self.assertEqual(c.data_file, 'godb.json')

    def test_change_base_path(self):
        with tempfile.TemporaryDirectory(dir=current_directory) as tmpdirname:
            c = self.get_config(tmpdirname)
            tdn = os.path.join(tmpdirname, 'godb.json')
            self.assertEqual(c.data_file, tdn)


    def test_base_path_with_concrete_path(self):
        with tempfile.TemporaryDirectory(dir=current_directory) as tmpdirname:
            c = self.get_config(tmpdirname, data_file='/test/go.db')
            tmp_ret = c.data_file
            if tmp_ret.startswith('C:'):
                tmp_ret = tmp_ret[2:]
            self.assertEqual(tmp_ret, '/test/go.db')





if __name__ == '__main__':
    unittest.main()
