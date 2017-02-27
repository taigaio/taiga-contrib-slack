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

from django.conf import settings

from taiga.projects.history import services as history_service
from taiga.projects.history.choices import HistoryType

from . import tasks


def _get_project_slackhooks(project):
    slackhooks = []
    for slackhook in project.slackhooks.all():
        slackhooks.append({
            "id": slackhook.pk,
            "url": slackhook.url,
            "channel": slackhook.channel,
            "notify_config": {
                "notify_epic_create": slackhook.notify_epic_create,
                "notify_epic_change": slackhook.notify_epic_change,
                "notify_epic_delete": slackhook.notify_epic_delete,
                "notify_relateduserstory_create": slackhook.notify_relateduserstory_create,
                "notify_relateduserstory_delete": slackhook.notify_relateduserstory_delete,
                "notify_issue_create": slackhook.notify_issue_create,
                "notify_issue_change": slackhook.notify_issue_change,
                "notify_issue_delete": slackhook.notify_issue_delete,
                "notify_userstory_create": slackhook.notify_userstory_create,
                "notify_userstory_change": slackhook.notify_userstory_change,
                "notify_userstory_delete": slackhook.notify_userstory_delete,
                "notify_task_create": slackhook.notify_task_create,
                "notify_task_change": slackhook.notify_task_change,
                "notify_task_delete": slackhook.notify_task_delete,
                "notify_wikipage_create": slackhook.notify_wikipage_create,
                "notify_wikipage_change": slackhook.notify_wikipage_change,
                "notify_wikipage_delete": slackhook.notify_wikipage_delete
            }

        })
    return slackhooks


def on_new_history_entry(sender, instance, created, **kwargs):
    if not created:
        return None

    if instance.is_hidden:
        return None

    model = history_service.get_model_from_key(instance.key)
    pk = history_service.get_pk_from_key(instance.key)
    obj = model.objects.get(pk=pk)

    slackhooks = _get_project_slackhooks(obj.project)

    if instance.type == HistoryType.create:
        task = tasks.create_slackhook
        extra_args = []
    elif instance.type == HistoryType.change:
        task = tasks.change_slackhook
        extra_args = [instance]
    elif instance.type == HistoryType.delete:
        task = tasks.delete_slackhook
        extra_args = [instance]

    for slackhook in slackhooks:
        args = [
            slackhook["url"], slackhook["channel"],
            slackhook["notify_config"], obj
        ] + extra_args

        if settings.CELERY_ENABLED:
            task.delay(*args)
        else:
            task(*args)
