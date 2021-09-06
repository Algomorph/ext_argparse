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
import enum
from typing import Union


class Parameter(object):
    setting_file_location_wildcard = '!settings_file_location'

    def __init__(self, default=None,
                 nargs='?',
                 arg_type: Union[str, type, enum.EnumMeta] = str,
                 action: str = 'store',
                 arg_help: str = "Documentation N/A",
                 console_only: bool = False,
                 required: bool = False,
                 shorthand=None,
                 setting_file_location: bool = False):
        """
        @rtype: Parameter
        @type default: object
        @param default: the default value
        @type nargs: int | str
        @param nargs: number of arguments. See python documentation for ArgumentParser.add_argument.
        @type arg_type: type | str
        @param arg_type: type of value to expect during parsing
        @type action: str | function
        @param action: action to perform with the argument value during parsing
        @type arg_help: str
        @param arg_help: documentation for this argument
        @type console_only: bool
        @param console_only: whether the argument is for console use only or for both config file & console
        @type required: bool
        @param required: whether the argument is required
        @type shorthand: str
        @param shorthand: acronym to use in the shorthand for the argument in the console
        @type setting_file_location: bool
        @param setting_file_location: whether this parameter can use the setting file location wildcard
        (in which case, when set to the wildcard, the parameter value resolves to the full path to the settings
        file instead.)
        """
        self.default = default
        self.required = required
        self.console_only = console_only
        self.nargs = nargs
        self.type = arg_type
        self.action = action
        self.argument = None
        if setting_file_location:
            self.help = arg_help + ("| If set to '" + Parameter.setting_file_location_wildcard + "' and a " +
                                    " settings file is provided, will be set to the location of the settings file.")
        else:
            self.help = arg_help
        self.setting_file_location = setting_file_location
        self.shorthand = shorthand
        self.value_map = None
        if type(self.type) == enum.EnumMeta:
            self.value_map = self.type._member_map_
            self.help = arg_help + "| Can be set to one of: " + str(list(self.value_map.keys()))

    def get_type(self):
        return self.type
