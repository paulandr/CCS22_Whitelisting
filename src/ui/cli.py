import os


def read_user_input(prompt: str, options: list = None) -> str:
    if options is not None:
        for i in range(0, len(options)):
            options[i] = str(options[i])

    user_in = input("> " + prompt + " ")

    if options is not None and user_in not in options:
        print("unexpected input! must be one of: " + str(options))
        user_in = read_user_input(prompt, options)

    return user_in


def read_user_input_yes_no(prompt: str) -> bool:
    user_in = read_user_input(prompt + " (Y/N)", ["Y", "y", "N", "n"])
    return user_in == "Y" or user_in == "y"


def file_json_parse(file: str) -> str:
    if os.path.isfile(file) and file.endswith(".json"):
        return os.path.abspath(file)
    else:
        raise TypeError(file)


def file_dir_parse(file: str) -> str:
    if os.path.isdir(file):
        return os.path.abspath(file) + "/"
    else:
        raise TypeError(file)


def file_parse(file: str) -> str:
    if os.path.isdir(file):
        return os.path.abspath(file) + "/"
    elif os.path.isfile(file) and file.endswith(".json"):
        return os.path.abspath(file)
    else:
        raise TypeError(file)
