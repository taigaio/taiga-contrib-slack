# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2021-present Kaleidos Ventures SL

from django.apps import AppConfig
from django.urls import include, path


def connect_taiga_contrib_slack_signals():
    from django.db.models import signals
    from taiga.projects.history.models import HistoryEntry
    from . import signal_handlers as handlers
    signals.post_save.connect(handlers.on_new_history_entry, sender=HistoryEntry, dispatch_uid="taiga_contrib_slack")


def disconnect_taiga_contrib_slack_signals():
    from django.db.models import signals
    signals.post_save.disconnect(dispatch_uid="taiga_contrib_slack")


class TaigaContribSlackAppConfig(AppConfig):
    name = "taiga_contrib_slack"
    verbose_name = "Taiga contrib slack App Config"

    def ready(self):
        from taiga.base import routers
        from taiga.urls import urlpatterns
        from .api import SlackHookViewSet

        router = routers.DefaultRouter(trailing_slash=False)
        router.register(r"slack", SlackHookViewSet, base_name="slack")
        urlpatterns.append(path('api/v1/', include(router.urls)))

        connect_taiga_contrib_slack_signals()
