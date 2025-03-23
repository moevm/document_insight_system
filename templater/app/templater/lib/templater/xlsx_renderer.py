from secretary import Renderer
import re
from xml.dom.minidom import parseString
from .msoffice_renderer import MsOfficeRenderer

class XlsxRenderer(MsOfficeRenderer):

    def render_content_to_xml(self, template, **kwargs):
        self.files = self._unpack_template(template)
        self.content_original = self.files['xl/sharedStrings.xml'].decode('utf-8')
        content = self.content_original
        slide = parseString(self.patch_xml(content))
        slide = self._render_xml_body(slide, **kwargs)
        return slide.toxml()


    def render(self, template, **kwargs):
        self.files = self._unpack_template(template)

        slide = parseString(self.patch_xml(self.files['xl/sharedStrings.xml'].decode('utf-8')))
        slide = self._render_xml_body(slide, **kwargs)
        self.files['xl/sharedStrings.xml'] = slide.toxml().encode('ascii', 'xmlcharrefreplace')

        self.log.debug('Template rendering finished')

        document = self._pack_document(self.files)
        return document.getvalue()