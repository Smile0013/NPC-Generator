#!/usr/bin/env python
"""
# NPC generator
# Cod version: v.0.1.0
# _______________________________________
# Generates NPC from database in txt file
# _______________________________________
# First update: 29.2.2024.
# First programmer: Martin Martinic
# Last update: 30.7.2025.
# Last programmer: Martin Martinic
# _______________________________________
"""

import random
import itertools
import re
import os

global_config_path = './config.txt'
global_database_path = './database'


def load_files(inp_data):
    # load data file
    # _______________________________________
    if inp_data.endswith('.txt'):  # support for legacy database type
        try:
            with open(inp_data, encoding='utf-8') as data_f:
                out_data = data_f.read()
        except FileNotFoundError:
            if inp_data == global_config_path or inp_data == global_database_path:
                raise FileNotFoundError(f"Database file {inp_data} not found.")
            pass

    else:  # file is data directory
        out_data = {}
        try:
            for tmp_filename in os.listdir(inp_data):
                if tmp_filename.endswith('.txt'):
                    tmp_group_name = tmp_filename[:-4]  # remove '.txt'
                    tmp_file_path = os.path.join(inp_data, tmp_filename)
                    with open(tmp_file_path, encoding='utf-8') as data_d:
                        out_data[tmp_group_name] = data_d.read()
        except FileNotFoundError:
            if inp_data == global_config_path or inp_data == global_database_path:
                raise FileNotFoundError(f"Database directory {inp_data} not found.")
            pass

    # debug print output
    # print(out_data)
    return out_data


def extract_groups(inp_data, delimiter='__'):
    """
    extracts list of all groups in database
    (used to search document for all groups and returns them inside of list)

    :param delimiter: Set of characters that define group set
    :param inp_data: String of document from which list is extracted
    :return: list of all groups and number of them
    """

    # input data is string with delimiters
    # _______________________________________
    if type(inp_data) == str:
        tmp_pattern = rf'({delimiter}\w+{delimiter})+'
        tmp_database = re.findall(tmp_pattern, inp_data, flags=0)
        out_group_list = [ins_str.strip(delimiter) for ins_str in tmp_database]

    # input data is dictionary with keys
    # _______________________________________
    elif type(inp_data) == dict:
        out_group_list = list(inp_data.keys())

    # _______________________________________
    else:
        raise TypeError(f'Type of {inp_data} not possible to compile')

    out_groups_length = len(out_group_list)

    # debug print output
    # print(out_group_list, out_groups_length)
    return out_group_list, out_groups_length


def extract_list(inp_data, group_name, delimiter='__'):
    """
    extracts list of elements inside of group and stores it inside of list
    (used to search document for certain group (Race) and returns all elements inside of it (dwarf, elf...))

    :param delimiter: Set of characters that define group set
    :param inp_data: String of document from which list is extracted
    :param group_name: Name of group for witch list is extracted
    :return: list of all elements in the group and length of that group list
    """

    # input data is string with delimiters
    # _______________________________________
    if type(inp_data) == str:
        tmp_pattern = rf'{delimiter}{group_name}{delimiter}(\n.+\s*)*/end'
        tmp_data = re.search(tmp_pattern, inp_data, flags=0)
        tmp_database_list = list(tmp_data.group(0).split('\n'))
        out_data_list = tmp_database_list[1:-1]

    # input data is dictionary with keys
    # _______________________________________
    elif type(inp_data) == dict:
        out_data_list = list(inp_data[group_name].split('\n'))

    # _______________________________________
    else:
        raise TypeError(f'Type of {inp_data} not possible to compile')

    out_data_list = [ins_element for ins_element in out_data_list if ins_element.strip()]
    out_list_length = len(out_data_list)

    # debug print output
    # print(out_data_list, out_list_length)
    return out_data_list, out_list_length


def clean_special_groups(group):
    """
    subtracts unnecessary characters from parameter: such as _by_ , and all other _
    than group all remaining words into list

    :param group: Parameter from which unnecessary characters are subtracted
    :return: List with group name and its specialties
    """

    tmp_group_string = group.replace('_by_', ' ')
    tmp_group_string = tmp_group_string.replace('_', ' ')
    tmp_group_and_specialties = re.findall(r'\w+', tmp_group_string)

    # debug print output
    # print(tmp_group_and_specialties)
    return tmp_group_and_specialties


