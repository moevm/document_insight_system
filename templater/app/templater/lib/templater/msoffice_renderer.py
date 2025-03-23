from secretary import Renderer
import re
from xml.dom.minidom import parseString
import zipfile
import io

class MsOfficeRenderer(Renderer):
    """ Custom renderer inherited from Secretary's Renderer """
    def patch_xml(self, src_xml):
        """ Strip all unnecessary xml tags to have a raw xml understandable by jinja2 """

        # replace {{<some tags>jinja2 stuff<some other tags>}} by {{jinja2 stuff}}
        # same thing with {% ... %}
        # "jinja2 stuff" could a variable, a 'if' etc... anything jinja2 will understand
        # def striptags(m):
        #     return re.sub('(<text:s/>)|(</text:[^>]*>.*?<text:[^>]*>)', '',
        #                     m.group(0), flags=re.DOTALL)
        # src_xml = re.sub(r'{%(?:(?!%}).)*|{{(?:(?!}}).)*', striptags,
        #                     src_xml, flags=re.DOTALL)
        return src_xml

    def _pack_document(self, files):
        # Store to a zip files in files
        self.log.debug('packing document')
        zip_file = io.BytesIO()

        zipdoc = zipfile.ZipFile(zip_file, 'a', zipfile.ZIP_DEFLATED)

        for fname, content in files.items():
            zipdoc.writestr(fname, content)

        self.log.debug('Document packing completed')

        return zip_file


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

            # self.log.error('Unescaped template was:\n{0}'.format(template_string))
            raise
        finally:
            self.log.debug('Rendering xml object finished')
