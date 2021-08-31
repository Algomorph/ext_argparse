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
from typing import Type, List

from ext_argparse.parameter import Parameter
from ext_argparse.param_collection import ParameterEnum
import argparse
import os.path
import re
from ruamel.yaml import YAML


class ArgumentProcessor(object):
    """
    A class for processing command-line arguments to a program.
    """

    def __init__(self, parameter_enum: Type[ParameterEnum]):
        self.parameter_enum = parameter_enum
        self.__generate_missing_shorthands()
        self.setting_file_location_args = self.__generate_setting_file_location_arg_collection()

    # ================= SETTING FILE STORAGE ==========================================================================#
    settings_file = Parameter(None, '?', str, 'store',
                              "File (absolute or relative-to-execution path) where to save and/or " +
                              "load settings for the program in YAML format.",
                              console_only=True, required=False)
    save_settings = Parameter(False, '?', 'bool_flag', 'store_true',
                              "Save (or update) setting file.",
                              console_only=True, required=False)
    settings_file_name = "settings_file"
    settings_file_shorthand = "-sf"
    save_settings_name = "save_settings"
    save_settings_shorthand = "-ss"

    def __generate_setting_file_location_arg_collection(self):
        sfl_arg_collection = set()
        for item in self.parameter_enum:
            if item.parameter.setting_file_location:
                sfl_arg_collection.add(item.name)
        return sfl_arg_collection

    def __generate_missing_shorthands(self):
        for item in self.parameter_enum:
            if item.parameter.shorthand is None:
                item.parameter.shorthand = "-" + "".join([item[1] for item in re.findall(r"(:?^|_)(\w)", item.name)])

    def generate_defaults_dict(self):
        """
        @rtype: dict
        @return: dictionary of Setting defaults
        """
        defaults_dict = {}
        for item in self.parameter_enum:
            defaults_dict[item.name] = item.parameter.default
        defaults_dict[ArgumentProcessor.settings_file_name] = ArgumentProcessor.settings_file.default
        defaults_dict[ArgumentProcessor.save_settings_name] = ArgumentProcessor.save_settings.default
        return defaults_dict

    def generate_parser(self, defaults, console_only=False, description="Description N/A", parents=None):
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
            if (enum_entry.parameter.console_only and console_only) or (
                    not enum_entry.parameter.console_only and not console_only):
                if enum_entry.parameter.type == 'bool_flag':
                    parser.add_argument('--' + enum_entry.name, enum_entry.parameter.shorthand,
                                        action=enum_entry.parameter.action,
                                        default=defaults[enum_entry.name], required=enum_entry.parameter.required,
                                        help=enum_entry.parameter.help)
                else:
                    parser.add_argument('--' + enum_entry.name, enum_entry.parameter.shorthand,
                                        action=enum_entry.parameter.action,
                                        type=enum_entry.parameter.type, nargs=enum_entry.parameter.nargs,
                                        required=enum_entry.parameter.required,
                                        default=defaults[enum_entry.name], help=enum_entry.parameter.help)
        if console_only:
            # add non-enum args
            enum_entry = ArgumentProcessor.settings_file
            parser.add_argument(ArgumentProcessor.settings_file_shorthand, '--' + ArgumentProcessor.settings_file_name,
                                action=enum_entry.action, type=enum_entry.type, nargs=enum_entry.nargs,
                                required=enum_entry.required, default=defaults[ArgumentProcessor.settings_file_name],
                                help=enum_entry.help)
            enum_entry = ArgumentProcessor.save_settings
            parser.add_argument(ArgumentProcessor.save_settings_shorthand, '--' + ArgumentProcessor.save_settings_name,
                                action=enum_entry.action, default=defaults[ArgumentProcessor.save_settings_name],
                                required=enum_entry.required, help=enum_entry.help)

        if not console_only:
            parser.set_defaults(**defaults)
        return parser

    def fill_enum_values(self, setting_dict):
        for enum_entry in self.parameter_enum:
            if enum_entry.name in setting_dict:
                enum_entry.__dict__["argument"] = setting_dict[enum_entry.name]


def process_arguments(program_arguments_enum: Type[ParameterEnum], program_help_description: str,
                      argv: List[str] = None) -> argparse.Namespace:
    argproc = ArgumentProcessor(program_arguments_enum)
    defaults = argproc.generate_defaults_dict()
    conf_parser = \
        argproc.generate_parser(defaults, console_only=True, description=program_help_description)

    # ============== STORAGE/RETRIEVAL OF CONSOLE SETTINGS ===========================================#
    args, remaining_argv = conf_parser.parse_known_args(argv)
    defaults[ArgumentProcessor.save_settings_name] = args.save_settings

    yaml = YAML(typ='safe')
    yaml.indent = 4
    yaml.default_flow_style = False

    if args.settings_file:
        defaults[ArgumentProcessor.settings_file_name] = args.settings_file
        if os.path.isfile(args.settings_file):
            file_stream = open(args.settings_file, "r", encoding="utf-8")
            config_defaults = yaml.load(file_stream)
            file_stream.close()
            if config_defaults:
                for key, value in config_defaults.items():
                    defaults[key] = value
        else:
            if not args.save_settings:
                raise ValueError("Settings file not found at: {0:s}".format(args.settings_file))

    parser = argproc.generate_parser(defaults, parents=[conf_parser])
    args = parser.parse_args(remaining_argv)

    # process "special" setting values
    if args.settings_file and os.path.isfile(args.settings_file):
        for key in args.__dict__.keys():
            if key in argproc.setting_file_location_args and args.__dict__[key] == \
                    Parameter.setting_file_location_wildcard:
                args.__dict__[key] = os.path.dirname(args.settings_file)

    setting_dict = vars(args)
    argproc.fill_enum_values(setting_dict)

    # save settings if prompted to do so
    if args.save_settings and args.settings_file:
        file_stream = open(args.settings_file, "w", encoding="utf-8")
        file_name = setting_dict[ArgumentProcessor.save_settings_name]
        del setting_dict[ArgumentProcessor.save_settings_name]
        del setting_dict[ArgumentProcessor.settings_file_name]

        yaml.dump(setting_dict, file_stream)
        file_stream.close()
        setting_dict[ArgumentProcessor.save_settings_name] = file_name
        setting_dict[ArgumentProcessor.settings_file_name] = True

    return args
