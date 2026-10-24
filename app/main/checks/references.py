import re


def literature_numbers(text):
    result = []
    for reference in re.findall(r'\[\^?[\d\s,;–—-]+\]', text):
        for part in re.split(r'[,;]', reference.strip('[]^')):
            part = part.strip()
            match = re.fullmatch(r'(\d+)\s*[-–—]\s*(\d+)', part)
            if match:
                start, end = map(int, match.groups())
                if 0 <= end - start <= 10000:
                    result.extend(range(start, end + 1))
            elif part.isdigit():
                result.append(int(part))
    return result
