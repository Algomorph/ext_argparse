from ext_argparse.argproc import process_arguments
from ext_argparse.parameter import Parameter
from ext_argparse.param_enum import ParameterEnum
from enum import Enum


class RoofMaterial(Enum):
    SLATE = 0
    METAL = 1
    CONCRETE = 2
    COMPOSITE = 3
    SOLAR = 4
    CLAY = 5
    SYNTHETIC_BARREL = 6
    SYNTHETIC_SLATE = 7
    SYNTHETIC_CEDAR = 8

class HOUSE_STYLE(Enum):
    CRAFTSMAN_BUNGALO = 0
    # TODO finish


class HouseRoofSettings(ParameterEnum):
    year_changed = Parameter(arg_type=int, default=2010, arg_help="The last year when the roof tiles were changed.")
    roof_material = Parameter(arg_type=RoofMaterial, default=RoofMaterial.SLATE.name,
                              arg_help="Material of the roof tiles.")


class HouseParameters(ParameterEnum):
    sturdiness = Parameter(arg_type=float, default=5.0, arg_help="Sturdiness of the house.")
    year_built = Parameter(arg_type=int, default=2000, arg_help="The year the house was built.")
    roof = HouseRoofSettings

