Taiga contrib slack
===================

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

Download in your `dist/js/` directory of Taiga front the `taiga-contrib-slack` compiled code:

```bash
  cd dist/js
  wget "https://raw.githubusercontent.com/taigaio/taiga-contrib-slack/stable/front/dist/slack.js"
```

Include the file in the `dist/index.html` file between the `libs.js` and `apps.js` with this line:

```html
  <script src="/js/slack.js"></script>
```
