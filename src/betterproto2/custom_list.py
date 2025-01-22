class List(list):
    """
    This list is used in compiled messages instead of the standard Python `list`.

    Having a separate class makes it easier for users to extend betterproto by monkey-patching this type if needed.

    TODO use it to simplify functions such as to_dict, __bytes__, etc.
    """

    pass
