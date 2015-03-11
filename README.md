Taiga contrib slack
===================

![Kaleidos Project](http://kaleidos.net/static/img/badge.png "Kaleidos Project")
[![Managed with Taiga.io](https://taiga.io/media/support/attachments/article-22/banner-gh.png)](https://taiga.io "Managed with Taiga.io")

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
  INSTALLED_APPS += ["taiga_contrib_slack"]
```

Then run the migrations to generate the new need table:

```bash
  python manage.py migrate taiga_contrib_slack
```

### Taiga Front

Download in your `dist/js/` directory of Taiga front the `taiga-contrib-slack` compiled code:

```bash
  cd dist/js
  wget "https://raw.githubusercontent.com/taigaio/taiga-contrib-slack/stable/front/dist/slack.js"
```

Include in your dist/js/conf.json in the contribPlugins list the value `"/js/slack.js"`:

```json
...
    "contribPlugins": ["/js/slack.js"]
...
```
