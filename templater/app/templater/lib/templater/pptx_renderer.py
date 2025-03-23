from secretary import Renderer
import re
from xml.dom.minidom import parseString
from .msoffice_renderer import MsOfficeRenderer


class PptxRenderer(MsOfficeRenderer):
    
    def render_content_to_xml(self, template, **kwargs):
        """ Render the content of odt file (only the file content.xml) and return result as xml string. 
        This function is used when verifying the template"""
        self.files = self._unpack_template(template)
        fullContent = ""
        self.content_original = ""
        for fname, content in self.files.items():
            if(bool(re.match(r"^ppt/slides/[^/]*.xml$", fname))):
                decoded = content.decode("utf-8")
                self.content_original += decoded
                slide = parseString(self.patch_xml(decoded))
                slide = self._render_xml_body(slide, **kwargs)
                fullContent += slide.toxml()
        return fullContent


    def render(self, template, **kwargs):
        self.log.debug('Initing a template rendering')
        self.files = self._unpack_template(template)

        for fname, content in self.files.items():
            if(bool(re.match(r"^ppt/slides/[^/]*.xml$", fname))):
                decoded = content.decode("utf-8")
                slide = parseString(self.patch_xml(decoded))
                slide = self._render_xml_body(slide, **kwargs)
                self.files[fname] = slide.toxml().encode('ascii', 'xmlcharrefreplace')

        self.log.debug('Template rendering finished')

        document = self._pack_document(self.files)
        return document.getvalue()