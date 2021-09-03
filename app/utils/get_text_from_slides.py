def get_text_from_slides(presentation, keyword):
    found_slides = []
    for i, title in enumerate(presentation.get_titles(), 1):
        if str(title).lower().find(str(keyword).lower()) != -1:
            found_slides.append(presentation.get_text_from_slides()[i - 1])
    return ' '.join(found_slides)
