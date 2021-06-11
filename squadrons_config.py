import argparse
import math
import keyboard_scancodes
from os.path import expandvars
from squadrons_text_map import joystick_text_map, kbm_text_map


# https://stackoverflow.com/a/11570745
def paths(tree, cur=()):
    if not tree or not isinstance(tree, dict):
        yield cur+(tree,)
    else:
        for n, s in tree.items():
            for path in paths(s, cur+(n,)):
                yield path

# Mashup of a couple stackoverflow responses
# https://stackoverflow.com/a/29652561
# https://stackoverflow.com/a/31998950


def gen_dict_extract_value(key, value, var, path):
    if not path:
        path = []
    if hasattr(var, 'items'):
        for k, v in var.items():
            if k == key and v == value:
                yield path
            if isinstance(v, dict):
                local_path = path[:]
                local_path.append(k)
                for result in gen_dict_extract_value(key, value, v, local_path):
                    yield result


def gen_dict_extract(key, var):
    if hasattr(var, 'items'):
        for k, v in var.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                yield from gen_dict_extract(key, v)


def parseFile(path):
    print(path)
    newdata = ''
    with open(path, "r") as f:
        data = f.read()
        newdata = data.splitlines()

    result = dict()
    for line in newdata:
        val = line.split(' ', 1)[1]
        line = line.split(' ')[0]

        leaf = result
        for item in line.split('.')[:-1]:
            if item not in leaf.keys():
                leaf[item] = dict()
            leaf = leaf[item]

        leaf[line.split('.')[-1]] = val

    result['GstInput']['JoystickDevice0'] = 'To Be Determined Device'

    # with open(path + ".json", "w") as outfile:
    #     json.dump(result, outfile, indent=4)

    return result


def translate_keyboard_id(key_id):
    val = keyboard_scancodes.LOOKUP[key_id]['leaf'][1]
    return "KEY_" + val


def translate_controller_id(button_id):
    # Gamepad Preset
    # 0 = Custom
    # 1 = Standard
    # 2 = Aviator
    # 3 = Southpaw

    # The items below match the button # from windows usb game controller config and the corresponding SWS Button/Axis
    # For a third part XBox One controller

    # dpad - POV_U : SWS Button 0
    if button_id == 0:
        return "POV_1_U"
    # dpad - POV_D : SWS Button 1
    if button_id == 1:
        return "POV_1_D"
    # dpad - POV_L : SWS Button 2
    if button_id == 2:
        return "POV_1_L"
    # dpad - POV_R : SWS Button 3
    if button_id == 3:
        return "POV_1_R"

    # Y - 4 : SWS Button 4
    if button_id == 4:
        return "BUTTON_4"
    # A - 1 : SWS Button 5
    if button_id == 5:
        return "BUTTON_1"
    # X - 3 : SWS Button 6
    if button_id == 6:
        return "BUTTON_3"
    # B - 2 : SWS Button 7
    if button_id == 7:
        return "BUTTON_2"
    # MISSING SWS Button 8
    if button_id == 8:
        return "BUTTON_UNKNOWN_8"
    # MISSING SWS Button 9
    if button_id == 9:
        return "BUTTON_UNKNOWN_9"

    # left joy click - 9 : SWS Button 10
    if button_id == 10:
        return "BUTTON_9"
    # right joy click - 10 : SWS Button 11
    if button_id == 11:
        return "BUTTON_10"
    # Menu/Start - 8 : SWS Button 12
    if button_id == 12:
        return "BUTTON_8"
    # View/Back - 7 : SWS Button 13
    if button_id == 13:
        return "BUTTON_7"
    # left trigger - Z+ : SWS Button 14
    if button_id == 14:
        return "AXIS_Z_P"
    # right trigger - Z- : SWS Button 15
    if button_id == 15:
        return "AXIS_Z_N"
    # LB - 5 : SWS Button 16
    if button_id == 16:
        return "BUTTON_5"
    # RB - 6 : SWS Button 17
    if button_id == 17:
        return "BUTTON_6"

    return "BUTTON_UNKNOWN_" + str(button_id)


def translate_controller_axis_id(axis_id):
    # left joy X+ : Axis 2
    # left joy X- : Axis 4
    # left joy Y+ : Axis 3
    # left joy Y- : Axis 5
    # right joy Rx+ : Axis 8
    # right joy Rx- : Axis 10
    # right joy Ry+ : Axis 9 ? In game this is up but usb controller shows pressing up is negative axis?
    # right joy Ry- : Axis 11 ? In game this is down but usb controller shows pressing down is positive axis?
    # TODO: possibly add negate as a parameter. Negate indicates if the axis is negative aka Left or Down
    if axis_id == 8:
        return "AXIS_RX_P"
    if axis_id == 10:
        return "AXIS_RX_N"
    if axis_id == 9:
        return "AXIS_RY_N"
    if axis_id == 11:
        return "AXIS_RY_P"
    if axis_id == 2:
        return "AXIS_X_P"
    if axis_id == 4:
        return "AXIS_X_N"
    if axis_id == 5:
        return "AXIS_Y_N"
    if axis_id == 3:
        return "AXIS_Y_P"

    return "AXIS_UNKNOWN_" + str(axis_id)


