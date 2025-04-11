from typing import Any

from prog.helpers import today
from prog.config import config, log
from collections import deque
from copy import copy
from prog.constants import *

class BaseGetLoadObj():

    def __init__(self, load_data=None, load_type=LOAD_TYPE_NEW, **kwargs):
        if kwargs:
            self.load_data(kwargs, load_type=load_type)

    def get_data(self):
        log.debug('getting data from %r', self)
        tmp_ret = self._get_data()
        log.debug('    data: %r', tmp_ret)
        return tmp_ret

    def _get_data(self):
        raise NotImplementedError()

    def load_data(self, data_obj, load_type=LOAD_TYPE_UPDATE):
        log.debug('loading data %s into class %s', load_type, self.__class__.__name__)
        log.debug('    data: %r', data_obj)
        self._load_data(data_obj, load_type=load_type)
        return

    def _load_data(self, data_obj:dict, load_type=LOAD_TYPE_UPDATE):
        raise NotImplementedError()



class RecentUses(BaseGetLoadObj):

    last_cleaned_date = None
    lifetime = 0

    def __init__(self, load_data=None, **kwargs):
        self.total = 0
        self.uses = {}
        super(RecentUses, self).__init__(load_data=load_data, **kwargs)

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
        self.lifetime += 1

    def clear(self):
        self.total = 0
        self.uses.clear()
        self.lifetime = 0
        self.last_cleaned_date = None

    def __int__(self):
        return self.total

    def _get_data(self):
        tmp_ret = dict(
            data=self.uses.copy(),
            lifetime=self.lifetime,
        )
        return tmp_ret

    def _load_data(self, data_obj:dict, load_type=LOAD_TYPE_NEW, t=None):
        # super(RecentUses, self)._load_data(data_obj, load_type=load_type)
        self.lifetime = data_obj.get('lifetime', self.lifetime)
        data_obj = data_obj.get('data', {})
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

    def _load_data(self, data_obj: list, load_type=LOAD_TYPE_NEW, t=None):
        # super(LastXEdits, self)._load_data(data_obj, load_type=load_type)
        data_obj.sort(key=lambda x: x[1], reverse=False)
        self.queue.extend(data_obj)
        self.last_edit_date = data_obj[-1][1]
        self.last_edit_user = data_obj[-1][0]

    def clear(self):
        self._queue.clear()
        self.last_edit_date = 0
        self.last_edit_user = ''

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

    def __init__(self, load_data=None, load_type=LOAD_TYPE_NEW, **kwargs):
        super(BaseRecord, self).__init__(load_data=load_data, load_type=load_type, **kwargs)

    def update(self, user=None, load_type=LOAD_TYPE_UPDATE, **kwargs):
        self.load_data(kwargs, load_type=LOAD_TYPE_UPDATE)
        if load_type == LOAD_TYPE_UPDATE and user is not None:
            self.add_edit(user=user)

    def _load_data(self, data_obj:dict=None, load_type=LOAD_TYPE_UPDATE):
        """
        create bew object from data file
        """
        if not data_obj:
            return
        self.active = data_obj.get('active', self.active)
        self.start_date = data_obj.get('start_date', self.start_date)
        self.end_date = data_obj.get('end_date', self.end_date)

        if load_type==LOAD_TYPE_NEW:
            self.created_date = today()
        elif load_type==LOAD_TYPE_IMPORT:
            self.created_date = data_obj.get('created_date')
            self.last_x_edits.load_data(data_obj['last_x_edits'])
            self.recent_uses.load_data(data_obj['recent_uses'])

    def _get_data(self):
        """
        generate dict for saving.
        """
        data_obj = {'active': self.active,
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'created_date': self.created_date,
                    'last_x_edits': self.last_x_edits.get_data(),
                    'recent_uses': self.recent_uses.get_data()}

        return data_obj

    def add_edit(self, user):
        if not user:
            user = config.unknown_user
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

