
from prog.helpers import today
from prog.config import config, log
from collections import deque
from copy import copy
"""
class _Use():
    def __init__(self, t, count=None):
        self.date = t
        self.expires = self.date + config.max_recent_days
        self.count = count or 1

    def add(self, inc_by=1):
        self.count += inc_by

    def exp(self, t=None):
        t = t or today()
        return self.expires > t

    def __int__(self):
        return self.count

    def __bool__(self):
        return self.exp()
"""

class BaseGetLoadObj():

    default_get_obj = dict()

    def __init__(self, load_data=None, **kwargs):
        if load_data:
            self.load_data(load_data)

    def get_data(self):
        log.debug('getting data from %r', self)
        tmp_ret = self._get_data()
        log.debug('    data: %r', tmp_ret)
        if tmp_ret is None:
            return copy(self.default_get_obj)
        return tmp_ret

    def _get_data(self):
        return None

    def load_data(self, data_obj):
        log.debug('loading data into class %s', self.__class__.__name__)
        log.debug('    data: %r', data_obj)
        self._load_data(data_obj)
        return

    def _load_data(self, data_obj):
        pass


class RecentUses(BaseGetLoadObj):
    """
    ru = RecentUses()
    ru.add()

    check list for overdue entries and remove
    add item to list
    recalc list.

    """

    last_cleaned_date = None
    default_get_obj = list()

    def __init__(self, load_data=None, **kwargs):
        super(RecentUses, self).__init__(load_data=load_data, **kwargs)
        if load_data:
            return
        self.total = 0
        self.uses = {}

    # TODO: fix cleanup to work better... probably change to straight dict and store last cleaned day.

    def add(self, t=None):
        t = t or today()

        if t != self.last_cleaned_date:
            self.last_cleaned_date = t
            e = t-config.max_recent_days + 1
            for d, v in list(self.uses.items()):
                if d < e:
                    self.total -= v
                    del self.uses[d]

        if t in self.uses:
            self.uses[t] += 1
        else:
            self.uses[t] = 1
        self.total += 1

    def __int__(self):
        return self.total

    def _get_data(self):
        return self.uses.copy()

    def _load_data(self, data_obj:dict, t=None):
        self.uses.clear()
        t = t or today()
        e = t - config.max_recent_days + 1
        self.last_cleaned_date = t

        for d, v in data_obj.items():
            if d >= e:
                self.uses[d] = v
                self.total += v
        self.last_cleaned_date = t

    def __len__(self):
        return len(self.uses)

"""
class _Edit():
    def __init__(self, user, date=None):
        self.user = user
        self.date = date or today()
"""

class LastXEdits(BaseGetLoadObj):
    """
    le = LastXEdits()
    le.add(user)

    stored user, date
    """

    _queue = None
    last_edit_date = 0
    last_edit_user = ''


    def __init__(self, load_data=None, **kwargs):
        super(LastXEdits, self).__init__(load_data=load_data, **kwargs)
        if load_data:
            return

    @property
    def queue(self):
        if self._queue is None:
            self._queue = deque([], config.max_last_x)
        return self._queue

    def add(self, user, t=None):
        t = t or today()
        self.last_edit_user = user
        self.last_edit_date = t
        self.queue.append((user, t))

    def _get_data(self):
        data_obj = list(self.queue)
        return data_obj

    def _load_data(self, data_obj: list):
        data_obj.sort(key=lambda x: x[1], reverse=False)
        self.queue.extend(data_obj)
        self.last_edit_date = data_obj[-1][1]
        self.last_edit_user = data_obj[-1][0]

    def __len__(self):
        return len(self.queue)

class BaseRecord(BaseGetLoadObj):
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
    rec_id = None

    def __init__(self, load_data=None, **kwargs):
        super(BaseRecord, self).__init__(load_data=load_data, **kwargs)
        if load_data:
            return
        self.created_date = today()


    def _load_data(self, data_obj:dict=None):
        """
        create bew object from data file
        """
        if data_obj is None:
            return
        self.active = data_obj.get('active', True)
        self.start_date = data_obj.get('start_date', None)
        self.end_date = data_obj.get('end_date', None)
        self.created_date = data_obj.get('created_date', None)
        self.last_x_edits.load_data(data_obj['last_x_edits'])
        self.recent_uses.load_data(data_obj['recent_uses'])

    def _get_data(self):
        """
        generate dict for saving.
        """
        data_obj = {}

        data_obj['active'] = self.active
        data_obj['start_date'] = self.start_date
        data_obj['end_date'] = self.end_date
        data_obj['created_date'] = self.created_date

        data_obj['last_x_edits'] = self.last_x_edits.get_data()
        data_obj['recent_uses'] = self.recent_uses.get_data()
        return data_obj

    def add_edit(self, user):
        self.last_x_edits.add(user)

    def add_use(self):
        self.recent_uses.add()

    def last_edits(self):
        return self.last_x_edits.queue

    @property
    def total_uses(self):
        return self.recent_uses.total

    @property
    def last_edit_date(self):
        return self.last_x_edits.last_edit_date

    @property
    def last_edit_name(self):
        return self.last_x_edits.last_edit_name



class BaseKeyRecord(BaseRecord):
    key_type = 'normal'

    def __init__(self, load_data=None, **kwargs):
        super(BaseKeyRecord, self).__init__(load_data, **kwargs)

