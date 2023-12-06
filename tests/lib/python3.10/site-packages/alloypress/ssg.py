import os
import markdown
import yaml
import re
import pkg_resources
import datetime

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

import latex2mathml.converter

from alloypress.stylesheet import css_content
from alloypress.stylesheet import generate_stylesheet

all_tags = set()

def create_index(input_dir = "./raw", output_dir = "./"):
    pages = {}
    for dir_name, subdir_list, file_list in os.walk(input_dir):
        if os.path.dirname(dir_name) != ".":
            for fname in file_list:
                if fname.endswith(".md"):
                    file_path = os.path.join(dir_name, fname)
                    with open(file_path, 'r') as file:
                        content = file.read()
                        yaml_head, mkd = content.split('---')[1:3]
                        header = yaml.safe_load(yaml_head)
                        dir_components = dir_name.split('/')
                        new_dir = os.path.join(*dir_components[:3])
                        if new_dir not in pages:
                            pages[new_dir] = {}
                        pages[new_dir][fname] = header
    for dir_name in pages:
        stripped_dir = os.path.relpath(dir_name, input_dir)
        index_md = '''---
title: Index
---

# ''' + stripped_dir
        setoftags = set()
        page_list = ""
        for k, v in sorted(pages[dir_name].items(), key=lambda x: x[1].get('date') if x[1].get('date') is not None else datetime.date.min, reverse=True):
            if k != 'index.md':
                page_list += f'''
<p class="''' + ' '.join(v.get('tags')) + '''"><a href="./''' + k.replace('.md', '.html') + '''">''' + v.get('title') + '''</a></p>'''
                setoftags.update(v.get('tags'))
                all_tags.update(v.get('tags'))
        toggles = ''
        for tag in sorted(setoftags):
            toggles += f'''
<input type="checkbox" id="''' + tag + '''" checked>
<label for="''' + tag + '''">''' + tag + '''</label>'''
        index_md += toggles
        index_md += page_list
        output_path = os.path.join(dir_name, 'index.md')
        with open(output_path, 'w') as file:
            file.write(index_md)

def update_css(output_dir = "./"):
    with open(os.path.join(output_dir, "style.css"), "a") as file:
        tag_css = '''

'''
        tag_css += ', '.join('.' + tag for tag in sorted(all_tags))
        tag_css += '''{
    display: none
}'''
        for tag in sorted(all_tags):
            tag_css += f'''

body:has(#{tag}:checked) .{tag} {{
    display: block
}}'''
        file.write(tag_css)

def convert(input_dir = "./raw", output_dir = "./"):
    """Generate static site."""
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
                
                relative_dir = os.path.relpath(dir_name, input_dir)
                dir_list = relative_dir.split('/')
                parent_dir = dir_list[0] if dir_list else ''
                if parent_dir == '.':
                    output_path = os.path.join(output_dir, fname.replace('.md', '.html'))
                else:
                    output_path = os.path.join(output_dir, parent_dir, fname.replace('.md', '.html'))
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w') as file:
                    depth = output_path.count('/') - 1
                    relative_path = '../' * depth
                    file.write(r'''<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="''' + relative_path + '''style.css"/>
                <title>''' + header.get('title') + '''</title>
            </head>
            <!-- If you're reading this, say hi! -->
            <body class="''' + parent_dir + '''">
            <div class="container">
            <div class="center-pane">''')
                    file.write(html)
                    file.write(r'''</div></div><div class="footer"> <hr>hic sunt dracones</div></body></html>''')

def generate(input_dir = "./raw", output_dir = "./"):
    generate_stylesheet(css_content, output_dir)
    create_index(input_dir, output_dir)
    update_css(output_dir)
    convert(input_dir, output_dir)