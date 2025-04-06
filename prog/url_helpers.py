from urllib import parse
import re
from exceptions import TemplateError, MissingKeys
from prog.config import log

""" looking for {}, {n} {xxx} """
PRE_URL_REGEX = re.compile(r'.*(\{\w*\}).*')

class UrlObj(object):
    def __init__(self, url_in):
        self.used_path = []
        self.remaining_path = []

        self.initial_url_str = url_in
        self.url = parse.urlparse(url_in)
        self.path_list = self.url.path.split('/')
        self.query = self.url.query

    def get_next_path(self):
        if not self.remaining_path:
            return None
        else:
            tmp_return = self.remaining_path.pop(0)
            self.used_path.append(tmp_return)
            return tmp_return


class UrlTemplate(object):
    replacement_str = ''
    error_handling = 'ERROR'
    template_str = ''
    positional = None
    named = None
    copy_all = False
    max_pos = 0
    generative = False

    def __init__(self, template, vars=None, var_check=True, replacement_str='', error_handling='ERROR'):
        self.template_str = template
        self.positional = []
        self.named = []
        self.update(template, error_handling, vars, var_check, replacement_str)

    def update(self, template=None, error_handling='ERROR', vars=None, var_check=True, replacement_str=''):
        self.error_handling = error_handling.upper()
        self.replacement_str = replacement_str

        self.positional.clear()
        self.named.clear()
        self.copy_all = False
        self.generative = False

        in_open = False
        in_double_open = False
        last_open_pos = 0

        for n, c in enumerate(template):
            if c == '{':
                if in_double_open:
                    continue
                if in_open:
                    if n + 1 == last_open_pos:
                        in_double_open = True
                        last_open_pos = 0
                        continue
                    raise TemplateError('Missing closing brace at position: {}, in: {}'.format(n+1, template))
                in_open = True
                last_open_pos = n
                continue
            if c == '}':
                if in_double_open:
                    in_double_open = False
                    continue
                if not in_open:
                    raise TemplateError('Missing opening brace before position: {}, in: {}'.format(n+1, template))
                in_open = False
                last_open_pos = 0

        tmp_match_list = PRE_URL_REGEX.findall(template)
        if tmp_match_list:
            self.generative = True
            for tmp_match in tmp_match_list:
                tmp_match = tmp_match[1:-1]
                if len(tmp_match) > 1 and tmp_match[1:2] == '{{':
                    continue
                if len(tmp_match) > 3 and tmp_match[-2:-1] == '}}':
                    continue
                if tmp_match == '':
                    if self.positional or self.named:
                        raise TemplateError('Cannot have any positional or named variable with save all ("{}")')
                    self.copy_all = True
                    continue
                if tmp_match.isdigit():
                    if self.copy_all:
                        raise TemplateError('Cannot have positional number after save all')
                    num = int(tmp_match) - 1
                    if num < 0:
                        raise TemplateError('Positional number cannot be less than 1')
                    self.positional.append(num)
                    self.max_pos = max(self.max_pos, num)
                else:
                    if self.copy_all:
                        raise TemplateError('Cannot have positional number after save all')
                    if var_check and tmp_match[1:-1] not in vars:
                        raise MissingKeys('Missing Variable in variable setup: '.format(tmp_match[1:-1]))
                    self.named.append(tmp_match[1:-1])
            if self.positional:
                self.positional.sort(reverse=True)

    def get_url(self, url_obj:UrlObj, vars:dict=None, cookies:dict=None):
        if self.generative:
            positionals = []
            named = {}

            if self.copy_all:
                tmp_rep = '/'.join(url_obj.remaining_path)
                if url_obj.query:
                    tmp_rep = '{}?{}'.format(tmp_rep, url_obj.query)
                positionals.append(tmp_rep)
            else:

                for k in self.named:
                    if k in ['p', 'q']:
                        continue
                    if k in cookies:
                        named[k] = cookies[str(k)]
                    elif k in vars:
                        named[k] = vars[str(k)]
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

                if 'p' in self.named:
                    named['p'] = '/'.join(url_obj.remaining_path)
                if 'q' in self.named:
                    named['q'] = url_obj.query

            new_url = self.template_str.format(*positionals, **named)
        else:
            new_url = self.template_str

        new_url = parse.urlsplit(new_url)

        # need to do the following


