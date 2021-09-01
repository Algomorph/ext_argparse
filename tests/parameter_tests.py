import os
import sys
import pytest
import pathlib

from ext_argparse import Parameter, ParameterEnum, process_arguments


class SequenceHandlingParameters(ParameterEnum):
    stop_before_index = Parameter(arg_type=int, default=10000000)
    start_from_index = Parameter(arg_type=int, default=0)


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
    kernel_strength = Parameter(arg_type=float, default=0.1, acronym="-kst")
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

    sequence_handling = SequenceHandlingParameters

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


def test_default_parameters():
    process_arguments(Parameters, "Runs 2D hierarchical optimizer on TSDF inputs generated from frame-pairs "
                                  "& random pixel rows from these. Alternatively, generates the said data or "
                                  "loads it from a folder from further re-use.", [])

    assert not Parameters.tikhonov_term_enabled.value
    assert not Parameters.analyze_only.value
    assert Parameters.output_path.value == "output/ho"
    assert Parameters.filtering_method.value == "NONE"
    assert Parameters.maximum_warp_update_threshold.value == 0.01
    assert Parameters.maximum_chunk_size.value == 8


def test_full_length_parameters():
    process_arguments(Parameters, "Runs 2D hierarchical optimizer on TSDF inputs generated from frame-pairs "
                                  "& random pixel rows from these. Alternatively, generates the said data or "
                                  "loads it from a folder from further re-use.",
                      ["--tikhonov_term_enabled",
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


def test_shorthand_parameters():
    process_arguments(Parameters, "Runs 2D hierarchical optimizer on TSDF inputs generated from frame-pairs "
                                  "& random pixel rows from these. Alternatively, generates the said data or "
                                  "loads it from a folder from further re-use.",
                      ["-tte",
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


def test_save_parameters():
    test_data_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), "test_data")
    output_settings_path = os.path.join(test_data_dir, "settings.yaml")
    # save default settings first
    process_arguments(Parameters, "Runs 2D hierarchical optimizer on TSDF inputs generated from frame-pairs "
                                  "& random pixel rows from these. Alternatively, generates the said data or "
                                  "loads it from a folder from further re-use.",
                      [f"--settings_file={output_settings_path}",
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
    process_arguments(Parameters, "Runs 2D hierarchical optimizer on TSDF inputs generated from frame-pairs "
                                  "& random pixel rows from these. Alternatively, generates the said data or "
                                  "loads it from a folder from further re-use.",
                      [f"--settings_file={output_settings_path}",
                       "--save_settings",
                       "-op=output/lo",
                       "-fm=BILINEAR",
                       "-mwut=0.007",
                       "-mcs=10",
                       ])
    # load defaults again
    process_arguments(Parameters, "Runs 2D hierarchical optimizer on TSDF inputs generated from frame-pairs "
                                  "& random pixel rows from these. Alternatively, generates the said data or "
                                  "loads it from a folder from further re-use.", [])

    assert Parameters.maximum_warp_update_threshold.value == 0.01

    # load modified settings
    process_arguments(Parameters, "Runs 2D hierarchical optimizer on TSDF inputs generated from frame-pairs "
                                  "& random pixel rows from these. Alternatively, generates the said data or "
                                  "loads it from a folder from further re-use.",
                      [f"--settings_file={output_settings_path}"])

    assert Parameters.output_path.value == "output/lo"
    assert Parameters.filtering_method.value == "BILINEAR"
    assert Parameters.maximum_warp_update_threshold.value == 0.007
    assert Parameters.maximum_chunk_size.value == 10
