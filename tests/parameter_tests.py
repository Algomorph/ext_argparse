import os
import pathlib

import pytest

from ext_argparse.argproc import process_arguments, dump
from ext_argparse.parameter import Parameter
from ext_argparse.param_enum import ParameterEnum
from io import StringIO


class Parameters(ParameterEnum):
    # optimizer settings
    tikhonov_term_enabled = Parameter(action="store_true", default=False, arg_type='bool_flag')
    gradient_kernel_enabled = Parameter(action="store_true", default=False, arg_type='bool_flag')

    maximum_warp_update_threshold = Parameter(arg_type=float, default=0.01)
    maximum_iteration_count = Parameter(arg_type=int, default=1000)
    maximum_chunk_size = Parameter(arg_type=int, default=8)

    rate = Parameter(arg_type=float, default=0.1)
    data_term_amplifier = Parameter(arg_type=float, default=1.0)
    tikhonov_strength = Parameter(arg_type=float, default=0.2)
    kernel_size = Parameter(arg_type=int, default=7)
    kernel_strength = Parameter(arg_type=float, default=0.1, shorthand="-kst")
    resampling_strategy = Parameter(arg_type=str, default="NEAREST_AND_AVERAGE",
                                    arg_help="Strategy for upsampling the warps and downsampling the pyramid"
                                             "in the C++ version of the optimizer, can be "
                                             "either NEAREST_AND_AVERAGE or LINEAR")

    # data generation settings
    filtering_method = Parameter(arg_type=str, default="NONE")
    smoothing_coefficient = Parameter(arg_type=float, default=0.5)

    # other experiment settings
    dataset_number = Parameter(arg_type=int, default=1)
    implementation_language = Parameter(arg_type=str, default="CPP")

    output_path = Parameter(arg_type=str, default="output/ho")
    generation_case_file = \
        Parameter(arg_type=str, default=None,
                  arg_help="Generate data for the set of frames & pixel rows specified in this .csv file."
                           " Format is <frame_index>,<pixel row index>,<focus coordinate x>, "
                           "<focus coordinate y>.")
    optimization_case_file = \
        Parameter(arg_type=str, default=None,
                  arg_help="Run optimizer only on the set of frames & pixel rows specified in this .csv file "
                           "(assuming they are also present in the specified dataset)."
                           " Format is <frame_index>,<pixel row index>,<focus coordinate x>, "
                           "<focus coordinate y>.")
    series_result_subfolder = Parameter(arg_type=str, default=None,
                                        arg_help="Additional subfolder name to append to the output directory (useful "
                                                 "when saving results for a whole series)")

    # other experiment flags
    analyze_only = Parameter(action="store_true", default=False, arg_type='bool_flag',
                             arg_help="Skip anything by the final analysis (and only do that if corresponding output"
                                      " file is available). Supersedes any other option that deals with data"
                                      " generation / optimization.")
    generate_data = Parameter(action="store_true", default=False, arg_type='bool_flag')
    skip_optimization = Parameter(action="store_true", default=False, arg_type='bool_flag')
    save_initial_fields_during_generation = Parameter(action="store_true", default=False, arg_type='bool_flag')
    save_initial_and_final_fields = Parameter(action="store_true", default=False, arg_type='bool_flag',
                                              arg_help="save the initial canonical & live and final live field during"
                                                       " the optimization")
    save_telemetry = Parameter(action="store_true", default=False, arg_type='bool_flag')

    convert_telemetry = Parameter(action="store_true", default=False, arg_type='bool_flag',
                                  arg_help="Convert telemetry to videos")

    stop_before_index = Parameter(arg_type=int, default=10000000)
    start_from_index = Parameter(arg_type=int, default=0)


@pytest.fixture
def description_string():
    return "Runs 2D hierarchical optimizer on TSDF inputs generated from frame-pairs " \
           "& random pixel rows from these. Alternatively, generates the said data or " \
           "loads it from a folder from further re-use."


def test_default_parameters(description_string):
    process_arguments(Parameters, description_string, argv=[])

    assert not Parameters.tikhonov_term_enabled.value
    assert not Parameters.analyze_only.value
    assert Parameters.output_path.value == "output/ho"
    assert Parameters.filtering_method.value == "NONE"
    assert Parameters.maximum_warp_update_threshold.value == 0.01
    assert Parameters.maximum_chunk_size.value == 8


def test_full_length_parameters(description_string):
    process_arguments(Parameters, description_string, argv=["--tikhonov_term_enabled",
                                                            "--analyze_only",
                                                            "--output_path=output/lo",
                                                            "--filtering_method=BILINEAR",
                                                            "--maximum_warp_update_threshold=0.005",
                                                            "--maximum_chunk_size=12",
                                                            ])

    assert Parameters.tikhonov_term_enabled.value
    assert Parameters.analyze_only.value
    assert Parameters.output_path.value == "output/lo"
    assert Parameters.filtering_method.value == "BILINEAR"
    assert Parameters.maximum_warp_update_threshold.value == 0.005
    assert Parameters.maximum_chunk_size.value == 12


def test_shorthand_parameters(description_string):
    process_arguments(Parameters, description_string, argv=["-tte",
                                                            "-ao",
                                                            "-op=output/lo",
                                                            "-fm=BILINEAR",
                                                            "-mwut=0.006",
                                                            "-mcs=12",
                                                            ])

    assert Parameters.tikhonov_term_enabled.value
    assert Parameters.analyze_only.value
    assert Parameters.output_path.value == "output/lo"
    assert Parameters.filtering_method.value == "BILINEAR"
    assert Parameters.maximum_warp_update_threshold.value == 0.006
    assert Parameters.maximum_chunk_size.value == 12


