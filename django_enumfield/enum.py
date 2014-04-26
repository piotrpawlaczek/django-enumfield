import logging
from enum import Enum as BaseEnum, EnumMeta as BaseEnumMeta

from django.utils.translation import ugettext_lazy as _
from django_enumfield.db.fields import EnumField


def translate(name):
    return _(name.replace('_', ' ').lower().title())

logger = logging.getLogger(__name__)


class EnumMeta(BaseEnumMeta):

    def __new__(cls, *args, **kwargs):
        """
        Create enum values from all uppercase class attributes and store them in a dict on the Enum class.
        """
        enum = super(EnumMeta, cls).__new__(cls, *args, **kwargs)
        attributes = filter(lambda (k, v): k.isupper(), enum.__dict__.iteritems())
        enum.values = {}
        for attribute in attributes:
            enum.values[attribute[1]] = enum.Value(attribute[0], attribute[1], enum)
        return enum


class Enum(BaseEnum):
    """
    A container for holding and restoring enum values.
    Usage:
        class BeerStyle(Enum):
            LAGER = 0
            STOUT = 1
            WEISSBIER = 2
    It can also validate enum value transitions by defining the _transitions variable as a dict with transitions.
    """
    __metaclass__ = EnumMeta


    @classmethod
    def choices(cls):
        """
        Returns a list of tuples with the value as first argument and the value container class as second argument.
        """
        return sorted(cls.values.iteritems(), key=lambda x: x[0])

    @classmethod
    def default(cls):
        """
        Returns default value, which is the first one by default.
        Override this method if you need another default value.
        Usage:
            IntegerField(choices=my_enum.choices(), default=my_enum.default(), ...
        """
        return cls.choices()[0][0]

    @classmethod
    def field(cls, **kwargs):
        """
        A shortcut for
        Usage:
            class MyModelStatuses(Enum):
                UNKNOWN = 0
            class MyModel(Model):
                status = MyModelStatuses.field()
        """
        return EnumField(cls, **kwargs)

    @classmethod
    def get(cls, name_or_numeric):
        """
        Will return a Enum.Value matching the value argument.
        """
        if isinstance(name_or_numeric, basestring):
            name_or_numeric = getattr(cls, name_or_numeric.upper())

        return cls.values.get(name_or_numeric)

    @classmethod
    def name(cls, numeric):
        """
        Will return the uppercase name for the matching Enum.Value.
        """
        return cls.get(numeric).name

    @classmethod
    def label(cls, numeric):
        """
        Will return the human readable label for the matching Enum.Value.
        """
        return translate(unicode(cls.get(numeric)))

    @classmethod
    def items(cls):
        """
        Will return a list of tuples consisting of every enum value in the form [('NAME', value), ...]
        """
        items = [(value.name, key) for key, value in cls.values.iteritems()]
        return sorted(items, key=lambda x: x[1])

    @classmethod
    def is_valid_transition(cls, from_value, to_value):
        """
        Will check if to_value is a valid transition from from_value. Returns true if it is a valid transition.
        """
        return from_value == to_value or from_value in cls.transition_origins(to_value)

    @classmethod
    def transition_origins(cls, to_value):
        """
        Returns all values the to_value can make a transition from.
        """
        return cls._transitions[to_value]
