import re

def find_missing_variables(**kwargs):
    return [name for name, value in kwargs.items() if value is None]

def is_valid_date(date):
    pattern = r'^\d{4}-\d{2}-\d{2}$'

    if re.match(pattern, date):
        return True
    return False