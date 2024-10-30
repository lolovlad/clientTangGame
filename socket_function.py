import re


def extract_between_start_end(text):
    pattern = r'START(.*?)END'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return None