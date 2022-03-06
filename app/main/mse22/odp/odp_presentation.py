from app.main.odp.slide_odp import SlideODP
from app.main.presentation_basic import PresentationBasic
from app.main.mse22.odp.odf_document import OdfDocument


class OdpPresentation(PresentationBasic, OdfDocument):
    def __init__(self, filename):
        PresentationBasic.__init__(self, filename)
        OdfDocument.__init__(self, filename)
        self.add_slides()

    # Shouldn't this be private?..
    def add_slides(self):
        for slide in self._pages:
            self.slides.append(SlideODP(slide, self._auto_styles))


def main(args):
    presentation = OdpPresentation(args.filename)
    print("{0} instance has been successfully created from '{1}'".format(type(presentation), args.filename))
    print("These methods are now present in the OdpPresentation class:", dir(presentation))
    print("This class is derived from already existing PresentationBasic class defining a presentation interface",
          "and from OdfDocument class encapsulating initialization logic for (hopefully) all ODF files")
    print("Examined presentation has {0} slide(s) with titles: {1}"
          .format(presentation.get_len_slides(), presentation.get_titles()))
    print("Full presentation text:")
    print("\n".join(
        filter(
            lambda string: len(string) > 0,
            map(lambda string: string[:-2:], presentation.get_text_from_slides())
        )
    ))
