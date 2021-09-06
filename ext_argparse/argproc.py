#  ================================================================
#  Created by Gregory Kramida on 8/9/16.
#  Copyright (c) 2016 Gregory Kramida
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  ================================================================
from typing import Type, List, Union

from ext_argparse.parameter import Parameter
from ext_argparse.param_enum import ParameterEnum
import argparse
import os.path
import re
import enum
from ruamel.yaml import YAML


def generate_lc_acronym_from_snake_case(snake_case_string: str) -> str:
    return "".join([word_match[1] for word_match in re.findall(r"(:?^|_)(\w)", snake_case_string)])


def unflatten_dict(dictionary):
    dict_out = {}
    path_word_pattern = re.compile(r'(?:^|[.])(\w+)')
    for key, value in dictionary.items():
        path_words = path_word_pattern.findall(key)
        current_level_dict = dict_out
        # create necessary nesting based on the key
        for word in path_words[:-1]:
            if word not in current_level_dict:
                current_level_dict[word] = {}
            current_level_dict = current_level_dict[word]
        current_level_dict[path_words[-1]] = value
    return dict_out


def flatten_dict(dictionary):
    dict_out = {}
    for key, value in dictionary.items():
        if type(value) == dict:
            flattened_sub_dict = flatten_dict(value)
            for sub_key, sub_value in flattened_sub_dict.items():
                dict_out[key + "." + sub_key] = sub_value
        else:
            dict_out[key] = value
    return dict_out


class ArgumentProcessor(object):
    """
    A class for processing command-line arguments to a program.
    """

    def __init__(self, parameter_enum: Type[ParameterEnum]):
        self.parameter_enum = parameter_enum
        self.__generate_missing_shorthands()
        self.setting_file_location_args = self.__get_setting_file_location_args()

    # ================= SETTING FILE STORAGE ==========================================================================#
    settings_file = Parameter(None, '?', str, 'store',
                              "File (absolute or relative-to-execution path) where to save and/or " +
                              "load settings for the program in YAML format.",
                              console_only=True, required=False)
    save_settings = Parameter(False, '?', 'bool_flag', 'store_true',
                              "Save (or update) setting file.",
                              console_only=True, required=False)
    settings_file_parameter_name = "settings_file"
    settings_file_shorthand = "-sf"
    save_settings_parameter_name = "save_settings"
    save_settings_shorthand = "-ss"

    @staticmethod
    def __get_setting_file_location_args_from_item(item, sfl_arg_collection: set, base_name=""):
        if item.parameter.type == 'parameter_enum':
            for sub_item in item.parameter:
                ArgumentProcessor.__get_setting_file_location_args_from_item(sub_item, sfl_arg_collection,
                                                                             base_name + item.name + ".")
        elif item.parameter.setting_file_location:
            sfl_arg_collection.add(base_name + item.name)

    def __get_setting_file_location_args(self):
        sfl_arg_collection = set()
        for item in self.parameter_enum:
            ArgumentProcessor.__get_setting_file_location_args_from_item(item, sfl_arg_collection)
        return sfl_arg_collection

    @staticmethod
    def __add_shorthand_for_param_enum_item(enum_entry, base_acronym: str = "") -> None:
        if enum_entry.parameter.type == 'parameter_enum':
            sub_enum_acronym = generate_lc_acronym_from_snake_case(enum_entry.name)
            for sub_item in enum_entry.parameter:
                ArgumentProcessor.__add_shorthand_for_param_enum_item(sub_item, base_acronym + sub_enum_acronym + ".")
        elif enum_entry.parameter.shorthand is None:
            enum_entry.parameter.shorthand = base_acronym + generate_lc_acronym_from_snake_case(enum_entry.name)

    def __generate_missing_shorthands(self):
        for item in self.parameter_enum:
            ArgumentProcessor.__add_shorthand_for_param_enum_item(item)

    @staticmethod
    def __add_to_defaults_dict(enum_entry, defaults_dict: dict, base_name: str = ""):
        if enum_entry.parameter.type == 'parameter_enum':
            for sub_enum_item in enum_entry.parameter:
                ArgumentProcessor.__add_to_defaults_dict(sub_enum_item, defaults_dict,
                                                         base_name + enum_entry.name + ".")
        else:
            defaults_dict[base_name + enum_entry.name] = enum_entry.parameter.default

    def generate_defaults_dict(self):
        """
        @rtype: dict
        @return: dictionary of Setting defaults
        """
        defaults_dict = {}
        for item in self.parameter_enum:
            ArgumentProcessor.__add_to_defaults_dict(item, defaults_dict)
        defaults_dict[ArgumentProcessor.settings_file_parameter_name] = ArgumentProcessor.settings_file.default
        defaults_dict[ArgumentProcessor.save_settings_parameter_name] = ArgumentProcessor.save_settings.default
        return defaults_dict

    @staticmethod
    def __add_parameter_enum_entry_to_parser(enum_entry: Union[Parameter, ParameterEnum],
                                             parser: argparse.ArgumentParser, defaults: dict, console_only: bool,
                                             base_name: str = "") \
            -> None:
        if enum_entry.parameter.type == 'parameter_enum':
            for sub_enum_entry in enum_entry.parameter:
                ArgumentProcessor.__add_parameter_enum_entry_to_parser(
                    sub_enum_entry, parser, defaults, console_only,
                    base_name + enum_entry.name + "."
                )
        elif (enum_entry.parameter.console_only and console_only) or \
                (not enum_entry.parameter.console_only and not console_only):
            # TODO: transition to match statement here when the Python requirements is at or above 3.10
            if enum_entry.parameter.type == 'bool_flag':
                parser.add_argument("-" + enum_entry.parameter.shorthand,
                                    '--' + base_name + enum_entry.name,
                                    action=enum_entry.parameter.action,
                                    default=defaults[base_name + enum_entry.name],
                                    required=enum_entry.parameter.required,
                                    help=enum_entry.parameter.help)
            elif isinstance(enum_entry.parameter.type, enum.EnumMeta):
                parser.add_argument("-" + enum_entry.parameter.shorthand,
                                    '--' + base_name + enum_entry.name,
                                    action=enum_entry.parameter.action,
                                    type=str, nargs=enum_entry.parameter.nargs,
                                    required=enum_entry.parameter.required,
                                    default=defaults[base_name + enum_entry.name],
                                    help=enum_entry.parameter.help)
            else:
                parser.add_argument("-" + enum_entry.parameter.shorthand,
                                    '--' + base_name + enum_entry.name,
                                    action=enum_entry.parameter.action,
                                    type=enum_entry.parameter.type, nargs=enum_entry.parameter.nargs,
                                    required=enum_entry.parameter.required,
                                    default=defaults[base_name + enum_entry.name],
                                    help=enum_entry.parameter.help)

    def generate_parser(self, defaults: dict, console_only: bool = False, description: str = "Description N/A",
                        parents: Union[List[argparse.ArgumentParser], None] = None) -> argparse.ArgumentParser:
        """
        @rtype: argparse.ArgumentParser
        @return: either a console-only or a config_file+console parser using the specified defaults and, optionally,
        parents.
        @type defaults: dict
        @param defaults: dictionary of default settings and their values.
        For a conf-file+console parser, these come from the config file. For a console-only parser, these are generated.
        @type console_only: bool
        @type description: str
        @param description: description of the program that uses the parser, to be used in the help file
        @type parents: list[argparse.ArgumentParser] | None
        """
        if console_only:
            parser = argparse.ArgumentParser(description=description,
                                             formatter_class=argparse.RawDescriptionHelpFormatter,
                                             add_help=False)
        else:
            if parents is None:
                raise ValueError("A conf-file+console parser requires at least a console-only parser as a parent.")
            parser = argparse.ArgumentParser(parents=parents)

        for enum_entry in self.parameter_enum:
            ArgumentProcessor.__add_parameter_enum_entry_to_parser(enum_entry, parser, defaults, console_only)

        if console_only:
            # add non-enum args
            enum_entry = ArgumentProcessor.settings_file
            parser.add_argument(ArgumentProcessor.settings_file_shorthand,
                                '--' + ArgumentProcessor.settings_file_parameter_name,
                                action=enum_entry.action, type=enum_entry.type, nargs=enum_entry.nargs,
                                required=enum_entry.required,
                                default=defaults[ArgumentProcessor.settings_file_parameter_name],
                                help=enum_entry.help)
            enum_entry = ArgumentProcessor.save_settings
            parser.add_argument(ArgumentProcessor.save_settings_shorthand,
                                '--' + ArgumentProcessor.save_settings_parameter_name,
                                action=enum_entry.action,
                                default=defaults[ArgumentProcessor.save_settings_parameter_name],
                                required=enum_entry.required, help=enum_entry.help)

        if not console_only:
            parser.set_defaults(**defaults)
        return parser

    @staticmethod
    def __fill_parameter_enum_values(argument_dictionary: dict, parameter_enum: Type[ParameterEnum],
                                     base_name: str = ""):
        for enum_entry in parameter_enum:
            if enum_entry.parameter.type == 'parameter_enum':
                ArgumentProcessor.__fill_parameter_enum_values(argument_dictionary, enum_entry.parameter,
                                                               base_name + enum_entry.name + ".")
            else:
                full_param_path = base_name + enum_entry.name
                if full_param_path in argument_dictionary:
                    enum_entry.__dict__["argument"] = argument_dictionary[full_param_path]

    def set_values_from_flat_dict(self, argument_dictionary: dict):
        ArgumentProcessor.__fill_parameter_enum_values(argument_dictionary, self.parameter_enum)

    @staticmethod
    def __post_process_enum_arg(enum_entry):
        if isinstance(enum_entry.parameter.type, enum.EnumMeta) and not isinstance(enum_entry.value, enum.Enum):
            enum_entry.__dict__["argument"] = enum_entry.parameter.value_map[enum_entry.value]
        elif enum_entry.parameter.type == 'parameter_enum':
            for sub_enum_entry in enum_entry.parameter:
                ArgumentProcessor.__post_process_enum_arg(sub_enum_entry)

    def post_process_enum_args(self):
        for enum_entry in self.parameter_enum:
            ArgumentProcessor.__post_process_enum_arg(enum_entry)


