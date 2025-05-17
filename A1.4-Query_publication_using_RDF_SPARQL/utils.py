import urllib.parse as encode
import logging
import xml.sax as parser
import pathlib
import bz2
import io
import xml.etree.ElementTree as ET
import html

def initialize_rdf_document(file: str):
    with open(file, 'w', encoding='utf-8') as f:
        f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        f.write("\n")
        f.write("<rdf:RDF\n")
        f.write("\txmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\"\n")
        f.write("\txmlns:info=\"https://zbmath.org/infos#\">\n")
        f.write("\n")

def add_rdf_entry(file: str, desc, infos):
    with open(file, 'a', encoding='utf-8') as f:
        f.write(desc)
        for info in infos:
            f.write(f"\t{info}")
        f.write("\t\t</rdf:Description>\n")
        f.write("\n")

def finalize_rdf_document(file: str):
    with open(file, 'a', encoding='utf-8') as f:
        f.write("</rdf:RDF>")

def get_new_rdf(doc_id: str):
    return f"\t\t<rdf:Description rdf:about=\"https://zbmath.org/?q=an%3A{encode_value(doc_id)}\">\n"

def get_classification(val: str):
    return f"\t\t<info:classification rdf:resource=\"https://zbmath.org/classification/?q=cc%3A{encode_value(val)}\"/>\n"

def get_author(val: str):
    return f"\t\t<info:author rdf:resource=\"https://zbmath.org/authors/?q=ai%3A{encode_value(val)}\"/>\n"

def get_keyword(val: str):
    return f"\t\t<info:keyword rdf:resource=\"https://zbmath.org/?q=ut%3A{encode_value(val)}\"/>\n"

def get_publication_year(val: str):
    return f"\t\t<info:year>{val}</info:year>\n"

def encode_value(val: str) -> str:
    return encode.quote_plus(val)

class RDFContentHandler(parser.handler.ContentHandler):
    def __init__(self, output_filename):
        super().__init__()
        self.output_filename = output_filename
        self.counter = 0
        self.is_new_started = True
        self.current_tag = ""
        self.infos = []
        self._charBuffer = []
        self.desc = ""      

    def start_unit(self, element_name):
        relevant_tags = {'record', 'zbmath:document_id', 'zbmath:classification', 'zbmath:author_id', 'zbmath:keyword', 'zbmath:publication_year'}
        if element_name in relevant_tags:
            self.current_tag = element_name

    def characters(self, data):
        if self.current_tag == "record" and self.is_new_started:
            self.is_new_started = False

        if self.current_tag == 'zbmath:document_id':
            self.desc = get_new_rdf(str(data).strip())

        if self.current_tag == 'zbmath:classification':
            self.infos.append(get_classification(str(data).strip()))

        if self.current_tag == 'zbmath:author_id':
            self.infos.append(get_author(str(data).strip()))

        if self.current_tag == 'zbmath:keyword':
            self.infos.append(get_keyword(str(data).strip()))

        if self.current_tag == 'zbmath:publication_year':
            self.infos.append(get_publication_year(str(data).strip()))

    def end_unit(self, element_name):
        if element_name == "record" and not self.is_new_started:
            add_rdf_entry(self.output_filename, self.desc, self.infos)
            self.desc = ""
            self.infos = []
            self.is_new_started = True
            self.current_tag = ""
        elif element_name in ['zbmath:document_id', 'zbmath:classification', 'zbmath:author_id', 'zbmath:keyword', 'zbmath:publication_year']:
            self.current_tag = ""

def find_xml_start(content):
    xml_start = content.find(b'<?xml')
    if xml_start == -1:
        xml_start = content.find(b'<OAI-PMH')
    if xml_start == -1:
        raise ValueError("Could not find the start of XML content")
    return content[xml_start:]

def buildRdfDataFile(filename, output_filename):
    abs_file_path = pathlib.Path(filename).absolute()
    initialize_rdf_document(output_filename)
    
    with bz2.open(abs_file_path, "rb") as f:
        xml_started = False
        xml_parser = parser.make_parser()
        handler = RDFContentHandler(output_filename)
        xml_parser.setContentHandler(handler)
        
        while True:
            chunk = f.read(1024 * 1024)  # Read larger chunks, e.g., 1MB
            if not chunk:
                break
            
            if not xml_started:
                xml_start_index = chunk.find(b'<?xml')
                if xml_start_index != -1:
                    xml_started = True
                    chunk = chunk[xml_start_index:]
                else:
                    continue            
            try:
                xml_parser.feed(chunk)
            except Exception as e:
                logging.error(f"Error parsing XML chunk: {str(e)}")
    
    finalize_rdf_document(output_filename)
    logging.info("RDF generation completed.")

class QueryTask:
    def __init__(self, id, type, queries, before=None, after=None):
        self.id = id
        self.type = type
        self.queries = queries
        self.solutions = []
        self.before = before
        self.after = after

    def __repr__(self):
        return f"Problem = id: {self.id}; type: {self.type}; queries: {self.queries}, " \
               f"| {self.before} | {self.after}, sol = {self.solutions}"

def parse_problem_xml(name):
    f = ET.parse(name)
    p = f.findall("Problem")

    problems = []

    for pr in p:
        values = pr.findall("*")
        queries = []
        problem_type = pr.get("type")
        by = None
        ay = None
        
        for v in values:
            if v.tag == "Author" or v.tag == "Keyword" or v.tag == "Classification":
                queries.append(v.text)
            elif v.tag == "BeforeYear":
                by = v.text
            elif v.tag == "AfterYear":
                ay = v.text

        problems.append(QueryTask(pr.get("id"), problem_type, queries, by, ay))

    return problems

def generate_solution_xml(problems, solution_filename):
    with open(solution_filename, "w", encoding='utf-8') as f:
        f.write("<Solutions>\n")
        for p in problems:
            f.write(f"  <Solution id=\"{p.id}\">\n")
            escaped_query = html.escape(p.query)
            f.write(f"    <Query>{escaped_query}</Query>\n")
            if p.type == 'keywords':
                for s in p.solutions:
                    f.write(f"    <Keyword>{s}</Keyword>\n")
            elif p.type == 'msc-intersection':
                for s in p.solutions:
                    f.write(f"    <Paper>{s}</Paper>\n")
            elif p.type == 'top-authors':
                for author, count in p.solutions:
                    f.write(f"\t\t<Author count=\"{count}\">{author}</Author>\n")
            f.write("  </Solution>\n")
        f.write("</Solutions>\n")
    print(f"{solution_filename} is created with all solutions.")
