
from collections import deque

from prog.bases import BaseKeyRecord, BaseRecord, BaseGetLoadObj
from prog.constants import *
from prog.config import config
import re
from prog.exceptions import TemplateError, MissingKeys
from prog.url_helpers import *
from urllib import parse

PRE_URL_REGEX = re.compile(r'(?<!\{)\{(\w*)\}(?!\})')


class ListOfLinks(BaseGetLoadObj):
    """ used to store lists of links"""

    def add_link(self):
        pass

    def remove_link(self):
        pass

    def get_link(self):
        pass

    def _load_data(self):
        pass

    def _get_data(self):
        pass


class ListOfKeys(BaseGetLoadObj):
    def add_key(self):
        pass

    def remove_key(self):
        pass

    def get_key(self):
        pass

    def _load_data(self):
        pass

    def _get_data(self):
        pass

"""
class VariableMapping(BaseKeyRecord):

    def __init__(self, load_data=None, load_type=LOAD_TYPE_NEW, **kwargs):
        self.data = {}
        super().__init__(load_data=load_data, load_type=load_type, **kwargs)

    def _get_data(self):
        return self.data.copy()

    def _load_data(self, data_obj: dict = None, load_type=LOAD_TYPE_UPDATE):
        if load_type == LOAD_TYPE_UPDATE:
            for k, v in data_obj.items():
                self.data[k] = v
        else:
            self.data = data_obj.copy()

    def get_var_dict(self, cookie_vars=None):
        tmp_ret = self.data.copy()
        if cookie_vars is not None:
            tmp_ret.update(cookie_vars)
        return tmp_ret

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __len__(self):
        return len(self.data)

    def items(self):
        return self.data.items()

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def __repr__(self):
        return 'Variables: %r' % self.data.keys()

    def __contains__(self, item):
        return item in self.data
"""


class KeyRecord(BaseKeyRecord):
    """Used to store a single key (lookup) record"""
    Keyword = None
    select_method = None
    children = None
    links = None

    def __init__(self, keyword=None, link=None, select_method=None, user=None, load_data=None, **kwargs):
        self.children = ListOfKeys()
        self.links = ListOfLinks()
        super(KeyRecord, self).__init__(load_data=load_data, **kwargs)
        if load_data:
            return
        self.Keyword = keyword
        if link:
            self.links.add_link(link)
        self.select_method = select_method or PRIORITY
        self.add_edit(user)

    def add_link(self):
        pass
    def rem_link(self):
        pass


    def _load_data(self, data_obj:dict):
        super().__init__(data_obj)
        self.Keyword = data_obj.get('Keyword', self.keyword)
        self.select_method = data_obj.get('select_method', self.select_method)
        if 'children' in data_obj:
            self.children.load_data(data_obj['children'])
        if 'links' in data_obj:
            self.links.load_data(data_obj['links'])

class SpecialKeyRecord(KeyRecord):
    """ used to store regex special link records"""

    regex_match = None
    regex_replace_template = None
    key_type = 'regex'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.regex_match = kwargs.get('regex_match', None)
        self.regex_replace_template = kwargs.get('regex_replace_template', None)



