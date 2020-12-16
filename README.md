# cast.postmarketos.org

## Dev

### Python Requirements Setup

Python 3.4+ is supported. Install all requirements, preferably within a virtualenv:

```shell
$ python -m venv .venv
$ source .venv/bin/activate
(venv)$ pip install -r requirements.txt
```

### Dev Server

Run the dev server during local development, changes are auto reloaded:

```shell
(venv)$ FLASK_DEBUG=1 FLASK_APP=app.py flask run
```

### Build

To run a static site build, run:

```shell
(venv)$ python freeze.py
```

This will generate a static version in `docs/`. Any manual changes to the `docs/` directory will be overridden in the next build.

Note that the `docs/` directory is ignored and not versioned.


### Upgrading requirements.txt

```shell
(venv)$ pip install pip-upgrader
(venv)$ pip-upgrade
```
