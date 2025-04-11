import unittest
from urllib.parse import urlparse
from prog.url_helpers import check_braces, make_qs_dict, merge_queries, UrlObj
from prog.exceptions import TemplateError
from prog.records import PRE_URL_REGEX
import logging

logging.basicConfig(level=logging.DEBUG)


class TestUrlHelpers(unittest.TestCase):
    def test_regex(self):

        REGEX_TESTS = [
            # (1, 'in_str', ['out1', 'out2']),
            # test empty
            # test no finds
            # test unbalanced
            # test with double brackests
            # test single find
            # test mult finds
            # test with numbers
            # test with longer strings
            # test with invalid contents
            # test with bracket inside brackets

            (10, '', []),
            (20, 'in_str', []),
            (30, '{in_str', []),
            (40, '{{in_str}}', []),
            (45, '{in_str}', ['in_str']),
            (50, 'in{str}foobar{{test}}', ['str']),
            (60, 'in{str}{foobar}', ['str', 'foobar']),
            (70, 'in{str}{1}', ['str', '1']),
            (80, 'in{strwithlonger}{1}{}', ['strwithlonger', '1', '']),
            (90, 'in_str{}', ['']),
            (100, 'in_str{xx.#}', []),

        ]

        for num, str_in, exp_out in REGEX_TESTS:
            with self.subTest(num=num, str_in=str_in):
                self.assertEqual(PRE_URL_REGEX.findall(str_in), exp_out)

    def test_check_braces(self):

        CHECK_BRACE_DATA = [
            (10, True, 'foobar'),
            (11, True, '{foobar}'),
            (12, True, 'f{{oob}}ar'),
            (13, True, 'f{oob}ar'),

            (20, False, '{foobar'),
            (21, False, '{{foobar'),
            (22, False, '{f{oobar}d}'),
            (23, False, 'd{{f{oobar}d}}x'),
            (24, False, 'foobar}'),
            (25, False, 'foobar}dd'),
            (26, False, 'foobar}}dd'),
        ]

        for num, good, check_str in CHECK_BRACE_DATA:
            with self.subTest(num=num, good=good):
                if good:
                    check_braces(check_str)
                else:
                    with self.assertRaises(TemplateError):
                        check_braces(check_str)

    def test_make_qs_dict(self):
        MAKE_QS_DICT = [
            (10, 'http://google.com', {}),
            (11, 'test=foo', {'test': ['foo']}),
            (12, 'testfoo', {}),
            (13, {'test': 'foo'}, {'test': ['foo']}),
            (14, 'google.com?test=foo&bar=snafu&bar=remf', {'test': ['foo'], 'bar': ['snafu', 'remf']}),
            (15, urlparse('google.com?test=foo&bar=snafu'), {'test': ['foo'], 'bar': ['snafu']}),
        ]

        for num, obj_in, check_str in MAKE_QS_DICT:
            with self.subTest(num=num, good=repr(obj_in)):
                self.assertEqual(make_qs_dict(obj_in), check_str)

    def test_basic_parse_url(self):
        tmp_out = urlparse('?test=foo&bar=snafu')
        self.assertEqual(tmp_out.query, 'test=foo&bar=snafu', repr(tmp_out))

    def test_merge_queries(self):

        MERGE_QUERIES_DATA = [
            # passed info, template_info
            (10, 'http://google.com', 'test=foo', {'test': ['foo']}, 'test=foo'),  # NONE, info
            (11, 'google.com', 'http://google.com?sna=fu', {'sna': ['fu']}, 'sna=fu'),  # info, none
            (12, 'http://google.com?test=foo', 'sna=fu', {'test': ['foo'], 'sna': ['fu']}, 'sna=fu&test=foo'),
            # info, info
            (13, 'http://google.com?test=foo', 'test=bar', {'test': ['foo']}, 'test=foo'),  # matching info, override
            (14, 'http://google.com?test=bar', 'test=foo', {'test': ['bar']}, 'test=bar'),  # matching info, no override
            (15, 'http://google.com?test=bar&test=foo', 'test=foo', {'test': ['bar', 'foo']}, 'test=bar&test=foo'),
            # matching info, no override
            (16, 'http://google.com', '', {}, ''),  # matching info, no override
            (17, 'http://google.com', 'ibm.com', {}, ''),  # matching info, no override
        ]

        for num, passed_info, template_info, exp_out, exp_str in MERGE_QUERIES_DATA:
            with self.subTest(num=num):
                with self.subTest(out_type='str'):
                    self.assertEqual(merge_queries(passed_info, template_info, as_str=True), exp_str)
                with self.subTest(out_type='dict'):
                    self.assertEqual(merge_queries(passed_info, template_info, as_str=False), exp_out)

    def test_url_obj(self):
        url = UrlObj('http://go.test.com/foo/bar/sna/fu?test=answer')
        self.assertEqual(str(url), 'http://go.test.com/foo/bar/sna/fu?test=answer')
        self.assertEqual(len(url), 4, repr(url))

        self.assertEqual(url.next, 'foo')
        self.assertEqual(url.remaining_path, ['bar', 'sna', 'fu'], repr(url))
        self.assertTrue(url)
        self.assertEqual(len(url), 3, repr(url))

        self.assertEqual(url.next, 'bar', repr(url))
        self.assertEqual(url.remaining_path, ['sna', 'fu'])
        self.assertTrue(url)
        self.assertEqual(len(url), 2)

        self.assertEqual(url.next, 'sna')
        self.assertEqual(url.remaining_path, ['fu'])
        self.assertTrue(url)
        self.assertEqual(len(url), 1)

        self.assertEqual(url.next, 'fu')
        self.assertEqual(url.remaining_path, [])
        self.assertFalse(url)
        self.assertEqual(len(url), 0)

        self.assertEqual(url.next, '')
        self.assertEqual(url.remaining_path, [])
        self.assertFalse(url)
        self.assertEqual(len(url), 0)

        self.assertEqual(url.next, '')
        self.assertEqual(url.remaining_path, [])
        self.assertFalse(url)
        self.assertEqual(len(url), 0)

    def test_url_iter(self):
        url = UrlObj('http://go.test.com/foo/bar/sna/fu?test=answer')
        EXP_PATHS = ['foo', 'bar', 'sna', 'fu']

        for i, p in enumerate(url):
            with self.subTest(expected=p, pass_no=i):
                self.assertEqual(p, EXP_PATHS[i], repr(url))
                self.assertEqual(url.remaining_path, EXP_PATHS[i+1:], repr(url))
                self.assertEqual(bool(url), i < len(EXP_PATHS), repr(url))

    def test_url_obj_no_segments(self):
        url = UrlObj('http://go.test.com')
        self.assertEqual(str(url), 'http://go.test.com')
        self.assertEqual(len(url), 0, repr(url))
        self.assertFalse(url)

        self.assertEqual(url.next, '')
        self.assertEqual(url.remaining_path, [], repr(url))
        self.assertFalse(url)
        self.assertEqual(len(url), 0, repr(url))

    def test_url_obj_1_segment(self):
        url = UrlObj('http://go.test.com/foo/')
        self.assertEqual(str(url), 'http://go.test.com/foo/')
        self.assertEqual(len(url), 1, repr(url))

        self.assertEqual(url.next, 'foo')
        self.assertEqual(url.remaining_path, [], repr(url))
        self.assertFalse(url)
        self.assertEqual(len(url), 0, repr(url))

        self.assertEqual(url.next, '')
        self.assertEqual(url.remaining_path, [], repr(url))
        self.assertFalse(url)
        self.assertEqual(len(url), 0, repr(url))
