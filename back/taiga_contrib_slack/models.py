from django.db import models
from django.utils.translation import ugettext_lazy as _


class SlackHook(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        null=False,
        blank=False,
        related_name="slackhooks",
        on_delete=models.CASCADE,
    )
    url = models.URLField(null=False, blank=False, verbose_name=_("URL"))
    channel = models.CharField(null=True, blank=True, verbose_name=_("Channel"), max_length=200)

    notify_epic_create = models.BooleanField(default=True)
    notify_epic_change = models.BooleanField(default=True)
    notify_epic_delete = models.BooleanField(default=True)

    notify_relateduserstory_create = models.BooleanField(default=True)
    notify_relateduserstory_delete = models.BooleanField(default=True)

    notify_issue_create = models.BooleanField(default=True)
    notify_issue_change = models.BooleanField(default=True)
    notify_issue_delete = models.BooleanField(default=True)

    notify_userstory_create = models.BooleanField(default=True)
    notify_userstory_change = models.BooleanField(default=True)
    notify_userstory_delete = models.BooleanField(default=True)

    notify_task_create = models.BooleanField(default=True)
    notify_task_change = models.BooleanField(default=True)
    notify_task_delete = models.BooleanField(default=True)

    notify_wikipage_create = models.BooleanField(default=True)
    notify_wikipage_change = models.BooleanField(default=True)
    notify_wikipage_delete = models.BooleanField(default=True)
