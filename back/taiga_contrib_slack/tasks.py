# Copyright (C) 2014-2017 Andrey Antukh <niwi@niwi.nz>
# Copyright (C) 2014-2017 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014-2017 David Barragán <bameda@dbarragan.com>
# Copyright (C) 2014-2017 Alejandro Alonso <alejandro.alonso@kaleidos.net>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import requests
import logging

from markdown.inlinepatterns import LINK_RE
import re

from django.conf import settings
from django.template import loader, Context

from taiga.base.api.renderers import UnicodeJSONRenderer
from taiga.base.utils.db import get_typename_for_model_instance
from taiga.celery import app
from taiga.users.models import User
from taiga.users.services import get_user_photo_url


logger = logging.getLogger(__name__)


def _get_type(obj):
    content_type = get_typename_for_model_instance(obj)
    return content_type.split(".")[1]


def _send_request(url, data):
    if settings.CELERY_ENABLED:
        requests.post(url, json=data)
        return

    try:
        requests.post(url, json=data)
    except Exception:
        logger.error("Error sending request to slack")


def _markdown_field_to_attachment(template_field, field_name, values):
    attachment = {
        "color": "warning",
        "mrkdwn_in": ["fields", "title", "fallback"]
    }
    context = Context({"field_name": field_name, "values": values})
    change_field_text = template_field.render(context.flatten())

    attachment['fallback'] = change_field_text.strip()
    attachment['title'] = field_name.replace("_", " ")

    attachment['fields'] = []
    if values[0] and values[1]:
        attachment['fields'].append({
            "title": "from",
            "value": values[0],
            "short": False,
        })
    attachment['fields'].append({
        "title": "to",
        "value": values[1] if values[1] else "empty",
        "short": False,
    })

    return attachment


def _field_to_attachment(template_field, field_name, values):
    attachment = {
        "color": "warning",
        "mrkdwn_in": ["fields", "title", "fallback"]
    }
    context = Context({"field_name": field_name, "values": values})
    change_field_text = template_field.render(context.flatten())

    attachment['fallback'] = change_field_text.strip()

    if field_name == "points":
        attachment['fields'] = []
        for role, points in values.items():
            attachment['fields'].append({
                "title": "{} role points".format(role),
                "value": "*From* {} *to* {}".format(points[0], points[1]),
                "short": True,
            })
    elif field_name == "subject":
        attachment['title'] = "subject"
        attachment['fields'] = [{
            "title": "From",
            "value": values[0],
            "short": False,
        }, {
            "title": "To",
            "value": values[1],
            "short": False,
        }]
    elif field_name == "attachments":
        attachment['fields'] = []
        if values['new']:
            for att in values['new']:
                attachment['fields'].append({
                    "title": "Added new attachment",
                    "value": "<{}|{}> {}".format(att["url"], att["filename"], att.get("description", "")),
                    "short": False,
                })
        if values['changed']:
            for att in values['changed']:
                attachment['fields'].append({
                    "title": "Changed Attachment file",
                    "value": "<{}|{}>".format(att["url"], att["filename"]),
                    "short": True,
                })

                if att.get('changes', {}).get('is_deprecated', None):
                    attachment['fields'].append({
                        "title": "deprecated",
                        "value": "*From* {} *to* {}".format(
                            att["changes"]["is_deprecated"][0],
                            att["changes"]["is_deprecated"][1]
                        ),
                        "short": False,
                    })
                if att.get('changes', {}).get('description', None):
                    attachment['fields'].append({
                        "title": "description",
                        "value": "*From:*\n{}\n*to*:\n{}".format(
                            att["changes"]["description"][0],
                            att["changes"]["description"][1]
                        ),
                        "short": False,
                    })
        if values['deleted']:
            for att in values['deleted']:
                attachment['fields'].append({
                    "title": "Deleted attachment",
                    "value": "{} {}".format(att["filename"], att.get("description", "")),
                    "short": False,
                })

    elif field_name in ["tags", "watchers"]:
        attachment['fields'] = [
            {
                "title": field_name,
                "value": "*From* {} *to* {}".format(", ".join(values[0]) if values[0] is not None else "None",
                                                    ", ".join(values[1]) if values[1] is not None else "None"),
                "short": True,
            },
        ]
    elif field_name == "assigned_to":
        from_value = "Unassigned"
        if values[0] is not None and values[0] != "":
            from_value = values[0]
        to_value = "Unassigned"
        if values[1] is not None and values[1] != "":
            to_value = values[1]
        attachment['fields'] = [
            {
                "title": "assigned to",
                "value": "*From* {} *to* {}".format(from_value, to_value),
                "short": True,
            },
        ]
    elif field_name == "custom_attributes":
        attachment['fields'] = []
        if values['new']:
            for att in values['new']:
                attachment['fields'].append({
                    "title": att["name"],
                    "value": "*to* {}".format(att["value"]),
                    "short": False,
                })
        if values['changed']:
            for att in values['changed']:
                attachment['fields'].append({
                    "title": att["name"],
                    "value": "*from* {} *to* {}".format(att["changes"]["value"][0],
                                                        att["changes"]["value"][1]),
                    "short": False,
                })

        if values['deleted']:
            for att in values['deleted']:
                attachment['fields'].append({
                    "title": att["name"],
                    "value": "deleted",
                    "short": True,
                })
    elif field_name == "is_blocked":
        attachment['fields'] = [
            {
                "title": "is blocked",
                "value": "*to* {}".format(values[1]),
                "short": True,
            },
        ]
    else:
        attachment['fields'] = [
            {
                "title": field_name.replace("_", " "),
                "value": "*From* {} *to* {}".format(values[0], values[1]),
                "short": True,
            },
        ]
    return attachment


