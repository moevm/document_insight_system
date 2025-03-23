from secretary import Renderer
import re
from xml.dom.minidom import parseString

class OpenOfficeRenderer(Renderer):
    """ Custom renderer inherited from Secretary's Renderer """
    def patch_xml(self, src_xml):
        """ Strip all unnecessary xml tags to have a raw xml understandable by jinja2 """

        # replace {{<some tags>jinja2 stuff<some other tags>}} by {{jinja2 stuff}}
        # same thing with {% ... %}
        # "jinja2 stuff" could a variable, a 'if' etc... anything jinja2 will understand
        def striptags(m):
            return re.sub('(<text:s[^>]*/>)|(</text:[^>]*>.*?<text:[^>]*>)', '',
                            m.group(0), flags=re.DOTALL)
        src_xml = re.sub(r'{%(?:(?!%}).)*|{{(?:(?!}}).)*', striptags,
                            src_xml, flags=re.DOTALL)
        return src_xml


    def _render_xml_body(self, xml_document, **kwargs):
        try:
            # self.template_images = dict()
            # self._prepare_document_tags(xml_document)
            xml_source = xml_document.toxml()
            xml_source = xml_source.encode('ascii', 'xmlcharrefreplace')
            jinja_template = self.environment.from_string(
                self._unescape_entities(xml_source.decode('utf-8'))
            )

            result = jinja_template.render(**kwargs)

            final_xml = parseString(result.encode('ascii', 'xmlcharrefreplace'))
            # if self.template_images:
            #     self.replace_images(final_xml)

            return final_xml
        except:
            self.log.error('Error rendering template:\n%s',
                           xml_document.toprettyxml(), exc_info=True)
            print(xml_document.toprettyxml())
            # self.log.error('Unescaped template was:\n{0}'.format(template_string))
            raise
        finally:
            self.log.debug('Rendering xml object finished')


    def render_content_to_xml(self, template, **kwargs):
        """ Render the content of odt file (only the file content.xml) and return result as xml string. 
        This function is used when verifying the template"""
        self.files = self._unpack_template(template)
        self.render_vars = {}

        # Keep content and styles object since many functions or
        # filters may work with then
        self.content = parseString(self.patch_xml(self.files['content.xml'].decode("utf-8")))
        self.content_original = self.content.toxml()
        # Render content.xml keeping just 'office:body' node.
        rendered_content = self._render_xml_body(self.content, **kwargs)
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
        # self.content  = parseString(self.files['content.xml'])
        # self.content = parseString(self.patch_xml(self.content.toxml()))

        self.content = parseString(self.patch_xml(self.files['content.xml'].decode("utf-8")))
        self.styles   = parseString(self.files['styles.xml'])
        self.manifest = parseString(self.files['META-INF/manifest.xml'])

        # Render content.xml keeping just 'office:body' node.
        rendered_content = self._render_xml_body(self.content, **kwargs)
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