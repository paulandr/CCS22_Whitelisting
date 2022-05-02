def set_difference(list_a: list, list_b: list) -> set:
    set_a = set(list_a)
    set_b = set(list_b)

    return set_a.difference(set_b)


def set_intersection(list_a: list, list_b: list) -> set:
    set_a = set(list_a)
    set_b = set(list_b)

    return set_a.intersection(set_b)
