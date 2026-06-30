# Asset pipeline

## Build

```bash
pookiepages build
```

Output:
```
pookiepages: build complete: 3 CSS files, 2 JS files minified -> dist/
```

## Options

```bash
pookiepages build --output my-dist/
pookiepages build --no-minify-css
pookiepages build --no-minify-js
```

## Configure in BuildConfig

```python
from pookiepages.config import BuildConfig

BUILD = BuildConfig(
    outputDir="dist",
    minifyCss=True,
    minifyJs=True,
    minifyHtml=False,
)
```

## Programmatic use

```python
from pookiepages.assets import minifyCss, minifyJs

compressed = minifyCss("body   {   color:   red ;   }")
minifiedJs = minifyJs("function hello()   {   return 'world'; }")
```
