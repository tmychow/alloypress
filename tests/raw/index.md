---
title: Test File
---

# Purpose

The purpose of this file is to show off the functionality of `alloypress`.

## Markdown Support

`Alloypress` supports the [original markdown syntax](https://daringfireball.net/projects/markdown/syntax):

- **bold** and *italic* text
- [links](https://google.com)
- and so on...

## Latex Support

Beyond that, it also supports inline equations via `latex2mathml`, such as $C(S_t, K, t)$ or even with dollar signs such as $\$10$, as well as block equations:

$$ C(S_t, K, t) = S_t N(d_1) - K e^{-r(T-t)} N(d_2) $$

## Syntax Highlighting

It also supports syntax highlighting for python:

```{python}
def fizzbuzz(n):
    for i in range(1, n+1):
        if i % 15 == 0:
            print("fizzbuzz")
        elif i % 3 == 0:
            print("fizz")
        elif i % 5 == 0:
            print("buzz")
        else:
            print(i)
```

## Sidenotes

It also supports sidenotes<span class="sidenote-count"><input type="checkbox" class="checkbox"><span class="sidenote">such as this</span></span>, which are displayed inline on narrow devices.

