# Copyright (C) 2013 Andrey Antukh <niwi@niwi.be>
# Copyright (C) 2014 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014 David Barragán <bameda@dbarragan.com>
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

from django.conf import settings
from django.template import loader, Context

from taiga.base.api.renderers import UnicodeJSONRenderer
from taiga.base.utils.db import get_typename_for_model_instance
from taiga.celery import app


logger = logging.getLogger(__name__)


def _get_type(obj):
    content_type = get_typename_for_model_instance(obj)
    return content_type.split(".")[1]


def _send_request(url, data):
    data["username"] = getattr(settings, "SLACKHOOKS_USERNAME", "Taiga")
    data["icon_url"] = getattr(settings, "SLACKHOOKS_ICON", "https://tree.taiga.io/images/favicon.png")

    serialized_data = UnicodeJSONRenderer().render(data)

    if settings.CELERY_ENABLED:
        requests.post(url, data=serialized_data)
        return

    try:
        requests.post(url, data=serialized_data)
    except Exception:
        logger.error("Error sending request to slack")


def _markdown_field_to_attachment(template_field, field_name, values):
    attachment = {
        "color": "warning",
        "mrkdwn_in": ["fields", "title", "fallback"]
    }
    context = Context({"field_name": field_name, "values": values})
    change_field_text = template_field.render(context)

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
    change_field_text = template_field.render(context)

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
                    "value": "*from* {} *to* {}".format(att["changes"]["value"][0], att["changes"]["value"][1]),
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


@app.task
def change_slackhook(url, channel, obj, change):
    obj_type = _get_type(obj)

    template_change = loader.get_template('taiga_contrib_slack/change.jinja')
    context = Context({"obj": obj, "obj_type": obj_type, "change": change})

    change_text = template_change.render(context)
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

    _send_request(url, data)


@app.task
def create_slackhook(url, channel, obj):
    obj_type = _get_type(obj)

    template = loader.get_template('taiga_contrib_slack/create.jinja')
    context = Context({"obj": obj, "obj_type": obj_type})
    description = getattr(obj, 'description', '-')

    data = {
        "text": template.render(context),
        "attachments": [{
            "color": "good",
            "fields": [{
                "title": "Creator",
                "value": obj.owner.get_full_name(),
                "short": True,
            }]
        }]
    }
    if description:
        data["attachments"][0]["fields"].append({
            "title": "Description",
            "value": description,
            "short": False,
        })

    if channel:
        data["channel"] = channel

    _send_request(url, data)


@app.task
def delete_slackhook(url, channel, obj):
    obj_type = _get_type(obj)

    template = loader.get_template('taiga_contrib_slack/delete.jinja')
    context = Context({"obj": obj, "obj_type": obj_type})
    description = getattr(obj, 'description', '-')

    data = {
        "text": template.render(context),
        "attachments": [{
            "color": "danger",
            "fields": [{
                "title": "Description",
                "value": description,
                "short": False,
            }]
        }]
    }

    if channel:
        data["channel"] = channel

    _send_request(url, data)


@app.task
def test_slackhook(url, channel):
    data = {
        "text": "Test slack message",

    }

    if channel:
        data["channel"] = channel

    _send_request(url, data)
