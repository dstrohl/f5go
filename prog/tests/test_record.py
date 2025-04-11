import unittest
from prog.records import LinkRecord
from prog.url_helpers import UrlObj

VARIABLES_FOR_TEST = {
    'var1': 'text1',
    'var2': 'text2',
    'var3': 'text3',
    'var4': 'text4',
}
URL_TESTS = [
    # num, template, passed, returned
    (100, 'https://google.com', 'https://go/ogle', 'https://google.com'),
    (110, 'https://google.com/{var1}', 'https://go/ogle', 'https://google.com/text1'),
    (120, 'https://google.com', 'https://go/ogle/t1/t2', 'https://google.com/t1/t2'),
    (130, 'https://google.com', 'https://go/ogle?foo=bar', 'https://google.com?foo=bar'),
    (140, 'https://google.com', 'https://go/ogle/t1/t2?foo=bar', 'https://google.com/t1/t2?foo=bar'),
    (150, 'https://google.com/x2/{}', 'https://go/ogle', 'https://google.com/x2/'),
    (160, 'https://google.com/x2/{}', 'https://go/ogle/t1/t2', 'https://google.com/x2/t1/t2'),
    (170, 'https://google.com/x2/{}', 'https://go/ogle/t1?foo=bar', 'https://google.com/x2/t1/t2?foo=bar'),
    (180, 'https://google.com?foo={}', 'https://go/ogle', 'https://google.com?foo'),
    (190, 'https://google.com?foo={}', 'https://go/ogle/t1', 'https://google.com?foo'),
    (200, 'https://google.com?foo={}', 'https://go/ogle/t1/t2', 'https://google.com?foo=/t1/t2'),
    (210, 'https://google.com?foo={}', 'https://go/ogle/t1?sna=fu', 'https://google.com?foo=t1/t2&sna=fu'),
    (220, 'https://test.com/{}', 'https://go/ogle/a/b/c/d?e=f', 'https://test.com/a/b/c/d?e=f'),
    (230, 'https://test.com/{p}', 'https://go/ogle/a/b/c/d?e=f', 'https://test.com/a/b/c/d'),
    (240, 'https://test.com/{q}', 'https://go/ogle/a/b/c/d?e=f', 'https://test.com?e=f'),
    (250, 'https://test.com/{1}', 'https://go/ogle/a/b/c/d?e=f', 'https://test.com/a'),
    (260, 'https://test.com/{1}{3}/{p}', 'https://go/ogle/a/b/c/d?e=f', 'https://test.com/ac/b/d'),
    (270, 'https://test.com/{5}', 'https://go/ogle/a/b/c/d?e=f', 'https://test.com/'),
    (280, 'https://test.com/{1}/{2}{q}', 'https://go/ogle/a/b/c/d?e=f', 'https://test.com/a/b?e=f'),
]

class TestUrlTemplate(unittest.TestCase):
    def make_link_record(self,
                          template,
                          var_ref=None,
                          local_replacement_str=None,
                          local_error_handling=None
                          ):
        if var_ref is None:
            var_ref = VARIABLES_FOR_TEST.copy()
        return LinkRecord(template,
                          var_ref=var_ref,
                          local_replacement_str=local_replacement_str,
                          lical_error_handling=local_error_handling)

    def test_create_obj_none(self):
        for n, t, sent, exp in URL_TESTS:
            with self.subTest(num=n, sent=sent, exp=exp):
                sent = UrlObj(sent)
                sent.next
                lr = self.make_link_record(t)
                act_ret = lr.get_url(sent, variables=VARIABLES_FOR_TEST)
                self.assertEqual(act_ret, exp, repr(lr))

    def test_error_missing_var(self):
        pass
    
    def test_update(self):
        pass

    def test_get_url_base(self):
        pass

    def test_get_url_generated(self):
        pass
