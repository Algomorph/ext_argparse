import os
import pathlib

import pytest
from ext_argparse.parameter import Parameter
from ext_argparse.param_enum import ParameterEnum
from ext_argparse.argproc import process_arguments


class LevelTwoGroupA(ParameterEnum):
    string_param = Parameter(arg_type=str, default="Istanbul", arg_help="Point of origin")
    int_param = Parameter(arg_type=int, default=8, arg_help="Number of hairs on chest")
    float_param = Parameter(arg_type=float, default=0.1, arg_help="Litres of vodka left to drink")


class LevelTwoGroupB(ParameterEnum):
    string_param = Parameter(arg_type=str, default="Kabul", arg_help="Point of origin")
    int_param = Parameter(arg_type=int, default=8, arg_help="Number of hairs on chest")
    float_param = Parameter(arg_type=float, default=0.1, arg_help="Litres of vodka left to drink")


class LevelTwoGroupC(ParameterEnum):
    string_param = Parameter(arg_type=str, default="Istanbul", arg_help="Point of origin")
    int_param = Parameter(arg_type=int, default=8, arg_help="Number of hairs on chest")
    float_param = Parameter(arg_type=float, default=0.1, arg_help="Litres of vodka left to drink")
    path_param = Parameter(arg_type=str, default=".", arg_help="Some path", setting_file_location=True)


class LevelOneGroupD(ParameterEnum):
    int_param = Parameter(arg_type=int, default=5, arg_help="Number of hairs on chest")
    group_a = LevelTwoGroupA
    group_b = LevelTwoGroupB
    group_c = LevelTwoGroupC


class LevelOneGroupA(ParameterEnum):
    string_param = Parameter(arg_type=str, default="Istanbul", arg_help="Point of origin")
    int_param = Parameter(arg_type=int, default=8, arg_help="Number of hairs on chest")
    float_param = Parameter(arg_type=float, default=0.1, arg_help="Litres of vodka left to drink")


class LevelOneGroupB(ParameterEnum):
    string_param = Parameter(arg_type=str, default="Istanbul", arg_help="Point of origin")
    int_param = Parameter(arg_type=int, default=8, arg_help="Number of hairs on chest")
    float_param = Parameter(arg_type=float, default=0.1, arg_help="Litres of vodka left to drink")


class LevelOneGroupC(ParameterEnum):
    string_param = Parameter(arg_type=str, default="Istanbul", arg_help="Point of origin")
    int_param = Parameter(arg_type=int, default=9, arg_help="Number of hairs on chest")
    float_param = Parameter(arg_type=float, default=0.1, arg_help="Litres of vodka left to drink")


class BaseLevelParams(ParameterEnum):
    string_param = Parameter(arg_type=str, default="Istanbul", arg_help="Point of origin")
    int_param = Parameter(arg_type=int, default=8, arg_help="Number of hairs on chest")

    group_a = LevelOneGroupA
    group_b = LevelOneGroupB
    group_c = LevelOneGroupC

    float_param = Parameter(arg_type=float, default=0.1, arg_help="Litres of coolaid left to drink")

    group_d = LevelOneGroupD


def test_default_nested_parameters():
    process_arguments(BaseLevelParams, "Test parameter parser", [])
    assert BaseLevelParams.float_param.value == 0.1
    assert BaseLevelParams.group_a.parameter.float_param.value == 0.1
    assert BaseLevelParams.group_c.parameter.int_param.value == 9
    assert BaseLevelParams.group_d.parameter.int_param.value == 5
    assert BaseLevelParams.group_d.parameter.group_a.parameter.float_param.value == 0.1
    assert BaseLevelParams.group_d.parameter.group_b.parameter.string_param.value == "Kabul"


def test_full_nested_parameters():
    process_arguments(BaseLevelParams, "Test parameter parser", [
        "--float_param=0.2",
        "--int_param=1",
        "--group_a.float_param=0.4",
        "--group_c.string_param=Constantinople",
        "--group_d.int_param=9",
        "--group_d.group_a.float_param=0.32",
        "--group_d.group_b.string_param=Liverpool"
    ])
    assert BaseLevelParams.float_param.value == 0.2
    assert BaseLevelParams.int_param.value == 1
    assert BaseLevelParams.group_a.parameter.float_param.value == 0.4
    assert BaseLevelParams.group_c.parameter.string_param.value == "Constantinople"
    assert BaseLevelParams.group_d.parameter.int_param.value == 9
    assert BaseLevelParams.group_d.parameter.group_a.parameter.float_param.value == 0.32
    assert BaseLevelParams.group_d.parameter.group_b.parameter.string_param.value == "Liverpool"


def test_shorthand_nested_parameters():
    process_arguments(BaseLevelParams, "Test parameter parser", [
        "-fp=0.2",
        "-ip=1",
        "-ga.fp=0.4",
        "-gc.sp=Constantinople",
        "-gd.ip=9",
        "-gd.ga.fp=0.32",
        "-gd.gb.sp=Liverpool"
    ])
    assert BaseLevelParams.float_param.value == 0.2
    assert BaseLevelParams.int_param.value == 1
    assert BaseLevelParams.group_a.parameter.float_param.value == 0.4
    assert BaseLevelParams.group_c.parameter.string_param.value == "Constantinople"
    assert BaseLevelParams.group_d.parameter.int_param.value == 9
    assert BaseLevelParams.group_d.parameter.group_a.parameter.float_param.value == 0.32
    assert BaseLevelParams.group_d.parameter.group_b.parameter.string_param.value == "Liverpool"


def test_nested_parameter_save_load():
    test_data_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), "test_data")
    output_settings_path = os.path.join(test_data_dir, "nested_settings.yaml")
    process_arguments(BaseLevelParams, "Test parameter parser", [
        f"--settings_file={output_settings_path}",
        "--save_settings",
        "--float_param=0.2",
        "--int_param=1",
        "--group_a.float_param=0.4",
        "--group_c.string_param=Constantinople",
        "--group_d.int_param=9",
        "--group_d.group_a.float_param=0.32",
        "--group_d.group_b.string_param=Liverpool",
        "--group_d.group_c.path_param=!settings_file_location"
    ])
    assert BaseLevelParams.float_param.value == 0.2
    assert BaseLevelParams.int_param.value == 1
    assert BaseLevelParams.group_a.parameter.float_param.value == 0.4
    assert BaseLevelParams.group_c.parameter.string_param.value == "Constantinople"
    assert BaseLevelParams.group_d.parameter.int_param.value == 9
    assert BaseLevelParams.group_d.parameter.group_a.parameter.float_param.value == 0.32
    assert BaseLevelParams.group_d.parameter.group_b.parameter.string_param.value == "Liverpool"
    assert BaseLevelParams.group_d.parameter.group_c.parameter.path_param.value == test_data_dir

    # load defaults
    process_arguments(BaseLevelParams, "Test parameter parser", [])
    assert BaseLevelParams.group_d.parameter.group_c.parameter.path_param.value == "."

    process_arguments(BaseLevelParams, "Test parameter parser", [
        f"--settings_file={output_settings_path}",
        "--int_param=2"
    ])

    assert BaseLevelParams.int_param.value == 2
    assert BaseLevelParams.group_d.parameter.group_c.parameter.path_param.value == test_data_dir

    # test that settings file was not overwritten
    process_arguments(BaseLevelParams, "Test parameter parser", [
        f"--settings_file={output_settings_path}"
    ])
    assert BaseLevelParams.int_param.value == 1


