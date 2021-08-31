from enum import Enum
from ext_argparse.parameter import Parameter


class ParameterEnum(Enum):
    @property
    def parameter(self):
        return super().value

    @property
    def value(self):
        return self.argument