def _link_transform(match):
    url_split = match.group(8).split()
    try:
        return "{} ({})".format(match.group(1), url_split[0])
    except IndexError:
        return "{}".format(match.group(1))


def _check_notify_permission(notify_config, obj_type, action):
    return notify_config.get('notify_{0}_{1}'.format(obj_type, action), False)


@app.task
def change_slackhook(url, channel, notify_config, obj, change):
    obj_type = _get_type(obj)

    if not _check_notify_permission(notify_config, obj_type, 'change'):
        return

    template_change = loader.get_template('taiga_contrib_slack/change.jinja')
    comment = re.sub(LINK_RE, _link_transform, change.comment)
    context = Context({"obj": obj, "obj_type": obj_type, "change": change, "comment": comment})

    change_text = template_change.render(context.flatten())
    data = {"text": change_text.strip()}
    data['attachments'] = []

    if channel:
        data["channel"] = channel

    # Get markdown fields
    if change.diff:
        template_field = loader.get_template('taiga_contrib_slack/field-diff.jinja')
        included_fields = ["description", "content", "blocked_note"]

        for field_name, values in change.diff.items():
            if field_name in included_fields:
                attachment = _markdown_field_to_attachment(template_field, field_name, values)

                data['attachments'].append(attachment)

    # Get rest of fields
    if change.values_diff:
        template_field = loader.get_template('taiga_contrib_slack/field-diff.jinja')
        excluded_fields = ["description_diff", "description_html", "content_diff",
                           "content_html", "blocked_note_diff", "blocked_note_html",
                           "backlog_order", "kanban_order", "taskboard_order", "us_order",
                           "finish_date", "is_closed"]

        for field_name, values in change.values_diff.items():
            if field_name in excluded_fields:
                continue

            attachment = _field_to_attachment(template_field, field_name, values)

            if attachment:
                data['attachments'].append(attachment)

    data["username"] = "{} ({})".format(
        getattr(settings, "SLACKHOOKS_USERNAME", "Taiga"),
        change.user['name']
    )
    try:
        user = User.objects.get(pk=change.user['pk'])
        data["icon_url"] = get_user_photo_url(user)
        if data["icon_url"] and not data["icon_url"].startswith("http"):
            data["icon_url"] = "https:{}".format(data["icon_url"])
    except User.DoesNotExist:
        data["icon_url"] = getattr(settings, "SLACKHOOKS_ICON", "https://tree.taiga.io/images/favicon.png")
    _send_request(url, data)


