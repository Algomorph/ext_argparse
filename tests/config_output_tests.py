import os
from io import StringIO
from pathlib import Path

from tests.common import HouseParameters, HouseStyle, RoofMaterial, test_data_dir

from ext_argparse import process_arguments, save_defaults, dump, add_comments_from_help, process_settings_file


def test_process_settings_file_with_generate_defaults(test_data_dir):
    output_settings_path = os.path.join(test_data_dir, "enum_setting_defaults3.yaml")
    process_settings_file(HouseParameters, output_settings_path, generate_default_settings_if_missing=True)
    assert HouseParameters.sturdiness.value == 5.0
    assert HouseParameters.year_built.value == 2000
    assert HouseParameters.roof.year_changed.value == 2010
    assert HouseParameters.style.value == HouseStyle.CRAFTSMAN_BUNGALO
    assert HouseParameters.roof.roof_material.value == RoofMaterial.SLATE


def test_save_defaults(test_data_dir):
    output_settings_path = os.path.join(test_data_dir, "enum_setting_defaults.yaml")
    if os.path.exists(output_settings_path):
        to_remove = Path(output_settings_path)
        to_remove.unlink()

    save_defaults(HouseParameters, output_settings_path, save_help_comments=False)

    HouseParameters.sturdiness.argument = 10.0
    HouseParameters.year_built.argument = 2002

    process_arguments(HouseParameters, "Parameters of the house to repair.", argv=[
        f"--settings_file={output_settings_path}"])

    assert HouseParameters.sturdiness.value == 5.0
    assert HouseParameters.year_built.value == 2000
    assert HouseParameters.roof.year_changed.value == 2010
    assert HouseParameters.style.value == HouseStyle.CRAFTSMAN_BUNGALO
    assert HouseParameters.roof.roof_material.value == RoofMaterial.SLATE

    with open(output_settings_path, 'r') as file:
        lines = file.readlines()
        # make sure we're actually reading from the file, not coming up with default settings
        assert len(lines) == 6
        assert lines[5] == "style: CRAFTSMAN_BUNGALO\n"


def test_save_defaults_with_comments(test_data_dir):
    output_settings_path = os.path.join(test_data_dir, "enum_setting_defaults_with_comments.yaml")
    if os.path.exists(output_settings_path):
        to_remove = Path(output_settings_path)
        to_remove.unlink()

    save_defaults(HouseParameters, output_settings_path, save_help_comments=True, line_length_limit=100)

    HouseParameters.sturdiness.argument = 12.0
    HouseParameters.year_built.argument = 2003

    process_arguments(HouseParameters, "Parameters of the house to repair.", argv=[
        f"--settings_file={output_settings_path}"])

    assert HouseParameters.sturdiness.value == 5.0
    assert HouseParameters.year_built.value == 2000
    assert HouseParameters.roof.year_changed.value == 2010
    assert HouseParameters.style.value == HouseStyle.CRAFTSMAN_BUNGALO
    assert HouseParameters.roof.roof_material.value == RoofMaterial.SLATE

    with open(output_settings_path, 'r') as file:
        lines = file.readlines()
        # make sure we're actually reading from the file, not coming up with default settings
        assert lines[0] == "# Sturdiness of the house.\n"
        assert lines[5] == "    # The last year when the roof tiles were changed.\n"
        assert lines[12] == "# 'NEOCLASSICAL', 'MEDITERRANEAN']\n"


def test_add_comments_from_help(test_data_dir):
    output_settings_path = os.path.join(test_data_dir, "enum_setting_defaults_with_comments.yaml")
    if os.path.exists(output_settings_path):
        to_remove = Path(output_settings_path)
        to_remove.unlink()
    save_defaults(HouseParameters, output_settings_path, save_help_comments=False)
    add_comments_from_help(HouseParameters, Path(output_settings_path), line_length_limit=100)
    with open(output_settings_path, 'r') as file:
        lines = file.readlines()
        # make sure we're actually reading from the file, not coming up with default settings
        assert lines[0] == "# Sturdiness of the house.\n"
        assert lines[5] == "    # The last year when the roof tiles were changed.\n"
        assert lines[12] == "# 'NEOCLASSICAL', 'MEDITERRANEAN']\n"


def test_dump_parameters():
    process_arguments(HouseParameters, "Parameters of the house to repair.", argv=[
        "--sturdiness=6.0",
        "--year_built=2001",
        "--roof.year_changed=2012",
        "--style=CONTEMPORARY",
        "--roof.roof_material=SOLAR"
    ])

    string_stream = StringIO()
    dump(HouseParameters, string_stream)

    ground_truth_lines = [
        "sturdiness: 6.0",
        "year_built: 2001",
        "roof:",
        "    year_changed: 2012",
        "    roof_material: SOLAR",
        "style: CONTEMPORARY",
        ""]
    ground_truth_string = '\n'.join(ground_truth_lines)
    output_string = string_stream.getvalue()

    assert output_string == ground_truth_string


def test_dump_parameters_with_comments():
    process_arguments(HouseParameters, "Parameters of the house to repair.", argv=[
        "--sturdiness=6.0",
        "--year_built=2001",
        "--roof.year_changed=2012",
        "--style=CONTEMPORARY",
        "--roof.roof_material=SOLAR"
    ])

    string_stream = StringIO()
    dump(HouseParameters, string_stream, save_help_comments=True, line_length_limit=100)

    ground_truth_lines = [
        "# Sturdiness of the house.",
        "sturdiness: 6.0",
        "# The year the house was built.",
        "year_built: 2001",
        "roof:",
        "    # The last year when the roof tiles were changed.",
        "    year_changed: 2012",
        "    # Material of the roof tiles.| Can be set to one of: ['SLATE', 'METAL', 'CONCRETE', 'COMPOSITE',",
        "    # 'SOLAR', 'CLAY', 'SYNTHETIC_BARREL', 'SYNTHETIC_SLATE', 'SYNTHETIC_CEDAR']",
        "    roof_material: SOLAR",
        "# Style of da house.| Can be set to one of: ['CRAFTSMAN_BUNGALO', 'CAPE_COD', 'RANCH', 'CONTEMPORARY',",
        "# 'QUEEN_ANNE', 'COLONIAL_REVIVAL', 'TUDOR_REVIVAL', 'TOWNHOUSE', 'PRAIRIE', 'MID_CENTURY_MODERN',",
        "# 'NEOCLASSICAL', 'MEDITERRANEAN']",
        "style: CONTEMPORARY",
        ""
    ]

    ground_truth_string = '\n'.join(ground_truth_lines)
    output_string = string_stream.getvalue()

    assert output_string == ground_truth_string