def translate_mouse_axis_id(axis_id):
    # Mouse X+ : Axis 2
    # Mouse X- : Axis 4
    # Mouse Y+ : Axis 3
    # Mouse Y- : Axis 5
    # Scroll+ : Axis 14
    # Scroll- : Axis 15

    # TODO: possibly add negate as a parameter. Negate indicates if the axis is negative aka Left or Down
    if axis_id == 2:
        return "AXIS_X_P"
    if axis_id == 4:
        return "AXIS_X_N"
    if axis_id == 5:
        return "AXIS_Y_N"
    if axis_id == 3:
        return "AXIS_Y_P"
    if axis_id == 14:
        return "AXIS_SCROLL_P"
    if axis_id == 15:
        return "AXIS_SCROLL_N"

    return "AXIS_UNKNOWN_" + str(axis_id)


def translate_button_id(button_id):
    # Axis: X-Axis: 8/10
    # Y-Axis: 9/11
    # Axis 26 is unmapped Axis indicator
    #
    # Buttons
    # UNKNOWN = 1-13
    # (hunch is 2-5, 8-11 are skipped because those are also axis values or maybe reserved for controllers)
    #
    # Slider0 = 14/15
    # Slider1 = 16/17
    # UNKNOWN = 18-21
    # Button 1-18 = 22-39
    # Z-Axis = 40/41
    # Rx = 42/43
    # Ry = 44/45
    # Rz = 46/47
    # POV1 48-51
    # POV2 52-55
    # POV3 56-59
    # POV4 60-63
    # Button 19-127 = 64-173
    # Button 174 is unmapped button indicator

    if button_id == 14:
        return "AXIS_SLIDER_0_P"
    if button_id == 15:
        return "AXIS_SLIDER_0_N"
    if button_id == 16:
        return "AXIS_SLIDER_1_P"
    if button_id == 17:
        return "AXIS_SLIDER_1_N"
    if 22 <= button_id <= 39:
        return "BUTTON_" + str(button_id - 21)
    if 64 <= button_id <= 173:
        return "BUTTON_" + str(button_id - 45)
    if button_id == 40:
        return "AXIS_Z_P"
    if button_id == 41:
        return "AXIS_Z_N"
    if button_id == 42:
        return "AXIS_RX_P"
    if button_id == 43:
        return "AXIS_RX_N"
    if button_id == 44:
        return "AXIS_RY_P"
    if button_id == 45:
        return "AXIS_RY_N"
    if button_id == 46:
        return "AXIS_RZ_P"
    if button_id == 47:
        return "AXIS_RZ_N"
    if 48 <= button_id <= 63:
        pov_num = math.floor((button_id-48) / 4) + 1
        dir_num = button_id % 4
        if dir_num == 0:
            direction = 'U'
        elif dir_num == 1:
            direction = 'D'
        elif dir_num == 2:
            direction = 'L'
        else:
            direction = 'R'

        return "POV_" + str(pov_num) + '_' + direction

    return "BUTTON_UNKNOWN_" + str(button_id)


def translate_axis_id(axis_id):
    # TODO: possibly add negate as a parameter. Negate indicates if the axis is negative aka Left or Down
    if axis_id == 8:
        return "AXIS_X_P"
    if axis_id == 10:
        return "AXIS_X_N"
    if axis_id == 9:
        return "AXIS_Y_N"
    if axis_id == 11:
        return "AXIS_Y_P"

    return "AXIS_UNKNOWN_" + str(axis_id)


