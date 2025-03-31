
from helpers import config, today, SelectMethods
from collections import deque


class _Use():
    def __init__(self, t, count=None):
        self.date = t
        self.expires = self.date + config.max_recent_days
        self.count = count or 1

    def add(self, inc_by=1):
        self.count += inc_by

    def __int__(self):
        return self.count

    def __bool__(self):
        return self.expires > today()

class RecentUses():
    """
    ru = RecentUses()
    ru.add()

    check list for overdue entries and remove
    add item to list
    recalc list.

    """
    def __init__(self):
        self.total = 0
        self._uses = {}

    def add(self):
        self.clean()

        t = today()

        if today in self._uses:
            self._uses[t].add()
        else:
            self._uses[t] = _Use(t)
        self.total += 1

    def clean(self):
        for d, u in self._uses.items():
            if u:
                self.total -= u.count
                del self._uses[d]

    def __int__(self):
        return self.total

    def get_data(self):
        data_obj = []
        for x in self._uses.values():
            data_obj.append(
                {'date': x.date, 'count': x.count}
            )
        return data_obj
    
    def load_data(self, data_obj:dict):
        local_data = data_obj.get('recent_uses', [])
        for x in local_data:
            self._uses[x['date']] = _Use(x['date'], x['count'])


class _Edit():
    def __init__(self, user, date=None):
        self.user = user
        self.date = date or today()

class LastXEdits():
    """
    le = LastXEdits()
    le.add(user)
    """
    def __init__(self):
        self.queue = deque([], config.max_last_x)

    def add(self, user):
        self.queue.append(_Edit(user))

    def get_data(self):
        data_obj = []
        for x in self.queue:
            data_obj.append(
                {'user': x.user, 'date': x.date}
            )
        return data_obj

    def load_data(self, data_obj: dict):
        local_data = data_obj.get('last_x_edits', [])
        for x in local_data:
            self.queue.append(_Edit(x['user'], x['date']))


class ListOfLinks():
    """ used to store lists of links"""
    pass

class ListOfKeys():
    pass


class BaseRecord(object):
    """
    handles all of the base record functions

    last_x_edits: = list of edit records that is x long
    recent_uses = contains

    """
    last_x_edits = LastXEdits()
    recent_uses = RecentUses()
    start_date = None
    end_date = None
    active = True
    created_date = None

    def __init__(self, **kwargs):
        if kwargs:
            self.load_data(kwargs)
        if self.created_date is None:
            self.created_date = today()

    def load_data(self, data_obj:dict=None):
        """
        create bew object from data file
        """
        if data_obj is None:
            data_obj = {}
        self.active = data_obj.get('active', True)
        self.start_date = data_obj.get('start_date', None)
        self.end_date = data_obj.get('end_date', None)
        self.last_x_edits.load_data(data_obj)
        self.recent_uses.load_data(data_obj)

    def get_data(self):
        """
        generate dict for saving.
        """
        data_obj = {}
        data_obj['last_x_edits'] = self.last_x_edits.get_data()
        data_obj['recent_uses'] = self.recent_uses.get_data()
        return data_obj

    def count_edit(self, user):
        self.last_x_edits.add(user)

    def count_use(self):
        self.recent_uses.add()

    def last_edits(self):
        return self.last_x_edits.queue

    def total_uses(self):
        return self.recent_uses.total


class BaseKeyRecord(BaseRecord):
    key_type = 'normal'
    pass

class KeyRecord(BaseKeyRecord):
    """Used to store a single key (lookup) record"""
    Keyword = None
    select_method = None
    children = None
    links = None

    def __init__(self, **kwargs):
        self.children = ListOfKeys()
        self.links = ListOfLinks()
        super().__init__(**kwargs)

    def load_data(self, data_obj:dict):
        super().__init__(data_obj)
        self.Keyword = data_obj.get('Keyword', self.keyword)
        self.select_method = data_obj.get('select_method', self.select_method)
        if 'children' in data_obj:
            self.children.load_data(data_obj['children'])
        if 'links' in data_obj:
            self.links.load_data(data_obj['links'])

    def set_select_method(self, method):
        if not isinstance(method, SelectMethods):

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
    priority = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url = kwargs.get('url', None)
        self.modify_path = kwargs.get('modify_path', None)
        self.modify_query = kwargs.get('modify_query', None)
        self.priority = kwargs.get('priority', 0)

