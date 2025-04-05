from unittest import TestCase

from prog.helpers import SelectMethods


#from ..helpers import SelectMethods

class TestSelectMethods(TestCase):
    def test_val(self):
        self.assertEqual(SelectMethods.PRIORITY.value, 'By Priority')

    def test_name(self):
        self.assertEqual(SelectMethods.PRIORITY.name, 'PRIORITY')

    def test_eq(self):
        tmp_ret = SelectMethods['PRIORITY']
        self.assertEqual(tmp_ret, SelectMethods.PRIORITY)