@pytest.fixture
def test_data_dir():
    return os.path.join(pathlib.Path(__file__).parent.resolve(), "test_data")


def test_save_parameters(test_data_dir, description_string):
    output_settings_path = os.path.join(test_data_dir, "settings.yaml")
    # save default settings first
    process_arguments(Parameters, description_string,
                      argv=[f"--settings_file={output_settings_path}",
                            "--save_settings",
                            "-op=output/ho",
                            "-fm=NONE",
                            "-mwut=0.01",
                            "-mcs=8",
                            ])

    assert Parameters.output_path.value == "output/ho"
    assert Parameters.filtering_method.value == "NONE"
    assert Parameters.maximum_warp_update_threshold.value == 0.01
    assert Parameters.maximum_chunk_size.value == 8

    # save modified settings
    process_arguments(Parameters, description_string,
                      argv=[f"--settings_file={output_settings_path}",
                            "--save_settings",
                            "-op=output/lo",
                            "-fm=BILINEAR",
                            "-mwut=0.007",
                            "-mcs=10",
                            ])
    # load defaults again
    process_arguments(Parameters, description_string, argv=[])

    assert Parameters.maximum_warp_update_threshold.value == 0.01

    # load modified settings
    process_arguments(Parameters, description_string,
                      argv=[f"--settings_file={output_settings_path}"])

    assert Parameters.output_path.value == "output/lo"
    assert Parameters.filtering_method.value == "BILINEAR"
    assert Parameters.maximum_warp_update_threshold.value == 0.007
    assert Parameters.maximum_chunk_size.value == 10


def test_default_settings_file(test_data_dir, description_string):
    default_settings_path = os.path.join(test_data_dir, "default_settings.yaml")
    process_arguments(Parameters, description_string,
                      argv=["-fm=BILINEAR",
                            "-mwut=0.03",
                            "-mcs=5",
                            ], default_settings_file=default_settings_path)
    default_settings2_path = os.path.join(test_data_dir, "default_settings2.yaml")
    if os.path.exists(default_settings2_path):
        os.unlink(default_settings2_path)

    assert Parameters.filtering_method.value == "BILINEAR"
    assert Parameters.maximum_warp_update_threshold.value == 0.03
    assert Parameters.maximum_chunk_size.value == 5
    assert Parameters.implementation_language.value == "PYTHON"
    assert Parameters.rate.value == 0.08
    assert Parameters.stop_before_index.value == 32

    process_arguments(Parameters, description_string,
                      argv=["--save_settings",
                            "-fm=BILINEAR",
                            "-mwut=0.02",
                            "-mcs=9",
                            ],
                      default_settings_file=default_settings2_path,
                      generate_default_settings_if_missing=True)

    assert Parameters.filtering_method.value == "BILINEAR"
    assert Parameters.maximum_warp_update_threshold.value == 0.02
    assert Parameters.maximum_chunk_size.value == 9
    assert Parameters.implementation_language.value == "CPP"
    assert Parameters.rate.value == 0.1
    assert Parameters.stop_before_index.value == 10000000

    # load defaults, just in case
    process_arguments(Parameters, description_string, argv=[])

    assert Parameters.filtering_method.value == "NONE"
    assert Parameters.maximum_warp_update_threshold.value == 0.01
    assert Parameters.maximum_chunk_size.value == 8

    process_arguments(Parameters, description_string,
                      argv=[f"--settings_file={default_settings2_path}"])

    assert Parameters.filtering_method.value == "BILINEAR"
    assert Parameters.maximum_warp_update_threshold.value == 0.02
    assert Parameters.maximum_chunk_size.value == 9


def test_dump_parameters(description_string):
    process_arguments(Parameters, description_string, argv=["--tikhonov_term_enabled",
                                                            "--analyze_only",
                                                            "--output_path=output/lo",
                                                            "--filtering_method=BILINEAR",
                                                            "--maximum_warp_update_threshold=0.005",
                                                            "--maximum_chunk_size=12",
                                                            ])
    string_stream = StringIO()
    dump(Parameters, string_stream)

    ground_truth_string = \
        """
        tikhonov_term_enabled: true
        gradient_kernel_enabled: false
        maximum_warp_update_threshold: 0.005
        maximum_iteration_count: 1000
        maximum_chunk_size: 12
        rate: 0.1
        data_term_amplifier: 1.0
        tikhonov_strength: 0.2
        kernel_size: 7
        kernel_strength: 0.1
        resampling_strategy: NEAREST_AND_AVERAGE
        filtering_method: BILINEAR
        smoothing_coefficient: 0.5
        dataset_number: 1
        implementation_language: CPP
        output_path: output/lo
        generation_case_file:
        optimization_case_file:
        series_result_subfolder:
        analyze_only: true
        generate_data: false
        skip_optimization: false
        save_initial_fields_during_generation: false
        save_initial_and_final_fields: false
        save_telemetry: false
        convert_telemetry: false
        stop_before_index: 10000000
        start_from_index: 0
        """
    ground_truth_string = '\n'.join(line.strip() for line in ground_truth_string.split())
    output_string = '\n'.join(line.strip() for line in string_stream.getvalue().split())

    assert output_string == ground_truth_string
