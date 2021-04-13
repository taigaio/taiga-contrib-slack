from taiga.base.api import serializers

from .models import SlackHook


class SlackHookSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlackHook
