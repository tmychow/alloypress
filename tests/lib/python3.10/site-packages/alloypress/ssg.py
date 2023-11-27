import os
import markdown
import yaml
import re
import pkg_resources

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

import latex2mathml.converter

from alloypress.stylesheet import generate_stylesheet

def generate(input_dir = "./raw", output_dir = "./", stylesheet = None):
    """Generate static site."""
    if stylesheet is None:
        generate_stylesheet(output_dir)
        stylesheet = "style.css"

    for dir_name, subdir_list, file_list in os.walk(input_dir):
        for fname in file_list:
            if fname.endswith(".md"):
                file_path = os.path.join(dir_name, fname)
                with open(file_path, 'r') as file:
                    content = file.read()
                    yaml_head, mkd = content.split('---')[1:3]
                    header = yaml.safe_load(yaml_head)

                    code_blocks = re.findall(r"```{python}(.*?)```", mkd, re.DOTALL)
                    for block in code_blocks:
                        mkd = mkd.replace(f"```{{python}}{block}```", highlight(block, PythonLexer(), HtmlFormatter(style="monokai")))

                    display_math_blocks = re.findall(r"\$\$(.*?)\$\$", mkd)
                    for block in display_math_blocks:
                        mkd = mkd.replace(f"$${block}$$", latex2mathml.converter.convert(rf"{block}", display="block"))

                    inline_math_blocks = re.findall(r"\$(?!\$)(.*?)\$(?!\$)", mkd, re.DOTALL)
                    for block in inline_math_blocks:
                        mkd = mkd.replace(f"${block}$", latex2mathml.converter.convert(rf"{block}", display="inline"))

                    html = markdown.markdown(mkd)
                
                output_path = os.path.join(output_dir, dir_name.replace(input_dir, '').lstrip('/'), fname.replace('.md', '.html'))
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w') as file:
                    file.write(r'''<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="style.css"/>
                <title>''' + header.get('title') + '''</title>
            </head>
            <!-- If you're reading this, say hi! -->
            <body>
            <div class="container">
            <div class="center-pane">''')
                    file.write(html)
                    file.write(r'''</div></div><div class="footer"> <hr>hic sunt dracones</div></body></html>''')