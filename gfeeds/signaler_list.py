from gi.repository import GObject


class SignalerList(GObject.Object):
    __gsignals__ = {
        'append': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,)
        ),
        'extend': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,)
        ),
        'pop': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,)
        ),
        'empty': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (str,)
        )
    }

    def __init__(self, n_list=None, **kwargs):
        if n_list is None:
            n_list = []
        super().__init__(**kwargs)
        self.__list = n_list.copy()

    # Note: you see all those "item" names?
    # Don't be confused, they don't refer to FeedItem objects
    # It's item as in "list item"

    def index(self, item):
        return self.__list.index(item)

    def extend(self, ex_list):
        self.__list.extend(ex_list)
        self.emit('extend', ex_list)

    def empty(self):
        self.__list = []
        self.emit('empty', '')

    def append(self, n_item):
        self.__list.append(n_item)
        self.emit('append', n_item)

    def pop(self, item):
        popped = self.__list[item]
        self.__list.pop(item)
        self.emit('pop', popped)
        return popped

    def remove(self, item):
        self.__list.remove(item)
        self.emit('pop', item)
        return item

    def __len__(self):
        return len(self.__list)

    # this also provides iteration and slicing
    def __getitem__(self, item):
        return self.__list[item]

    def __repr__(self):
        return str(type(self)) + self.__list.__repr__()

    def get_list(self):
        return self.__list.copy()
