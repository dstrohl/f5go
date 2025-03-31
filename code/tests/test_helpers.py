from unittest import TestCase

from code import SelectMethods


#from ..helpers import SelectMethods

class TestSelectMethods(TestCase):
    def test_str(self):
        self.assertEqual(SelectMethods.PRIORITY, 'By Priority')
