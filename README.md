# ext_argparse

![python app workflow](https://github.com/Algomorph/ext_argparse/actions/workflows/python-app.yml/badge.svg)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


This is an extended version of Python's `argparse` that, in a nutshell, supports these three things:
* using code-completion to access parameters and/or their values (a.k.a. arguments)
* configuration file input/output, with the option to override/update files via the command line
* natural support for Python's Enums, i.e. categorical parameters.

## Why another CLI / Config File Library?

Over about six years I've found myself reusing a basic version of the code in this library over and over again, because 
I didn't find anything that supported CLI & config IO functionality which I thought was natural and comfortable. 
Recently, I again found myself in need of such a library and discovered that in all those years, nobody published 
a library having all these features and characteristics (although some of these have other features that may or may not 
interest you.)

Features / characteristics of existing libraries and modules in comparison to **ext_argparse**:

| Feature (down) \ library (right) | argparse | configparser | docopt  | easyargs | parse_it  | $click_  | hydra    | **ext_argparse** |   
| -------------------------------- | -------- | ------------ | ------  | -------  | --------- | -------- | -------- | ---------------- |
| Command line input               | **yes**  |              | **yes** | **yes**  | **yes**   | **yes**  | **yes**  | **yes**          |
| Environment variable input       |          |              |         |          | **yes**   |          |          |                  |
| Configuration file input         |          | **yes**      |         |          | **yes**   |          | **yes**  | **yes**          |
| Configuration file output        |          | **yes**      |         |          |           |          |          | **yes**          |
| Argument code-complete support   |          |              |         | **yes**  |           | **yes**  | **yes**  | **yes**          |
| Argument documentation (--help)  | **yes**  |              |         |          |           | **yes**  |          | **yes**          |
| Config-file comments             |          | **yes**      |         |          | **yes**   |          |          | **yes**          |
| Nested arguments                 |          | **yes**      |         |          |           |          | **yes**  | **yes**          |
| Nested commands                  |          |              |         |          |           | **yes**  |          |                  |
| Enum argument type               |          |              |         |          |           |          | **yes**  | **yes**          |
| Avoids duplicating names in code | kind-of  |              | kind-of | **yes**  | kind-of   |          | **yes**  | **yes**          |
| Avoids magic strings             | kind-of  |              |         | **yes**  |           | **yes**  | **yes**  | **yes**          |

I should note that positional arguments are currently not supported in `ext_argparse`, and that is a major limitation 
(and easy fix) that, I think, should be addressed soon.

Another difference that also deserves note here is that `ext_argparse` currently supports configuration file IO *only* 
in [YAML](https://yaml.org/) format. Support for config file comments (via the `ruamel.yaml` package) may be easily 
integrated, as well as backends for other popular formats, such as [TOML](https://github.com/toml-lang/toml) and
[JSON5](https://json5.org/). Contributions are welcome!

In the meantime, `parse_it` supports six formats, including JSON, YAML, TOML, HCL, INI, and XML, but obviously has other
limitations as can be observed in the table.

(*) Also of note is that `easyargs` and `$click_` in a sense support code-completion of the arguments, since they provide 
a one-to-one mapping between function parameters and CLI parameters. In contrast, `ext_argparse` does this directly via 
the fields of the user-provided parameter enumeration, i.e. any class extending `ParameterEnum` (see usage below).

`hydra` deserves an honorable mention here. It supports code-completion, and arguably in a better way than `ext_argparse`,
via Python's built-in [dataclasses](https://docs.python.org/3/library/dataclasses.html). The only downside to that approach
is that documentation strings cannot yet be handled and it's not clear how to provide support for such, although that issue
is being [discussed](https://github.com/facebookresearch/hydra/issues/633). `hydra` is the only library besides `ext_argparse`
that naturally handles Enums and allows to override configuration file arguments from the command line. It also provides 
several other features that `ext_argparse` currently doesn't: argument override rules, config groups, etc.

## Installation

There are three different ways to install `ext_argparse`. Choose your poison.

### Via PyPI & Pip

`pip install ext_argparse`

### Via Online Repo & Pip:

`pip install -e git+https://github.com/Algomorph/ext_argparse@main`

### From Source via Pip:

`git clone https://github.com/Algomorph/ext_argparse` or `git clone git@github.com:Algomorph/ext_argparse.git`

Then, from repository root,

`python3 -m build --wheel` or `py -m build --wheel` depending on your platform,

and, finally, install the resulting wheel:

`pip install dist/*.whl`

## Basic Usage

```Python
from ext_argparse import ParameterEnum, Parameter, process_arguments


class Parameters(ParameterEnum):  # name your subclass here however you see fit
    # Parameter class constructor also accepts arguments for 'nargs' and 'action',
    # similar to ArgumentParser.add_argument
    name = Parameter(default="Frodo Baggins", arg_type=str, arg_help="Name of our hero.")
    lembas_bread = Parameter(arg_type=int, required=True)
    height = Parameter(default=1.12, arg_type=float, arg_help="Height in meters.")


# ...
# Then, somewhere in the main function or body of your program:

process_arguments(Parameters, program_help_description="A program for estimating chances of hero at success.")

# And access arguments like so:
print(f"The name of our dear hero is: {Parameters.name.value}")
can_fit_through_narrow_caves = Parameters.height.value < 1.3
provisions_duration_days = Parameters.lembas_bread.value * 2
```
Note that IDEs and editors with proper code autocompletion, such as properly-configured VS Code, Sublime Text, or 
PyCharm, will now be able to suggest parameter name completion after `Parameters.`, which may prove useful in situations 
with a great number of parameters.

Names of CLI parameters are handled similar to the argparse library, e.g. the code above might be run with this command:

`python3 -m estimate_hero_success.py --name="Samwise Gamgee" --lembas_bread=25 --height=1.21`

Shorthand notation, by default, is autogenerated using the first letters of the parameter name, e.g.:

`python3 -m estimate_hero_success.py -n="Samwise Gamgee" -lb=25 -h=1.21`

If there is a need to avoid shorthand parameter naming conflicts or a need for a custom shorthand, `shorthand` may be
passed to the constructor of any `Parameter`:

`lembas_bread = Parameter(arg_type=int, required=True, shorthand="lembr")`

Here, the resulting command might look like:

`python3 -m estimate_hero_success.py -n="Samwise Gamgee" -lembr=25 -h=1.21`

## Enum Type Support

We can naturally extend the example above to use Enums:

```Python
from ext_argparse import ParameterEnum, Parameter, process_arguments
from enum import Enum


class Species(Enum):
    HOBBIT = 0
    ELF = 2
    ORK = 3
    HUMAN = 4
    WIZARD = 5
    DRAGON = 6
    GIANT_SPIDER = 7
    CAVE_TROLL = 8


class Parameters(ParameterEnum):
    name = Parameter(default="Frodo Baggins", arg_type=str,
                     arg_help="Name of our hero.")
    lembas_bread = Parameter(arg_type=int, required=True)
    species = Parameter(default=Species.HOBBIT, arg_type=Species,
                        arg_help="Species of our hero.")


# ...
# Then, somewhere in the main function or body of your program:
process_arguments(Parameters, program_help_description="A program for estimating chances of hero at success.")

# Argument access:
print(f"The name of our dear hero is: {Parameters.name.value}")
provisions_duration_days = Parameters.lembas_bread.value * 2
if Parameters.species.value is Species.CAVE_TROLL:
    print("Cave trolls turn to stone at daytime. Let's check what time of day it is...")
```

Our command line might then look like this:
`python3 -m estimate_hero_success.py --name="Gandalf the Grey" --lembas_bread=5 --height=1.82 --species=WIZARD`

Note that just the string `WIZARD` is used at the command line, not something like `Species.WIZARD` or lowercase `wizard`.

## Configuration File IO

We can easily handle settings from a configuration file via passing some special settings that are _always_ handled.

`python3 -m estimate_hero_success.py --lembas_bread=25  --settings_file=lord_of_the_rings/the_two_towers/SamwiseConfig.yaml`

The command line above will read the parameter values in [YAML](https://yaml.org/) format from the specified file and 
_override_ the `lembas_bread` setting with the argument `25`. The setting file `SamwiseConfig.yaml` for the example 
above might look like this:

```yaml
name: "Samwize Gamgee"
lembas_bread: 20
height: 1.21
```

If you also wanted to save the updated settings that you've overridden from the command line, you can use something like:

`python3 -m estimate_hero_success.py --lembas_bread=25  --settings_file=lord_of_the_rings/the_two_towers/SamwiseConfig.yaml --save_settings`

**Note**: it is up to you to ensure there are no shorthand conflicts with `settings_file` and `save_settings` (`sf` and 
`ss` shorthands, respectively) via innovative naming or custom `shorthand` arguments.

There is also a special value you can use in string arguments accepting _paths_ to resources, `!setting_file_location`, 
that will be substituted with the directory of the setting file inside the program (when such is specified).

Imagine we had the following parameter in our `Parameters` enum above:

`output_path = Parameter(default="./output", arg_type=str, help="Where to store the output data and report.")`

We could then pass in the `!setting_file_location` wildcard like so:

`python3 -m estimate_hero_success.py --settings_file=lord_of_the_rings/the_two_towers/SamwiseConfig.yaml --output=!setting_file_location`

The value of `Parameters.output` would be `lord_of_the_rings/the_two_towers`. 

Also note that command line arguments appear and are handled _exactly_ the same as parameter values inside the settings 
file, including the `Enum` parameters, the `!setting_file_location` wildcard, and nested arguments (described below).

Also, note that any subset of arguments can be provided from either or both sources, in which case the remaining 
parameters will be set to default values.

## Nested Parameter Support

Any level of nesting can be handled both via the configuration file or the command line:

```Python
from ext_argparse import ParameterEnum, Parameter, process_arguments
from typing import Type


class QuestParameters(ParameterEnum):
    name = Parameter(default="Ring Destruction", arg_type=str, arg_help="Name of the quest.")
    destination = Parameter(default="Mount Doom", arg_type=str, arg_help="Final quest destination.")
    year = Parameter(default=3018, arg_type=int, arg_help="Year of the Third Age when the quest is to begin")


class HeroParameters(ParameterEnum):
    name = Parameter(default="Frodo Baggins", arg_type=str, arg_help="Name of our hero.")
    lembas_bread = Parameter(arg_type=int, required=True)
    height = Parameter(default=1.12, arg_type=float, arg_help="Height in meters.")


class Parameters(ParameterEnum):
    output = Parameter(default="!setting_file_location", arg_type=str,
                       arg_help="Directory where to output the detailed analysis data and report.")
    # Note the usage of typing.Type here to give code completion an additional nudge. 
    # Otherwise, it won't work on the nesting for PyCharm (haven't tested in VS Code or Sublime).
    hero: Type[HeroParameters] = HeroParameters
    quest: Type[QuestParameters] = QuestParameters


# ...
# Then, somewhere in the main function or body of your program:

process_arguments(Parameters,
                  program_help_description="A program for estimating chances of hero at success in a particular quest.")

# And access arguments like so (note the usage of .hero and .quest):
print(f"The name of our dear hero is: {Parameters.hero.name.value}")
can_fit_through_narrow_caves = Parameters.hero.height.value < 1.3
provisions_duration_days = Parameters.hero.lembas_bread.value * 2

print(f"The name of the quest is: {Parameters.quest.name.value}")
aragorn_alive_at_start_of_quest = Parameters.quest.year.value > 2931
# ...
```

A command line for the above program might look like this:

`python3 -m estimate_hero_success.py --hero.name="Saruman the White" --hero.lembas_bread=0 --hero.height=1.84 --quest.name="Corruption of Rohan" --quest.year=3014 --quest.destination=Edoras`

A settings file with the above arguments might look like this:
```yaml
output: '!setting_file_location'
hero:
  name: "Saruman the White"
  lembas_bread: 0
  height: 1.21
quest:
  name: "Corruption of Rohan"
  year: 3014
  destination: "Edoras"
```

## Licence Information

The code is released under [Apache License V2](https://www.apache.org/licenses/LICENSE-2.0).