def process_arguments(program_arguments_enum: Type[ParameterEnum], program_help_description: str,
                      argv: List[str] = None) -> argparse.Namespace:
    processor = ArgumentProcessor(program_arguments_enum)
    defaults = processor.generate_defaults_dict()

    conf_parser = \
        processor.generate_parser(defaults, console_only=True, description=program_help_description)

    # ============== STORAGE/RETRIEVAL OF CONSOLE SETTINGS ===========================================#
    args, remaining_argv = conf_parser.parse_known_args(argv)

    defaults[ArgumentProcessor.save_settings_parameter_name] = args.save_settings

    yaml = YAML(typ='safe')
    yaml.indent = 4
    yaml.default_flow_style = False

    if args.settings_file:
        defaults[ArgumentProcessor.settings_file_parameter_name] = args.settings_file
        if os.path.isfile(args.settings_file):
            file_stream = open(args.settings_file, "r", encoding="utf-8")
            config_defaults = yaml.load(file_stream)
            file_stream.close()
            if config_defaults:
                config_defaults = flatten_dict(config_defaults)
                for key, value in config_defaults.items():
                    defaults[key] = value
        else:
            if not args.save_settings:
                raise ValueError("Settings file not found at: {0:s}".format(args.settings_file))

    parser = processor.generate_parser(defaults, parents=[conf_parser])
    args = parser.parse_args(remaining_argv)

    # process "special" setting values
    keys_with_sfl_wildcard_set = set()
    if args.settings_file and os.path.isfile(args.settings_file):
        for key in args.__dict__.keys():
            if key in processor.setting_file_location_args and args.__dict__[key] == \
                    Parameter.setting_file_location_wildcard:
                args.__dict__[key] = os.path.dirname(args.settings_file)
                keys_with_sfl_wildcard_set.add(key)

    argument_dict = vars(args)
    processor.set_values_from_flat_dict(argument_dict)
    processor.post_process_enum_args()

    # reset paths where wildcards were used back to the wildcards
    if args.settings_file and os.path.isfile(args.settings_file):
        for key in argument_dict.keys():
            if key in keys_with_sfl_wildcard_set:
                argument_dict[key] = Parameter.setting_file_location_wildcard
    unflattened_argument_dict = unflatten_dict(argument_dict)

    # save settings if prompted to do so
    if args.save_settings and args.settings_file:
        # TODO: alter the saving such that it doesn't overwrite comments in the configuration file
        file_stream = open(args.settings_file, "w", encoding="utf-8")
        file_name = unflattened_argument_dict[ArgumentProcessor.save_settings_parameter_name]
        del unflattened_argument_dict[ArgumentProcessor.save_settings_parameter_name]
        del unflattened_argument_dict[ArgumentProcessor.settings_file_parameter_name]
        yaml.dump(unflattened_argument_dict, file_stream)
        file_stream.close()
        unflattened_argument_dict[ArgumentProcessor.save_settings_parameter_name] = file_name
        unflattened_argument_dict[ArgumentProcessor.settings_file_parameter_name] = True

    return args
