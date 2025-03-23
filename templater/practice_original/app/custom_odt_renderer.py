from secretary import Renderer
import re
from xml.dom.minidom import parseString

class CustomOdtRenderer(Renderer):
    """ Custom renderer inherited from Secretary's Renderer """
    def patch_xml(self, src_xml):
        """ Strip all unnecessary xml tags to have a raw xml understandable by jinja2 """

        # replace {{<some tags>jinja2 stuff<some other tags>}} by {{jinja2 stuff}}
        # same thing with {% ... %}
        # "jinja2 stuff" could a variable, a 'if' etc... anything jinja2 will understand
        def striptags(m):
            return re.sub('(<text:s/>)|(</text:[^>]*>.*?<text:[^>]*>)', '',
                            m.group(0), flags=re.DOTALL)
        src_xml = re.sub(r'{%(?:(?!%}).)*|{{(?:(?!}}).)*', striptags,
                            src_xml, flags=re.DOTALL)
        return src_xml


    def render_content_to_xml(self, template, **kwargs):
        """ Render the content of odt file (only the file content.xml) and return result as xml string. 
        This function is used when verifying the template"""
        self.files = self._unpack_template(template)
        self.render_vars = {}

        # Keep content and styles object since many functions or
        # filters may work with then
        self.content  = parseString(self.files['content.xml'])
        self.content = parseString(self.patch_xml(self.content.toxml()))
        self.content_original = self.content.toxml()
        # Render content.xml keeping just 'office:body' node.
        rendered_content = self._render_xml(self.content, **kwargs)
        self.content.getElementsByTagName('office:document-content')[0].replaceChild(
            rendered_content.getElementsByTagName('office:body')[0],
            self.content.getElementsByTagName('office:body')[0]
        )
        return self.content.toxml()


    def render(self, template, **kwargs):
        self.log.debug('Initing a template rendering')
        self.files = self._unpack_template(template)
        self.render_vars = {}

        # Keep content and styles object since many functions or
        # filters may work with then
        self.content  = parseString(self.files['content.xml'])
        self.content = parseString(self.patch_xml(self.content.toxml()))
        self.styles   = parseString(self.files['styles.xml'])
        self.manifest = parseString(self.files['META-INF/manifest.xml'])

        # Render content.xml keeping just 'office:body' node.
        rendered_content = self._render_xml(self.content, **kwargs)
        self.content.getElementsByTagName('office:document-content')[0].replaceChild(
            rendered_content.getElementsByTagName('office:body')[0],
            self.content.getElementsByTagName('office:body')[0]
        )

        # Render styles.xml
        self.styles = self._render_xml(self.styles, **kwargs)

        self.log.debug('Template rendering finished')

        self.files['content.xml']           = self.content.toxml().encode('ascii', 'xmlcharrefreplace')
        self.files['styles.xml']            = self.styles.toxml().encode('ascii', 'xmlcharrefreplace')
        self.files['META-INF/manifest.xml'] = self.manifest.toxml().encode('ascii', 'xmlcharrefreplace')

        document = self._pack_document(self.files)
        return document.getvalue()