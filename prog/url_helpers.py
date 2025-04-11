from urllib import parse
from prog.exceptions import TemplateError
from prog.config import log

__all__ = ['UrlObj', 'check_braces', 'make_list', 'make_qs_dict', 'merge_queries']

""" looking for {}, {n} {xxx} """
# PRE_URL_REGEX = re.compile(r'.*(\{\w*\}).*')


class UrlObj(object):
    def __init__(self, url_in):
        self.next_counter = 0
        self.used_path = []
        self.pending_path = None
        self.initial_url_str = url_in
        self.url = parse.urlparse(url_in)
        self.base = self.url.netloc + ':' + self.url.hostname
        tmp_path = self.url.path.strip('/').strip()
        if tmp_path:
            self._remaining_path = tmp_path.split('/')
        else:
            self._remaining_path = []
        self.query = self.url.query

        log.debug('Created URL Object: %r' % self)

    @property
    def next(self):
        self.next_counter += 1
        log.debug('getting next url path segment (%s)' % self.next_counter)
        if not self._remaining_path:
            if self.pending_path:
                log.debug('returning pending path: %s' % self.pending_path)
                tmp_ret = self.pending_path
                self.pending_path = ''
                return tmp_ret
            else:
                log.debug('no remaining path, returning ""')
                return ''

        """
        if self.pending_path:
        else:
            self.pending_path = self._remaining_path[0]
        """
        if not self.pending_path:
            self.pending_path = self._remaining_path[0]
            log.debug('no current pending path (first path), returning first segment: %s'% self.pending_path)
            log.debug('remaining segments: %r' % self._remaining_path)
            return self.pending_path

        self.used_path.append(self._remaining_path.pop(0))
        if self._remaining_path:
            log.debug('moving next segment to pending segment: %s' % self._remaining_path[0])
            self.pending_path = self._remaining_path[0]
        else:
            log.debug('no next segment')
            self.pending_path = ''
        log.debug('returning segment: %s' % self.pending_path)
        return self.pending_path

    @property
    def remaining_path(self):
        if not self.pending_path:
            return self._remaining_path
        if self._remaining_path:
            return self._remaining_path[1:]
        else:
            return []

    def __len__(self):
        return len(self.remaining_path)

    def __str__(self):
        return self.initial_url_str

    def __iter__(self):
        yield self.next

    def __repr__(self):
        """  http://go.test.com [l1 / l2] l3 [l4 / l5]o=bar  """
        tmp_ret = '{} [{}] {} [{}]'.format(self.base, ' / '.join(self.used_path), self.pending_path, ' / '.join(self.remaining_path))
        if self.query:
            tmp_ret += " ?" + self.query
        tmp_ret += ' ({})'.format(str(self.next_counter))
        return tmp_ret

def check_braces(template):
    in_open = False
    in_double_open = False
    last_open_pos = 0

    for n, c in enumerate(template):
        if c == '{':
            if in_double_open:
                continue
            if in_open:
                if n - 1 == last_open_pos:
                    in_double_open = True
                    last_open_pos = 0
                    continue
                raise TemplateError('Missing closing brace at position: {}, in: {}'.format(n + 1, template))
            in_open = True
            last_open_pos = n
            continue
        if c == '}':
            if in_double_open:
                in_double_open = False
                continue
            if not in_open:
                raise TemplateError('Missing opening brace before position: {}, in: {}'.format(n + 1, template))
            in_open = False
            last_open_pos = 0
    if in_open:
        raise TemplateError('Missing closing brace before position in: {}'.format(template))

def make_qs_dict(info):
    if not info:
        return {}
    if isinstance(info, dict):
        for k, v in info.items():
            info[k] = make_list(v)
        return info
    if isinstance(info, str):
        if '=' in info and '?' not in info:
            info = '?' + info
        if '?' in info:
            info = parse.urlsplit(info)
        else:
            return {}
    if isinstance(info, (parse.ParseResult, parse.SplitResult, UrlObj)):
        return parse.parse_qs(info.query)
    else:
        raise AttributeError('Unknown information passed to make QS:  {}'.format(repr(info)))

def make_list(data, merge_data=None, unique=False):
    if not data:
        data = []
    if not isinstance(data, (list, tuple)):
        if not isinstance(data, str):
            data = list(data)
        else:
            data = [data]
    if merge_data:
        merge_data = make_list(merge_data, unique=unique)
        data.extend(merge_data)
    if unique:
        data = list(set(data))
    return data

def merge_queries(passed_info, template_info=None, as_str=False):
    passed_info = make_qs_dict(passed_info)
    template_info = make_qs_dict(template_info)
    passed_info = passed_info.copy()
    template_info.update(passed_info)

    if as_str:
        return parse.urlencode(template_info, doseq=True)
    return template_info