if __name__ == '__main__':
    input_parser = argparse.ArgumentParser()
    input_parser.add_argument("-p", "--profile_path", help="path to ProfileOptions_profile_synced file. "
                              + "By default this value is set to the Steam path %%userprofile%%\\Documents\\"
                              + "STAR WARS Squadrons Steam\\settings\\ProfileOptions_profile_synced",
                              default=expandvars("%userprofile%\\Documents\\STAR WARS Squadrons Steam\\settings\\"
                                                 + "ProfileOptions_profile_synced"))
    input_parser.add_argument("-m", "--mouse", help="Output Mouse bindings", action="store_true")
    input_parser.add_argument("-k", "--keyboard", help="Output Keyboard bindings", action="store_true")
    input_parser.add_argument("-c", "--controller", help="Output Controller bindings", action="store_true")
    input_parser.add_argument("-s", "--stick", help="Output Flight Stick bindings", action="store_true")
    args = input_parser.parse_args()
    profiles = parseFile(args.profile_path)

    if not (args.mouse or args.keyboard or args.controller or args.stick):
        output_all = True
    else:
        output_all = False

    buttons = dict()
    axis = dict()
    if int(profiles['GstKeyBinding']['InputDataVersion']) < 4:
        unmapped_button = 86
        unmapped_mouse_button = 8
        unmapped_axis = 26
        unmapped_keyboard_button = 0
    else:
        unmapped_button = 174
        unmapped_mouse_button = 8
        unmapped_axis = 26
        unmapped_keyboard_button = 0

    device_ids = sorted(set(gen_dict_extract('deviceid',
                                      profiles['GstKeyBinding']['IncomStarshipInputConcepts'])))

    device_types = sorted(set(gen_dict_extract('type',
                                      profiles['GstKeyBinding']['IncomStarshipInputConcepts'])))
    for device_type in device_types:
        for device_id in device_ids:
            button_list = list()
            axis_list = list()
            header_printed = False

            if device_type == '-1' and device_id == '-1':
                continue

            if device_type == '0' and not (output_all or args.mouse):
                continue
            elif device_type == '1' and not (output_all or args.controller):
                continue
            elif device_type == '2' and not (output_all or args.keyboard):
                continue
            elif device_type == '3' and not (output_all or args.stick):
                continue
            elif device_type == '-1' and not (output_all or args.stick):
                continue

            if device_id == '-1':
                if device_type == '0':
                    profiles['GstInput']['JoystickDevice' + str(int(device_id) + 1)] = 'Mouse'
                elif device_type == '1':
                    profiles['GstInput']['JoystickDevice' + str(int(device_id) + 1)] = 'Controller'
                elif device_type == '2':
                    profiles['GstInput']['JoystickDevice' + str(int(device_id) + 1)] = 'Keyboard'
                else:
                    profiles['GstInput']['JoystickDevice' + str(int(device_id) + 1)] = 'To Be Determined Device'


            for x in gen_dict_extract_value('deviceid', device_id,
                                            profiles['GstKeyBinding']['IncomStarshipInputConcepts'], None):
                ret = profiles['GstKeyBinding']['IncomStarshipInputConcepts']
                for k in x:
                    ret = ret[k]

                if ret['type'] == device_type:
                    if not header_printed:
                        header_printed = True
                        print("********************************************")
                        print(profiles['GstInput']['JoystickDevice' + str(int(device_id) + 1)])
                        print("********************************************")
                    if ret['negate'] == '1':
                        axis_direction = '_N'
                    else:
                        axis_direction = '_P'

                    if ret['type'] == '0' or ret['type'] == '2':  # Mouse or keyboard
                        try:
                            event_desc = kbm_text_map[x[0] + axis_direction]
                        except KeyError:
                            event_desc = kbm_text_map[x[0]]
                    elif ret['type'] == '1' or ret['type'] == '3':  # Controller or HOTAS
                        try:
                            event_desc = joystick_text_map[x[0] + axis_direction]
                        except KeyError:
                            event_desc = joystick_text_map[x[0]]
                    else:
                        event_desc = ''

                    if ret['type'] == '0':  # Mouse
                        if ret['axis'] != str(unmapped_axis):
                            print(translate_mouse_axis_id(int(ret['axis'])), ":::", event_desc)
                            axis_list.append(int(ret['axis']))
                        elif ret['button'] != str(unmapped_mouse_button):
                            print('BUTTON_' + ret['button'], ":::", event_desc)
                            button_list.append(int(ret['button']))
                    elif ret['type'] == '1':  # Controller
                        if ret['axis'] != str(unmapped_axis):
                            print(translate_controller_axis_id(int(ret['axis'])), ":::", event_desc)
                            axis_list.append(int(ret['axis']))
                        elif ret['button'] != str(unmapped_button):
                            print(translate_controller_id(int(ret['button'])), ":::", event_desc)
                            button_list.append(int(ret['button']))
                    elif ret['type'] == '2':  # Keyboard
                        if ret['button'] != str(unmapped_keyboard_button):
                            print(translate_keyboard_id(int(ret['button'])), ":::", event_desc)
                            button_list.append(int(ret['button']))
                    elif ret['type'] == '3':  # HOTAS
                        if ret['axis'] != str(unmapped_axis):
                            print(translate_axis_id(int(ret['axis'])), ":::", event_desc)
                            axis_list.append(int(ret['axis']))
                        elif ret['button'] != str(unmapped_button):
                            print(translate_button_id(int(ret['button'])), ":::", event_desc)
                            button_list.append(int(ret['button']))


            buttons[device_id] = button_list
            axis[device_id] = axis_list
