# alloypress

My Python static site generator. It supports markdown, latex, syntax highlighting and sidenotes, using only html and css with no client-side rendering.

# features

- supports jon gruber's original markdown syntax
- supports latex via latex2mathml using $ delimiters
- supports syntax highlighting for python, and other languages soon
- supports sidenotes in both wide and narrow devices, with the latter displayed inline by a button

# to be added

- mdn in drafts aren't generated
- an index site with list of subposts is always generated for each folder
- s

# package

- `style.css` contains the 

# dependencies

- `pygments` for syntax highlighting
- `latex2mathml` for latex support

# approach

- everything is a static site, nothing is rendered client-side, and it is pure html/css i.e. it doesn't require any js


# structure

pycounts
├── LICENSE                    ┐ Package documentation
├── README.md                  ┘
├── pyproject.toml             ┐ 
├── src                        │
│   └── alloypress             │ Package source code, metadata,
│       ├── __init__.py        │ and build instructions 
│       ├── ssg.py             │
│       └── style.css          ┘
└── tests                      ┐
    └── ...                    ┘ Package tests