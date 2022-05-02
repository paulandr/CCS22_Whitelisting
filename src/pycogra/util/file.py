import os.path


def get_filename(file: str, add_extension: bool = False) -> str:
    print(file)
    assert(os.path.isfile(file))
    result: str = os.path.basename(file)

    if not add_extension:
        result = result[0:result.find('.')]

    return result
