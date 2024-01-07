# alloypress

A Python static site generator which I use for [my personal website](https://tmychow.com).

Made using the [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

## Getting Started

Install via `pip install alloypress`.

Run the following Python code in the root directory of your site:

```
from alloypress import StaticSite

ssg = StaticSite()
ssg.generate()
```

An example of this can be seen in `./tests`. It will take every `.md` file in `./raw` and generate the HTML in `./`.

## Features 

The high-level approach of `alloypress` is serve static HTML and CSS files, rendering nothing client-side.

It supports:

- Jon Gruber's original [Markdown syntax](https://daringfireball.net/projects/markdown/syntax) via `markdown`
- LaTeX via `latex2mathml` inside `$` and `$$` delimiters
- Syntax highlighting for Python via `pygments`
- Sidenotes which are displayed inline on narrow devices
- Sortable and tag-filtered index page for each top-level folder
- Only re-generates HTML if the Markdown has been modified, and deletes orphaned HTML files

## To Be Implemented

- [ ] Support for other languages via `pygments`
- [ ] Sidebar-based navigation
- [ ] Embedding-based search across all pages
- [ ] Post summaries on the index page via yaml frontmatter
- [ ] More coming soon...