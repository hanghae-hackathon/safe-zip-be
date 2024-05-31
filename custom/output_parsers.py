from langchain_core.output_parsers import BaseOutputParser
from IPython.display import display, HTML

class HTMLOutputParser(BaseOutputParser):
    def parse(self, input):
        html_content = f"<pre style='font-size: 14px; line-height: 1.6;'>{input}</pre>"
        return display(HTML(html_content))