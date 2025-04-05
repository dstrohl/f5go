
from collections import deque

from prog.bases import BaseKeyRecord, BaseRecord, BaseGetLoadObj
from prog.helpers import SelectMethods
from prog.config import config


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
        self.select_method = select_method or SelectMethods().PRIORITY
        self.add_edit(user)

    def add_link(self):

    def rem_link(self):




    def _load_data(self, data_obj:dict):
        super().__init__(data_obj)
        self.Keyword = data_obj.get('Keyword', self.keyword)
        self.select_method = data_obj.get('select_method', self.select_method)
        if 'children' in data_obj:
            self.children.load_data(data_obj['children'])
        if 'links' in data_obj:
            self.links.load_data(data_obj['links'])

    def set_select_method(self, method):
        if not isinstance(method, SelectMethods):
            method = SelectMethods(method)
        self.select_method = method


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
    url = None
    modify_path = None
    modify_query = None
    modify_error_url = None
    modify_error_text = None
    priority = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url = kwargs.get('url', None)
        self.modify_path = kwargs.get('modify_path', None)
        self.modify_query = kwargs.get('modify_query', None)
        self.modify_error_url = kwargs.get('modify_error_url', None)
        self.priority = kwargs.get('priority', 0)

    def update(self):

    def get_url(self):

    def is_generative(self):


    def __len__(self):