@app.task
def create_slackhook(url, channel, notify_config, obj):
    obj_type = _get_type(obj)

    if not _check_notify_permission(notify_config, obj_type, 'create'):
        return

    template = loader.get_template('taiga_contrib_slack/create.jinja')
    context = Context({"obj": obj, "obj_type": obj_type})
    create_text = template.render(context.flatten())
    data = {
        "text": create_text.strip(),
        "attachments": [{
            "color": "good",
            "fields": [{
                "title": "Creator",
                "value": obj.owner.get_full_name(),
                "short": True,
            }]
        }]
    }

    if obj_type == "wikipage":
        # For wikipages
        content = getattr(obj, 'content', None)
        if content:
            data["attachments"][0]["fields"].append({
                "title": "Content",
                "value": content,
                "short": False,
            })
    else:
        # For stories, tasks, issues and epics
        description = getattr(obj, 'description', None)
        if description:
            data["attachments"][0]["fields"].append({
                "title": "Description",
                "value": description,
                "short": False,
            })

    if channel:
        data["channel"] = channel

    data["username"] = "{} ({})".format(
        getattr(settings, "SLACKHOOKS_USERNAME", "Taiga"),
        obj.owner.get_full_name()
    )
    data["icon_url"] = get_user_photo_url(obj.owner)
    if data["icon_url"] and not data["icon_url"].startswith("http"):
        data["icon_url"] = "https:{}".format(data["icon_url"])

    _send_request(url, data)


@app.task
def delete_slackhook(url, channel, notify_config, obj, change):
    obj_type = _get_type(obj)

    if not _check_notify_permission(notify_config, obj_type, 'delete'):
        return

    template = loader.get_template('taiga_contrib_slack/delete.jinja')
    context = Context({"obj": obj, "obj_type": obj_type})
    delete_text = template.render(context.flatten())
    data = {
        "text": delete_text.strip(),
        "attachments": [{
            "color": "danger",
            "fields": []
        }]
    }

    if obj_type == "wikipage":
        # For wikipages
        content = getattr(obj, 'content', None)
        if content:
            data["attachments"][0]["fields"].append({
                "title": "Content",
                "value": content,
                "short": False,
            })
    else:
        # For stories, tasks, issues and epics
        description = getattr(obj, 'description', None)
        if description:
            data["attachments"][0]["fields"].append({
                "title": "Description",
                "value": description,
                "short": False})

    if channel:
        data["channel"] = channel

    data["username"] = "{} ({})".format(
        getattr(settings, "SLACKHOOKS_USERNAME", "Taiga"),
        change.user['name']
    )
    try:
        user = User.objects.get(pk=change.user['pk'])
        data["icon_url"] = get_user_photo_url(user)
        if data["icon_url"] and not data["icon_url"].startswith("http"):
            data["icon_url"] = "https:{}".format(data["icon_url"])
    except User.DoesNotExist:
        data["icon_url"] = getattr(settings, "SLACKHOOKS_ICON", "https://tree.taiga.io/images/favicon.png")
    _send_request(url, data)


@app.task
def test_slackhook(url, channel):
    data = {
        "text": "Test slack message",
    }

    if channel:
        data["channel"] = channel

    data["username"] = getattr(settings, "SLACKHOOKS_USERNAME", "Taiga")
    data["icon_url"] = getattr(settings, "SLACKHOOKS_ICON", "https://tree.taiga.io/images/favicon.png")
    _send_request(url, data)