def generate_all_combinations_of_sublists(subgroup_parameters_list, group_name):
    """
    generates all possible combinations of subgroup name for given set of conditional parameters

    :param group_name: name of group for which are made subgroup names
    :param subgroup_parameters_list: list of conditional parameters for given group
    :return: list of all possible subgroup names
    """

    out_subgroup_list = []
    out_subgroup_specificy_rating_list = []

    # selects amount of parameters that will build subgroup
    for tmp_num_of_groups in range(len(subgroup_parameters_list)):
        # builds index list form list so that sublist can be called by its index
        tmp_group_indexes_list = list(range(len(subgroup_parameters_list)))

        # runs for every combination of groups dependent on for loop above
        for tmp_comb_of_groups in itertools.combinations(tmp_group_indexes_list, (tmp_num_of_groups + 1)):

            # list in which all combination of parameters for subgroup are listed
            tmp_subgroup_parameters_list_copy = []

            # selects all groups from current combination
            for tmp_group_index in tmp_comb_of_groups:
                tmp_subgroup_parameters_list_copy.append(subgroup_parameters_list[tmp_group_index])

            # generates list with all parameters from current combination
            for tmp_subgroup_block in itertools.product(*tmp_subgroup_parameters_list_copy):

                tmp_list = []
                for tmp_parameter_index in range(len(tmp_subgroup_block)):
                    tmp_list.append(tmp_subgroup_block[tmp_parameter_index])
                out_subgroup_list.append(tmp_list)
                out_subgroup_specificy_rating_list.append(len(tmp_list))

    for tmp_subgroup_index in range(len(out_subgroup_list)):
        out_subgroup_list[tmp_subgroup_index] = ''.join(out_subgroup_list[tmp_subgroup_index]) + group_name

    # debug print output
    # print(out_subgroup_list, out_subgroup_specificy_rating_list)
    return out_subgroup_list, out_subgroup_specificy_rating_list


def merge_rarity_lists(base_list, added_list):
    """
    merge two lists, if one parameter is in both lists it takes rarity class form added_list

    :param base_list: list to which parameters are added
    :param added_list: list from which parameters are added
    :return: list that have parameters from both lists with rarity class prioritized by added_list
    """

    tmp_active_list = base_list + added_list

    for tmp_counter_base_list in range(len(base_list)):
        for tmp_counter_added_list in range(len(added_list)):

            # find rarity class of all parameters
            tmp_pattern = re.compile(r'(\(\w{1,3}\))$')
            tmp_base_list_rarity = re.findall(tmp_pattern, base_list[tmp_counter_base_list])
            tmp_added_list_rarity = re.findall(tmp_pattern, added_list[tmp_counter_added_list])

            # remove rarity class from parameter string
            try:
                tmp_base_list_element = base_list[tmp_counter_base_list].replace(tmp_base_list_rarity[0], '')
            except IndexError:
                tmp_base_list_element = base_list[tmp_counter_base_list]
            try:
                tmp_added_list_element = added_list[tmp_counter_added_list].replace(tmp_added_list_rarity[0], '')
            except IndexError:
                tmp_added_list_element = added_list[tmp_counter_added_list]

            # if there are multiple of the same parameter replace one in base list with the new one
            if tmp_base_list_element == tmp_added_list_element:
                tmp_active_list[tmp_counter_base_list] = added_list[tmp_counter_added_list]

    # remove duplicates from the list
    out_new_list = list(dict.fromkeys(set(tmp_active_list)))
    # debug print output
    # print(out_new_list)
    return out_new_list


