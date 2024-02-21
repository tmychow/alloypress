import os
import markdown
import yaml
import re
import datetime

import shutil

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

import latex2mathml.converter

from alloypress.stylesheet import css_content

class StaticSite:
    def __init__(self, input_dir = "./raw", output_dir = "./", custom_css = None):
        """
        Initialise SSG object with input and output directories.
        Prepare for a set of tags and a dictionary of pages.
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.custom_css = custom_css
        self.all_tags = set()
        self.pages = {}
        self.generated_html_files = set()
    
    def generate_stylesheet(self):
        """
        Generate default stylesheet in output directory.
        """
        if self.custom_css:
            shutil.copy(self.custom_css, os.path.join(self.output_dir, "style.css"))
        else:
            with open(os.path.join(self.output_dir, "style.css"), "w") as file:
                file.write(css_content)
    
    def collect_page_info(self):
        """
        Collect information from all markdown files in input directory.
        """
        # Loop through all files in input directory
        for dir_name, subdir_list, file_list in os.walk(self.input_dir):
            # For each markdown file in the directory
            # Take the yaml header and fill the dictionary
            # with the directory and filename as keys
            # and the yaml header as values
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
                            if new_dir not in self.pages:
                                self.pages[new_dir] = {}
                            self.pages[new_dir][fname] = header
    
    def create_index_page(self):
        """
        Generate a markdown index page for each directory.
        """
        # For each directory in the dictionary
        # Create an index markdown with the subdirectory name as title
        for dir_name in self.pages:
            stripped_dir = os.path.relpath(dir_name, self.input_dir)
            index_md = '''---
title: Index
---

# ''' + stripped_dir
            # Add all pages in reverse chronological order
            setoftags = set()
            page_list = ""
            for k, v in sorted(self.pages[dir_name].items(), key=lambda x: x[1].get('date') if x[1].get('date') is not None else datetime.date.min, reverse=True):
                if k != 'index.md':
                    page_list += f'''
<p class="''' + ' '.join(v.get('tags')) + '''"><a href="''' + stripped_dir + '''/''' + k.replace('.md', '.html') + '''">''' + v.get('title') + '''</a></p>'''
                    setoftags.update(v.get('tags'))
                    self.all_tags.update(v.get('tags'))
            # Add all tags as checkboxes
            toggles = ''
            for tag in sorted(setoftags):
                toggles += f'''
<input type="checkbox" id="''' + tag + '''" checked>
<label for="''' + tag + '''">''' + tag + '''</label>'''
            # Add all tags and page list to index markdown
            index_md += toggles
            index_md += page_list
            output_path = os.path.join(dir_name, 'index.md')
            with open(output_path, 'w') as file:
                file.write(index_md)
    
    def update_css_with_tags(self):
        """
        Update stylesheet with all tags.
        """
        with open(os.path.join(self.output_dir, "style.css"), "a") as file:
            tag_css = '''

'''
            # Add all tags to stylesheet, defaulting to hidden
            tag_css += ', '.join('.' + tag for tag in sorted(self.all_tags))
            tag_css += '''{
        display: none
}'''
            # Add all tags to stylesheet, visible when checkbox is checked
            for tag in sorted(self.all_tags):
                tag_css += f'''

    body:has(#{tag}:checked) .{tag} {{
        display: block
}}'''
            file.write(tag_css)

    def highlight_code_blocks(self, mkd):
        """
        Highlight code blocks in markdown.
        """
        code_blocks = re.findall(r"```{python}(.*?)```", mkd, re.DOTALL)
        for block in code_blocks:
            mkd = mkd.replace(f"```{{python}}{block}```", highlight(block, PythonLexer(), HtmlFormatter(style="monokai")))
        return mkd
    
    def convert_math_blocks(self, mkd):
        """
        Convert math blocks in LaTeX to MathML.
        """
        display_math_blocks = re.findall(r"\$\$(.*?)\$\$", mkd)
        for block in display_math_blocks:
            mkd = mkd.replace(f"$${block}$$", latex2mathml.converter.convert(rf"{block}", display="block"))
        inline_math_blocks = re.findall(r"\$(?!\$)(.*?[^\\])\$(?!\$)", mkd, re.DOTALL)
        for block in inline_math_blocks:
            mkd = mkd.replace(f"${block}$", latex2mathml.converter.convert(rf"{block}", display="inline"))
        return mkd

    def create_output_path(self, dir_name, fname):
        """
        Create output path for a given directory and filename.
        """
        relative_dir = os.path.relpath(dir_name, self.input_dir)
        dir_list = relative_dir.split('/')
        parent_dir = dir_list[0] if dir_list else ''
        if parent_dir == '.':
            output_path = os.path.join(self.output_dir, fname.replace('.md', '.html'))
        else:
            output_path = os.path.join(self.output_dir, parent_dir, fname.replace('.md', '.html'))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        return parent_dir, output_path
    
    def write_to_html(self, output_path, header, parent_dir, html):
        """
        Write HTML to file.
        """
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

    def check_for_orphans(self):
        """
        Checks for orphaned HTML files which no longer have a corresponding markdown file.
        """
        for dir_name, subdir_list, file_list in os.walk(self.output_dir):
            for fname in file_list:
                if fname.endswith(".html"):
                    file_path = os.path.join(dir_name, fname)
                    if file_path not in self.generated_html_files:
                        os.remove(file_path)
                        print(f"Removed {file_path}")

    def convert_to_html(self):
        """
        Convert markdown files to HTML.
        """
        # For each markdown file in the directory
        for dir_name, subdir_list, file_list in os.walk(self.input_dir):
            for fname in file_list:
                if fname.endswith(".md"):
                    file_path = os.path.join(dir_name, fname)
                    # Create output directory and filepath
                    parent_dir, output_path = self.create_output_path(dir_name, fname)
                    self.generated_html_files.add(output_path)
                    # If it is a new file or the markdown file has been edited
                    if not os.path.exists(output_path) or os.path.getmtime(file_path) > os.path.getmtime(output_path):
                        # Extract the markdown
                        # Highlight code blocks and convert math blocks
                        # Convert markdown to HTML
                        with open(file_path, 'r') as file:
                            content = file.read()
                            yaml_head, mkd = content.split('---')[1:3]
                            header = yaml.safe_load(yaml_head)
                            mkd = self.highlight_code_blocks(mkd)
                            mkd = self.convert_math_blocks(mkd)
                            html = markdown.markdown(mkd)
                        # Write HTML to file
                        self.write_to_html(output_path, header, parent_dir, html)
                        print(f"Generated {output_path}")
        self.check_for_orphans()
                            
    def generate(self):
        """
        Call all methods to generate static site.
        """
        self.generate_stylesheet()
        self.collect_page_info()
        self.create_index_page()
        self.update_css_with_tags()
        self.convert_to_html()