class LinkRecord(BaseRecord):
    """ used to store a single link"""
    priority = 0
    local_replacement_str = None
    local_error_handling = None
    template = ''
    positional = None
    named = None
    copy_all = False
    copy_remainder = True
    copy_query = True
    max_pos = 0
    generative = False
    variable_object = None

    def __init__(self, template, var_ref=None, load_type=LOAD_TYPE_NEW, **kwargs):
        self.positional = []
        self.named = []
        self.var_ref = var_ref
        super().__init__(template=template, load_type=load_type, **kwargs)

    def _get_data(self):
        tmp_ret = super()._get_data()
        tmp_ret['priority'] = self.priority
        tmp_ret['template'] = self.template
        tmp_ret['local_replacement_str'] = self.replacement_str
        tmp_ret['local_error_handling'] = self.error_handling
        return tmp_ret

    def _load_data(self, data_obj:dict=None, load_type=LOAD_TYPE_UPDATE):
        super().__init__(data_obj, load_type=load_type)
        self.priority = data_obj.get('priority', self.priority)
        self.local_replacement_str = data_obj.get('local_replacement_str', self.local_replacement_str)
        self.local_error_handling = data_obj.get('local_error_handling', self.local_error_handling)
        old_template = self.template
        self.template = data_obj.get('template', self.template)
        if old_template != self.template:
            self.process_url()

    @property
    def error_handling(self):
        return self.local_error_handling or config.default_replacement_error_handling

    @property
    def replacement_str(self):
        return self.local_replacement_str or config.default_replacement_replacement_str

    def process_url(self):
        variables = self.var_ref or {}
        template = self.template
        # self.error_handling = error_handling.upper()
        # self.replacement_str = replacement_str

        self.positional.clear()
        self.named.clear()
        self.copy_all = False
        self.generative = False
        self.copy_remainder = False
        self.copy_query = False

        check_braces(template)

        tmp_match_list = PRE_URL_REGEX.findall(template)

        if tmp_match_list:

            self.generative = True

            for tmp_match in tmp_match_list:
                if tmp_match == '':
                    if len(tmp_match) != 1:
                        raise TemplateError('Cannot have any positional or named variable with save all ("{}")')
                    self.copy_all = True
                    break
                if tmp_match.isdigit():
                    num = int(tmp_match) - 1
                    if num < 0:
                        raise TemplateError('Positional number cannot be less than 1')
                    self.positional.append(num)
                    self.max_pos = max(self.max_pos, num)
                elif tmp_match == 'p':
                    self.copy_all = True
                elif tmp_match == 'q':
                    self.copy_all = True
                else:
                    raise MissingKeys('Missing Variable in variable setup: {}'.format(tmp_match))
                    # self.named.append(tmp_match)

    def get_url(self, url_obj:UrlObj, variables:dict=None):
        variables = variables or {}
        if self.generative:
            return self._get_generated_url(url_obj, variables)
        else:
            return self._get_base_url(url_obj)

    def _get_base_url(self, url_obj:UrlObj):
        if isinstance(url_obj, str):
            url_obj = UrlObj(url_obj)
        tmp_ret = self.template
        if url_obj.remaining_path:
            tmp_path = '\\'.join(url_obj.remaining_path)
            tmp_ret = parse.urljoin(tmp_ret, tmp_path)
        tmp_qs = merge_queries(url_obj, self.template, as_str=True)
        if tmp_qs:
            tmp_ret = tmp_ret + '?' + tmp_qs
        return tmp_ret

    def _get_generated_url(self, url_obj:UrlObj, variables:dict=None):
        positionals = []
        named = {}
        variables = variables or {}
        if self.copy_all:
            tmp_rep = '/'.join(url_obj.remaining_path)
            if url_obj.query:
                tmp_rep = '{}?{}'.format(tmp_rep, url_obj.query)
            positionals.append(tmp_rep)
        else:
            for k in self.named:
                if k in variables:
                    named[k] = variables[str(k)]
                else:
                    if self.error_handling == 'REPLACE':
                        named[k] = self.replacement_str
                    else:
                        raise MissingKeys('Missing Variable in variable setup: '.format(k))
            if self.positional:
                if self.max_pos + 1 > len(url_obj.remaining_path):
                    if self.error_handling == 'ERROR':
                        raise TemplateError('Not enough path elements to fill in positional variables')
                for k in range(self.max_pos + 1):
                    if k in self.positional:
                        if k >= len(url_obj.remaining_path):
                            positionals.append(self.replacement_str)
                        else:
                            positionals.append(url_obj.remaining_path.pop(k))
                    else:
                        positionals.append('')

            if self.copy_remainder:
                for x in sorted(self.positional, reverse=True):
                    url_obj.remaining_path.pop(x)
                named['p'] = '/'.join(url_obj.remaining_path)
            if self.copy_query and url_obj.query:
                named['q'] = '?' + url_obj.query

        new_url = self.template.format(*positionals, **named)
        # new_url = parse.urlsplit(new_url)
        new_qs = merge_queries(url_obj, new_url, as_str=True)

        if new_qs:
            new_url = new_url + '?' + new_qs

        return new_url


    def __repr__(self):
        return 'LinkRecord(%s)' % self.template
