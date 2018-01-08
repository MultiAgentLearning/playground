from a import db
from collections import OrderedDict
import datetime
from flask import abort
from sqlalchemy import Column, DateTime, Text
from a.utils import sql


def camel_case(snake_str):
    parts = snake_str.split('_')
    return parts[0] + ''.join([p.title() for p in parts[1:]])


class DictSerializableMixin(object):
    include_keys = None

    def serialize(self):
        excluded_keys = ['password', 'id', 'created_at', 'updated_at']
        result = OrderedDict()
        include_keys = self.include_keys or self.__mapper__.c.keys()
        for key in include_keys:
            if key not in excluded_keys:
                result[camel_case(key)] = getattr(self, key)
        return result


class SlugMixin(object):
    slug = Column(Text, index=True)

    def set_slug(self, name=None):
        name = name.replace(',', '')
        name = '-'.join(name.lower().split(' '))
        count = self.__class__.query.filter_by(name=name).count()
        if count:
            slug += '-%d' % count
        self.slug = slug


class TimeMixin(object):
    created_at = Column(DateTime,
                        default=datetime.datetime.utcnow)
    updated_at = Column(DateTime,
                        default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)


class AttrsMixin(object):
    @sql.commit_decorator
    def setattr(self, **kwargs):
        for k,v in kwargs.iteritems():
            if hasattr(self, k):
                setattr(self, k, v)

    def getattr(self, k):
        if hasattr(self, k):
            return getattr(self, k)
        return None


class BaseModelMixin(TimeMixin, DictSerializableMixin, AttrsMixin):
    _repr_hide = ['created_at', 'updated_at']

    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_by(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def get_or_404(cls, id):
        rv = cls.get(id)
        if rv is None:
            abort(404)
        return rv

    @classmethod
    def get_or_create(cls, **kwargs):
        r = cls.get_by(**kwargs)
        if not r:
            return cls.create(**kwargs), True
        return r, False

    @classmethod
    def create(cls, **kwargs):
        r = cls(**kwargs)
        db.session.add(r)
        db.session.commit()
        return r

    def save(self):
        db.session.add(self)

    def delete(self):
        db.session.delete(self)

    def __repr__(self):
        values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in
                           self.__table__.c.keys() if n not in self._repr_hide)
        return "%s(%s)" % (self.__class__.__name__, values)

