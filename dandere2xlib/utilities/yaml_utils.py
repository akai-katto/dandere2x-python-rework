import yaml


def get_options_from_section(section: yaml, ffmpeg_command=False):
    def list_to_string(list_input: list):
        return_str = ''
        for item in list_input:
            return_str += item + ","

        return return_str[:-1]

    execute = []

    for item in section:
        if section[item] is not None:

            # if the item is any value but 'true', append both the key and value
            if section[item] is not True:

                if type(section[item]) is list and ffmpeg_command is True:
                    execute.append(str(item))
                    execute.append(list_to_string(section[item]))

                else:
                    execute.append(str(item))
                    execute.append(str(section[item]))

            # if it's set to true, simply append the key
            else:
                execute.append(str(item))

    return execute