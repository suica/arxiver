import json
import datetime
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.orm.dynamic import AppenderQuery


class Serializable():
    _dict_fields = []

    def to_dict(self):
        dic = {}
        for k in self._dict_fields:
            v = self.__getattribute__(k)
            if isinstance(v,datetime.datetime):
                v = v.isoformat()
            elif isinstance(v, (InstrumentedList)):
                v = list(v)
            elif isinstance(v, AppenderQuery):
                v = v.all()
            dic[k] = v
        return dic


def hack(self, o):
    if isinstance(o, Serializable):
        return o.to_dict()
    return str(type(o))


json.JSONEncoder.default = hack
