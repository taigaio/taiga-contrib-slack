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
