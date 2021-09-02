from enum import Enum
from ext_argparse.parameter import Parameter


# class classproperty(property):
#     def __get__(self, cls, owner):
#         return classmethod(self.fget).__get__(None, owner)()


class ParameterEnum(Enum):
    @staticmethod
    def get_type():
        return 'parameter_enum'

    @property
    def parameter(self):
        return super().value

    @property
    def value(self):
        return self.argument
