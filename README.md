Taiga contrib slack
===================

**WARNING:** Not usable yet, currently in development.

The Taiga plugin for slack integration.

Installation
------------

### Taiga Back

In your Taiga back python virtualenv install the pip package `taiga-contrib-slack` with:

```bash
  pip install taiga-contrib-slack
```

Modify your settings/local.py and include the line:

```python
  INSTALLED_APPS += "taiga_contrib_slack"
```

The run the migrations to generate the new need table:

```bash
  python manage.py migrate taiga_contrib_slack
```

### Taiga Front

In your Taiga front directory install the bower package `taiga-contrib-slack` with:

```bash
  bower install taiga-contrib-slack
```

Configure your contrib packages in `????-ToDo-????`.

Recompile the taiga-front contrib code with:

```bash
  gulp contrib
```