class NonPlayableCharacter:

    def __init__(self):
        # defining local variables
        self.loc_all_groups_list = extract_groups(Database)[0]
        self.loc_special_groups = extract_groups(Config)

        # variables used for options inside of config.txt file
        # _______________________________________
        self.loc_rarity_classes = extract_list(Config, self.loc_special_groups[0][0])
        self.loc_optional_groups = extract_list(Config, self.loc_special_groups[0][1])
        self.loc_multiple_groups = extract_list(Config, self.loc_special_groups[0][2])
        self.loc_conditioned_groups = extract_list(Config, self.loc_special_groups[0][3])

        self.loc_all_rarity_classes = []

    # functions used for options inside of config.txt file
    # _______________________________________
    def rarity_classes(self, list_rarity_classes=False, get_rarity_corrected_list=False, group=None):
        """
        reads config.txt and connects rarity class defined in it with percentage given for it
        modifies given group or list in accordance to parameter rarity class for each parameter

        :param list_rarity_classes: if True reads config.txt and learns rarity classes
        :param get_rarity_corrected_list: if True modifies parameter list
        :param group: name of group or list for witch parameters are modified
        :return: list of parameters modified in accordance to their rarity class with
        """

        if list_rarity_classes:
            # all rarity classes are sorted in list with their percentage of occurring

            for tmp_rarity in self.loc_rarity_classes[0]:
                try:
                    self.loc_all_rarity_classes.append([clean_special_groups(tmp_rarity)[0],
                                                        int(clean_special_groups(tmp_rarity)[1])])
                except ValueError:
                    pass

        if get_rarity_corrected_list:

            tmp_all_active_parameters = []

            # check if input was database group or regular list
            if type(group) == str:
                try:
                    tmp_all_parameters_from_group = extract_list(Database, group)[0]
                except AttributeError:
                    tmp_all_parameters_from_group = []
                except KeyError:
                    tmp_all_parameters_from_group = []
            else:
                tmp_all_parameters_from_group = group

            # for every parameter in group check its rarity class and base on its chance to occur in active list,
            # form active lis of parameters
            for tmp_parameter in tmp_all_parameters_from_group:

                tmp_str_to_remove = ''
                tmp_pattern = re.compile(r'(\(\w{1,3}\))$')
                # extract rarity class  from parameter
                try:
                    tmp_rarity_class_str = re.findall(tmp_pattern, tmp_parameter)[0]
                    tmp_str_to_remove = tmp_rarity_class_str
                    tmp_rarity_class_str = tmp_rarity_class_str.replace('(', '')
                    tmp_rarity_class_str = tmp_rarity_class_str.replace(')', '')
                except IndexError:
                    tmp_rarity_class_str = ''

                # search if that rarity class is defined
                try:
                    tmp_rarity_class_index = [ins_rarity[0] for ins_rarity in self.loc_all_rarity_classes] \
                        .index(tmp_rarity_class_str)
                    tmp_rarity_class_int = self.loc_all_rarity_classes[tmp_rarity_class_index][1]
                except ValueError:
                    # check if rarity class is integer
                    try:
                        tmp_rarity_class_int = int(tmp_rarity_class_str)
                    # if not give it 100% chance of occurring
                    except ValueError:
                        tmp_rarity_class_int = 100

                if tmp_rarity_class_int >= random.randint(1, 100):
                    tmp_all_active_parameters.append(tmp_parameter.replace(tmp_str_to_remove, ''))

            return tmp_all_active_parameters

    def optional_groups(self):
        """
        check for optional groups and subtract unlucky ones from total parameter list

        :return: list of groups from witch are excluded unlucky groups
        """

        # input [[group, ''], [group_2, ''], [group_3, ''], ... ]
        # output [[group, ''], [group_3, ''], ... ]

        for tmp_parameter in self.loc_optional_groups[0]:
            # input Fear_by_80

            tmp_optional_group = clean_special_groups(tmp_parameter)
            # ['Fear', '80']
            tmp_optional_group_chance = random.randint(1, 100)

            # remove group from loc_groups_and_parameters_list if tmp_optional_group_chance
            # is less then chance specified in config.txt
            if int(tmp_optional_group[1]) <= tmp_optional_group_chance:
                try:
                    self.loc_groups_and_parameters_list.remove([tmp_optional_group[0], ''])
                except ValueError:
                    pass
                try:
                    self.loc_all_active_groups.remove(tmp_optional_group[0])
                except ValueError:
                    pass

    def multiple_groups(self):
        """
        check for groups that have multiple parameters than adds parameters in accordance to config file

        :return: added empty parameters to groups that deserve them
        """

        # input [[group, ''], [group_2, ''], [group_3, ''], ... ]
        # output [[group, '', ''], [group_2, '', '', ''], [group_3, ''], ... ]

        for tmp_parameter in self.loc_multiple_groups[0]:
            # input Race_by_20_min1max2

            tmp_multiple_group = clean_special_groups(tmp_parameter)
            # ['Race', '20', 'min1max2']
            # get range in which can be amount of parameters in group
            tmp_multiple_parameter_range = [int(n) for n in re.findall(r'\d+', tmp_multiple_group[2])]

            # count how many times will that parameter appear
            tmp_parameter_counter = tmp_multiple_parameter_range[0]

            tmp_optional_group_chance = random.randint(1, 100)
            tmp_counter = 0
            while (tmp_counter < (tmp_multiple_parameter_range[1] - tmp_multiple_parameter_range[0])) \
                    and (int(tmp_multiple_group[1]) >= tmp_optional_group_chance):
                tmp_parameter_counter += 1
                tmp_counter += 1
                tmp_optional_group_chance = random.randint(1, 100)

            # this is new list that will be substituted in place of old group parameter list
            tmp_multiple_parameter = [tmp_multiple_group[0]] + [''] * tmp_parameter_counter

            # if group is in group set than exchange its amount of parameters with new set
            try:
                tmp_groups_and_parameters_list = [ins_group[0] for ins_group in self.loc_groups_and_parameters_list]
                tmp_index = tmp_groups_and_parameters_list.index(tmp_multiple_group[0])

                self.loc_groups_and_parameters_list[tmp_index] = tmp_multiple_parameter
            except ValueError:
                pass

    def conditioned_groups(self, list_conditioned_groups=False, select_conditioned_parameters=False):
        """
        checks for conditioned groups and removes tam from normal set of groups then after
        all unconditioned groups are selected, checks if any of possible conditioned groups exists
        if so adds them to choosing pool

        :param list_conditioned_groups: if True removes conditioned group from normal set of groups
        :param select_conditioned_parameters: if True selects parameters from any existing conditioned group
        :return: list of all groups that are not conditioned and selects parameters for conditioned groups
        """

        for tmp_group in self.loc_conditioned_groups[0]:
            # input Name_by_Sex_Race
            tmp_group_and_subgroups = clean_special_groups(tmp_group)
            # ['Name', 'Sex', 'Race']
            tmp_active_group = tmp_group_and_subgroups[0]
            tmp_active_subgroups = tmp_group_and_subgroups[1:]

            if list_conditioned_groups:
                try:
                    self.loc_all_active_groups.remove(tmp_active_group)
                except ValueError:
                    pass

            if select_conditioned_parameters:

                # standard parameters for conditioned group
                # tmp_all_active_parameters = extract_list(Database, tmp_active_group)[0]
                tmp_all_active_parameters = []
                tmp_subgroup_parameters_list = []

                for tmp_subgroup in tmp_active_subgroups:

                    try:
                        tmp_subgroup_index = [ins_subgroup[0] for ins_subgroup in self.loc_groups_and_parameters_list] \
                            .index(tmp_subgroup)
                        tmp_subgroup_parameters_list.append(self.loc_groups_and_parameters_list[tmp_subgroup_index][1:])
                    except ValueError:
                        pass

                tmp_database = None

                # Database is string
                # _______________________________________
                if type(Database) == str:
                    tmp_database = Database

                # Database is directory
                # _______________________________________
                elif type(Database) == dict:
                    tmp_database_path = f'{global_database_path}/{tmp_active_group}'
                    try:
                        tmp_database = load_files(tmp_database_path)
                    except UnboundLocalError:
                        print(f'Directory {tmp_database_path} not found')
                        pass

                # _______________________________________
                else:
                    raise TypeError(f'Type of {Database} not possible to compile')

                tmp_subgroup_with_specificy_list = []
                tmp_subgroup_with_specificy_list += (generate_all_combinations_of_sublists
                                                     (tmp_subgroup_parameters_list, tmp_active_group))

                for tmp_specificy in range(max(tmp_subgroup_with_specificy_list[1]), -1, -1):

                    if not tmp_all_active_parameters:
                        # if subgroups exist
                        # _______________________________________
                        if tmp_specificy >= 1:
                            tmp_subgroup_list = [tmp_subgroup_with_specificy_list[0][ins_subgroup]
                                                 for ins_subgroup in [ins_specificy for ins_specificy, ins_element
                                                                      in enumerate(tmp_subgroup_with_specificy_list[1])
                                                                      if ins_element == tmp_specificy]]

                            for tmp_subgroup2 in tmp_subgroup_list:

                                try:  # try to grab data for subgroup
                                    tmp_subgroup_parameters = extract_list(tmp_database, tmp_subgroup2, '==')[0]
                                    tmp_all_active_parameters = \
                                        merge_rarity_lists(tmp_all_active_parameters, tmp_subgroup_parameters)
                                except AttributeError:
                                    # there is no subgroup with that name (legacy for '.txt' database)
                                    pass
                                except KeyError:  # there is no subgroup with that name in database directory
                                    # print(f'File {tmp_subgroup2} not found in{tmp_database}')
                                    try:  # check if name of subgroup is writen with underscore instead of space
                                        tmp_subgroup_parameters = \
                                            extract_list(tmp_database, tmp_subgroup2.replace(' ', r'_'), '==')[0]
                                        tmp_all_active_parameters = \
                                            merge_rarity_lists(tmp_all_active_parameters, tmp_subgroup_parameters)
                                    except KeyError:  # there is no data for subgroup (database as directory)
                                        # print(f'File {tmp_subgroup2} not found in{tmp_database_path}')
                                        pass

                        # id no subgroup was found
                        # _______________________________________
                        elif tmp_specificy <= 0:
                            tmp_all_active_parameters = extract_list(Database, tmp_active_group)[0]

                tmp_all_active_parameters = [ins_parameter for ins_parameter in tmp_all_active_parameters
                                             if ins_parameter.strip()]

                # print(tmp_all_active_parameters)
                self.select_parameter_for_groups([tmp_active_group], tmp_all_active_parameters)

    # _______________________________________

    def select_parameter_for_groups(self, active_groups=None, active_parameters=None):
        """
        used to select parameter for group

        :param active_groups: either single group name or list of groups
        :param active_parameters: either reads from database or list of parameters
        :return: list of groups with selected parameter
        """

        # default active_groups are ones which characteristics are not change with other functions
        if active_groups is None:
            active_groups = self.loc_all_active_groups

        for tmp_group in active_groups:

            # default active_parameters are ones for active_group
            if active_parameters is None:
                tmp_all_active_parameters = self.rarity_classes(False, True, tmp_group)
            else:
                tmp_all_active_parameters = self.rarity_classes(False, True, active_parameters)

            tmp_num_of_active_parameters = len(tmp_all_active_parameters)
            tmp_all_random_chances = []

            tmp_group_index = [ins_group_to_find[0] for ins_group_to_find in self.loc_groups_and_parameters_list] \
                .index(tmp_group)

            tmp_parameter_index = 0

            # for every element in sublist check for empty string, than replace it with random parameter
            for tmp_parameter in self.loc_groups_and_parameters_list[tmp_group_index]:

                if tmp_parameter == '' and tmp_parameter_index <= tmp_num_of_active_parameters:
                    # ensures that no single parameter will occur more than once
                    tmp_parameter_chance = random.randint(0, tmp_num_of_active_parameters - 1)
                    while tmp_parameter_chance in tmp_all_random_chances:
                        tmp_parameter_chance = random.randint(0, tmp_num_of_active_parameters - 1)

                    tmp_all_random_chances.append(tmp_parameter_chance)

                    self.loc_groups_and_parameters_list[tmp_group_index][tmp_parameter_index] = \
                        tmp_all_active_parameters[tmp_parameter_chance]

                tmp_parameter_index += 1

            self.loc_groups_and_parameters_list[tmp_group_index] = \
                [ins_parameter for ins_parameter in self.loc_groups_and_parameters_list[tmp_group_index] if
                 ins_parameter not in ['']]

    def __call__(self, force=[]):

        # check force and manipulate local groups
        if force:
            for tmp_force in force:
                tmp_force_group = tmp_force[0]
                # add forced group to all groups if not in
                self.loc_all_groups_list.append(tmp_force_group)
                self.loc_all_groups_list = list(set(self.loc_all_groups_list))

        # resetting non playable character specific lists every time it is called
        self.loc_all_rarity_classes = []  # list of all additional rarity classes
        self.loc_all_active_groups = self.loc_all_groups_list.copy()  # groups witch selection of parameters is not
        # conditioned by document config.txt
        self.loc_groups_and_parameters_list = []  # all groups and thai parameters in one list

        # add empty parameter to each group
        for tmp_group in self.loc_all_groups_list:
            self.loc_groups_and_parameters_list.append([tmp_group, ''])
            # [[group, ''], [group_2, ''], [group__3, ''], ... ]

        self.rarity_classes(True)
        if self.loc_optional_groups[0][0] != 'None':
            self.optional_groups()
        if self.loc_multiple_groups[0][0] != 'None':
            self.multiple_groups()
        if self.loc_conditioned_groups[0][0] != 'None':
            self.conditioned_groups(list_conditioned_groups=True)

        # Insert forced parameters
        if force:
            for tmp_force2 in force:
                tmp_force_group2 = [tmp_force2[0]]
                tmp_force_parameter2 = tmp_force2[1:]
                self.select_parameter_for_groups(active_groups=tmp_force_group2, active_parameters=tmp_force_parameter2)

        self.select_parameter_for_groups()

        if self.loc_conditioned_groups[0][0] != 'None':
            self.conditioned_groups(select_conditioned_parameters=True)

        return self.loc_groups_and_parameters_list


