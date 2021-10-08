import os
import os.path
import pathlib

import pytest

from ext_argparse.argproc import process_arguments

from tests.common import HouseParameters, HouseStyle, RoofMaterial, test_data_dir


def test_default_parameters():
    process_arguments(HouseParameters, "Parameters of the house to repair.", argv=[])

    assert HouseParameters.sturdiness.value == 5.0
    assert HouseParameters.year_built.value == 2000
    assert HouseParameters.roof.year_changed.value == 2010
    assert HouseParameters.style.value == HouseStyle.CRAFTSMAN_BUNGALO
    assert HouseParameters.roof.roof_material.value == RoofMaterial.SLATE


def test_changed_enum_parameters():
    process_arguments(HouseParameters, "Parameters of the house to repair.", argv=[
        "--sturdiness=6.0",
        "--year_built=2001",
        "--roof.year_changed=2012",
        "--style=CONTEMPORARY",
        "--roof.roof_material=SOLAR"
    ])

    assert HouseParameters.sturdiness.value == 6.0
    assert HouseParameters.year_built.value == 2001
    assert HouseParameters.roof.year_changed.value == 2012
    assert HouseParameters.style.value == HouseStyle.CONTEMPORARY
    assert HouseParameters.roof.roof_material.value == RoofMaterial.SOLAR


def test_nested_parameter_save_load(test_data_dir):
    output_settings_path = os.path.join(test_data_dir, "enum_settings.yaml")

    process_arguments(HouseParameters, "Parameters of the house to repair.", argv=[
        f"--settings_file={output_settings_path}"])

    assert HouseParameters.sturdiness.value == 5.0
    assert HouseParameters.year_built.value == 2000
    assert HouseParameters.roof.year_changed.value == 2010
    assert HouseParameters.style.value == HouseStyle.CRAFTSMAN_BUNGALO
    assert HouseParameters.roof.roof_material.value == RoofMaterial.SLATE

    process_arguments(HouseParameters, "Parameters of the house to repair.", argv=[
        f"--settings_file={output_settings_path}",
        "--save_settings",
        "--sturdiness=6.0",
        "--year_built=2001",
        "--roof.year_changed=2012",
        "--style=CONTEMPORARY",
        "--roof.roof_material=SOLAR"
    ])

    assert HouseParameters.sturdiness.value == 6.0
    assert HouseParameters.year_built.value == 2001
    assert HouseParameters.roof.year_changed.value == 2012
    assert HouseParameters.style.value == HouseStyle.CONTEMPORARY
    assert HouseParameters.roof.roof_material.value == RoofMaterial.SOLAR

    # load defaults
    process_arguments(HouseParameters, "Parameters of the house to repair.", argv=[
        "--sturdiness=5.0",
        "--year_built=2000",
        "--roof.year_changed=2010",
        "--style=CRAFTSMAN_BUNGALO",
        "--roof.roof_material=SLATE"
    ])

    assert HouseParameters.sturdiness.value == 5.0
    assert HouseParameters.year_built.value == 2000
    assert HouseParameters.roof.year_changed.value == 2010
    assert HouseParameters.style.value == HouseStyle.CRAFTSMAN_BUNGALO
    assert HouseParameters.roof.roof_material.value == RoofMaterial.SLATE

    process_arguments(HouseParameters, "Parameters of the house to repair.", argv=[
        f"--settings_file={output_settings_path}"])

    # verify loaded settings were altered from default
    assert HouseParameters.sturdiness.value == 6.0
    assert HouseParameters.year_built.value == 2001
    assert HouseParameters.roof.year_changed.value == 2012
    assert HouseParameters.style.value == HouseStyle.CONTEMPORARY
    assert HouseParameters.roof.roof_material.value == RoofMaterial.SOLAR

    # save defaults now
    process_arguments(HouseParameters, "Parameters of the house to repair.", argv=[
        f"--settings_file={output_settings_path}",
        "--save_settings",
        "--sturdiness=5.0",
        "--year_built=2000",
        "--roof.year_changed=2010",
        "--style=CRAFTSMAN_BUNGALO",
        "--roof.roof_material=SLATE"
    ])

    assert HouseParameters.sturdiness.value == 5.0
    assert HouseParameters.year_built.value == 2000
    assert HouseParameters.roof.year_changed.value == 2010
    assert HouseParameters.style.value == HouseStyle.CRAFTSMAN_BUNGALO
    assert HouseParameters.roof.roof_material.value == RoofMaterial.SLATE
