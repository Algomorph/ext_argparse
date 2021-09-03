import typing

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


class HouseStyle(Enum):
    CRAFTSMAN_BUNGALO = 0
    CAPE_COD = 1
    RANCH = 2
    CONTEMPORARY = 3
    QUEEN_ANNE = 4
    COLONIAL_REVIVAL = 5
    TUDOR_REVIVAL = 6
    TOWNHOUSE = 7
    PRAIRIE = 8
    MID_CENTURY_MODERN = 9
    NEOCLASSICAL = 10
    MEDITERRANEAN = 11


class HouseRoofSettings(ParameterEnum):
    year_changed = Parameter(arg_type=int, default=2010, arg_help="The last year when the roof tiles were changed.")
    roof_material: typing.Type[RoofMaterial] = Parameter(arg_type=RoofMaterial, default=RoofMaterial.SLATE,
                                                         arg_help="Material of the roof tiles.")


class HouseParameters(ParameterEnum):
    sturdiness = Parameter(arg_type=float, default=5.0, arg_help="Sturdiness of the house.", shorthand="stu")
    year_built = Parameter(arg_type=int, default=2000, arg_help="The year the house was built.")
    roof: typing.Type[HouseRoofSettings] = HouseRoofSettings
    style = Parameter(arg_type=HouseStyle, default=HouseStyle.CRAFTSMAN_BUNGALO, arg_help="Style of da house.",
                      shorthand="sty")


def test_default_parameters():
    process_arguments(HouseParameters, "Parameters of the house to repair.", [])

    assert HouseParameters.sturdiness.value == 5.0
    assert HouseParameters.year_built.value == 2000
    assert HouseParameters.roof.year_changed.value == 2010
    assert HouseParameters.style.value == HouseStyle.CRAFTSMAN_BUNGALO
    assert HouseParameters.roof.roof_material.value == RoofMaterial.SLATE
