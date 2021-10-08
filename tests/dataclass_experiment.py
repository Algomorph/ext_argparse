import sys
from dataclasses import dataclass, field, MISSING

# Warning: this is experimental code only!
# Experimenting -- for future API using dataclasses instead of a custom Enum extension

from ext_argparse.param_enum import ParameterEnum

PROGRAM_EXIT_SUCCESS = 0


def parameter(help: str, default=MISSING, default_factory=MISSING, repr=True, hash=None, init=True, compare=True,
              metadata=None):
    return field(default=default, default_factory=default_factory, repr=repr, hash=hash, init=init, compare=compare,
                 metadata={"help": help})


@dataclass
class ParameterCollection:
    pass  # here go methods that exploit the Field metadata, potentially a __post_init__ method as well


@dataclass
class DreamsAndWishes:
    dream_car: str = "Tesla"
    dream_house: str = "castle in the sky"
    dream_spouse: str = "Kristina"
    dream_child: str = "another hedgehog"


@dataclass
class HedgehogParameters(ParameterCollection):
    name: str
    needle_count: int = 0
    dreams_and_wishes: DreamsAndWishes = DreamsAndWishes


def main():
    print(HedgehogParameters.dreams_and_wishes.dream_car)

    return PROGRAM_EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
