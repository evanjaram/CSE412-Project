def find_missing_variables(**kwargs):
    return [name for name, value in kwargs.items() if value is None]