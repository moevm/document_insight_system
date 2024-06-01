# text1 is the suspect, text2 is potentially borrowed text

def compareTexts(text1, text2):
    match = 0
    for shingle in range(len(text1)):
        if text1[shingle] in text2:
            match += 1
    res = round(match / len(text1) * 100, 2)
    return res
