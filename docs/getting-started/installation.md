# Installation

pookiepages requires Python 3.12 or newer.

```bash
pip install pookiepages
```

## Scaffold a project

```bash
pookiepages init
```

The wizard asks for a project name and type (dynamic or static). It creates the project directory with the right structure.

## Project structure

```
my-project/
    pages/              # HTML files - each file becomes a route
        index.html      # serves at /
        about.html      # serves at /about
    static/             # CSS, JS, images
    models/             # PookieDB models
    routes/             # Dynamic API routes
    migrations/         # Database migrations
    pookiepages.config.py
    settings.py
    .gitignore
```