def print_non_playable_character(npc_data, print1=False, save=False):
    """
    prints out or saves character scheat

    :param print1: if True print character scheat
    :param save: if True save character scheat to save.txt
    :param npc_data: list of groups ad parameters of nps
    :return: printed or saved character scheat
    """

    tmp_max_group_length = max(len(ins_group[0]) for ins_group in npc_data) if npc_data else 10
    try:
        tmp_string = '\n'

        for tmp_group in npc_data:
            tmp_formatted_params = ', '.join(tmp_group[1:])
            tmp_string += f'{tmp_group[0]: <{tmp_max_group_length}}\t: {tmp_formatted_params} \n'

        tmp_string += r'-' * 120 + '\n'

        if print1:
            print(tmp_string)

        if save:
            with open('./save.txt', 'a', encoding='utf-8') as Save:
                Save.write(tmp_string)
    except TypeError:
        print('no NPC detected')


if __name__ == '__main__':

    # _______________________________________
    print('┌─┬┬─┬─┐┌──┐           ┌┐     \n'
          '││││┼│┌┘│┌─┼─┬─┬┬─┬┬┬─┐│└┬─┬┬┐\n'
          '││││┌┤└┐│└┐│┴┤│││┴┤┌┤┼└┤┌┤┼│┌┘\n'
          '└┴─┴┘└─┘└──┴─┴┴─┴─┴┘└──┴─┴─┴┘ \n')

    ControlDict = {
        'new': {'ControlList': ['n', 'new'],
                'Description': 'generate new NPC',
                'Help': 'Additional functions for \'new\':\n'
                        '--\'GroupName\'=\'Parameter\'\t- force parameter to npc for certain group'
                },

        'save': {'ControlList': ['s', 'save'],
                 'Description': 'save NPC',
                 'Help': ''
                 },

        'list': {'ControlList': ['ls', 'l', 'list'],
                 'Description': 'list data from database',
                 'Help': 'Additional functions for \'list\':\n'
                         '--\'GroupName\'\t- list all parameters of certain group\n'
                         '->\'GroupName\'\t- list all sub groups of certain group\n'
                         '--\'GroupName\'>\'SubGroupName\'\t- list all parameters of subgroup'
                 },

        'help': {'ControlList': ['help', 'h'],
                 'Description': 'shows help',
                 'Help': ''
                 },

        'escape': {'ControlList': ['esc', 'escape', 'close', 'q', 'quit'],
                   'Description': 'close program',
                   'Help': ''
                   }
    }

    def call_help(inp_control=None):
        if not inp_control:
            for inst_control_keys in ControlDict.keys():
                print(f'{ControlDict[inst_control_keys][list(ControlDict[inst_control_keys].keys())[0]][0]: <10}- '
                      f'{ControlDict[inst_control_keys][list(ControlDict[inst_control_keys].keys())[1]]}')
        else:
            tmp_control_list = ', '.join(ControlDict[inp_control][list(ControlDict[inp_control].keys())[0]])
            print(f'List of basic functions for \'{inp_control}\': \n'
                  f'{tmp_control_list: <{len(tmp_control_list) + 5}}- '
                  f'{ControlDict[inp_control][list(ControlDict[inp_control].keys())[1]]}')
            print(ControlDict[inp_control]['Help'])

    # _______________________________________
    Config = load_files(global_config_path)
    try:
        Database = load_files(global_database_path)
    except FileNotFoundError:
        try:
            Database = load_files(f'{global_database_path}.txt')
            print(f'database directory not found at {global_database_path}, you are using legacy version of database')
        except FileNotFoundError:
            raise FileNotFoundError
    NPC = NonPlayableCharacter()
    npc = None

    call_help()
    # _______________________________________
    while True:
        Control = input(':').split(' -')

        try:
            # escape
            if Control[0].lower() in ControlDict['escape']['ControlList']:
                break

            # new character
            elif Control[0].lower() in ControlDict['new']['ControlList']:
                # generate new character (no special conditions)
                if len(Control) == 1:
                    npc = NPC()
                    print_non_playable_character(npc, True)
                # generate character with forced conditions
                else:
                    ForceList = []
                    GenerateNpc = True

                    for NumOfControls in range(len(Control) - 1):
                        # force parameter
                        if Control[NumOfControls + 1].startswith('-'):
                            Force = Control[NumOfControls + 1][1:]
                            Force = Force.split('=')
                            ForceList.append(Force)
                        # help
                        elif Control[NumOfControls + 1] in ControlDict['help']['ControlList']:
                            call_help('new')
                            GenerateNpc = False

                    if GenerateNpc:
                        npc = NPC(force=ForceList)
                        print_non_playable_character(npc, True)

            # save character
            elif Control[0].lower() in ControlDict['save']['ControlList']:
                if len(Control) == 1:
                    print_non_playable_character(npc, False, True)
                else:
                    # help
                    if Control[1] in ControlDict['help']['ControlList']:
                        call_help('save')

            # list from database
            elif Control[0].lower() in ControlDict['list']['ControlList']:
                PrintList = []
                if len(Control) == 1:
                    PrintList = extract_groups(Database)[0]

                else:
                    # list parameters in group
                    if Control[1].startswith('-'):
                        Group = Control[1][1:]
                        try:    # first check if group is in database
                            PrintList = extract_list(Database, Group)[0]
                        except KeyError:
                            pass
                        if not PrintList:   # if there was no group found in database check is it a path
                            Group = Group.split('>')
                            try:    # try path to find list
                                PrintList = extract_list(load_files(f'{global_database_path}/{Group[0]}'), Group[1])[0]
                            except KeyError:
                                try:    # replace space with dash and try again to find a list
                                    print(Group[1].replace(' ', '_'))
                                    PrintList = extract_list(load_files(f'{global_database_path}'
                                                                        f'/{Group[0]}'), Group[1].replace(' ', '_'))[0]
                                except KeyError:
                                    pass
                    # list subgroups
                    elif Control[1].startswith('>'):
                        SubGroup = Control[1][1:]
                        SubGroupPath = rf'{global_database_path}/{SubGroup}'
                        SubGroupDatabase = load_files(SubGroupPath)
                        PrintList = extract_groups(SubGroupDatabase)[0]
                    # help
                    elif Control[1] in ControlDict['help']['ControlList']:
                        call_help('list')

                if PrintList:
                    for Element in PrintList:
                        print(Element)

            # popup help
            elif Control[0].lower() in ControlDict['help']['ControlList']:
                call_help()
                print('version: v.0.1.0')

            # wring input
            else:
                print('invalid input, try \'help\'')

        except IndexError:
            print('invalid input, try \'help\'')
