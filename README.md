Taiga contrib slack
===================

![Kaleidos Project](http://kaleidos.net/static/img/badge.png "Kaleidos Project")
[![Managed with Taiga.io](https://taiga.io/media/support/attachments/article-22/banner-gh.png)](https://taiga.io "Managed with Taiga.io")

The Taiga plugin for slack integration.

![taiga-contrib-slack example](doc/img/taiga-slack-notifications.png)

Installation
------------

#### Taiga Back

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

Download in your `dist/plugins/` directory of Taiga front the `taiga-contrib-slack` compiled code (you need subversion in your system):

```bash
  cd dist/
  mkdir -p plugins
  cd plugins
  svn export "https://github.com/taigaio/taiga-contrib-slack/tags/$(pip show taiga-contrib-slack | awk '/^Version: /{print $2}')/front/dist" "slack"
```

Include in your dist/conf.json in the contribPlugins list the value `"/plugins/slack/slack.json"`:

```json
...
    "contribPlugins": [
        (...)
        "/plugins/slack/slack.json"
    ]
...
```

How to use
----------

Follow the instructions on our support page [Taiga.io Support > Contrib Plugins > Slack integration](https://taiga.io/support/slack-integration/ "Taiga.io Support > Contrib Plugins > Slack integration")
