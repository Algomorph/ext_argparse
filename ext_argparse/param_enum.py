from enum import Enum, EnumMeta, _EnumDict
from types import DynamicClassAttribute

EnumMetaFeta = type("EnumMetaFeta", (), dict(EnumMeta.__dict__))


class NestedEnumMeta(EnumMeta):
    @classmethod
    def __prepare__(metacls, cls, bases):
        # check that previous enum members do not exist
        EnumMeta._check_for_existing_members(cls, bases)
        # create the namespace dict
        enum_dict = _EnumDict()
        enum_dict._cls_name = cls
        # inherit previous flags and _generate_next_value_ function
        member_type, first_enum = EnumMeta._get_mixins_(cls, bases)
        if first_enum is not None:
            enum_dict['_generate_next_value_'] = getattr(
                first_enum, '_generate_next_value_', None,
            )
        return enum_dict

    def __new__(metacls, cls, bases, classdict):
        enum_class = super().__new__(metacls, cls, bases, classdict)
        member_type, first_enum = metacls._get_mixins_(cls, bases)
        __new__, save_new, use_args = metacls._find_new_(
            classdict, member_type, first_enum,
        )
        nested_enum_members = []
        setattr(enum_class, "_full_member_map_", {})

        for key, member in enum_class._member_map_.items():
            if isinstance(member.parameter, NestedEnumMeta):
                nested_enum_members.append((key, member))
            else:
                member.argument = None
            enum_class._full_member_map_[key] = member

        for key, member in nested_enum_members:
            del enum_class._member_map_[key]
            delattr(enum_class, key)
            setattr(enum_class, key, member.parameter)
            enum_class._member_map_[key] = member.parameter
        return enum_class

    def __iter__(cls):
        """
        Returns members in definition order.
        """
        return (cls._full_member_map_[name] for name in cls._member_names_)

    @property
    def parameter(self):
        return self

    @property
    def type(self):
        return 'parameter_enum'


class ParameterEnum(Enum, metaclass=NestedEnumMeta):
    @property
    def parameter(self):
        return super().value

    @property
    def value(self):
        return self.argument
