# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2021-present Kaleidos Ventures SL

from taiga.base import filters
from taiga.base import response
from taiga.base.api import ModelCrudViewSet
from taiga.base.decorators import detail_route

from . import models
from . import serializers
from . import permissions
from . import tasks


class SlackHookViewSet(ModelCrudViewSet):
    model = models.SlackHook
    serializer_class = serializers.SlackHookSerializer
    permission_classes = (permissions.SlackHookPermission,)
    filter_backends = (filters.IsProjectAdminFilterBackend,)
    filter_fields = ("project",)

    @detail_route(methods=["POST"])
    def test(self, request, pk=None):
        slackhook = self.get_object()
        self.check_permissions(request, 'test', slackhook)

        tasks.test_slackhook(slackhook.url, slackhook.channel)

        return response.NoContent()
