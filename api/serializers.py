from rest_framework import serializers
from .models import ConfigurationModel

class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigurationModel
        fields = ['cloudflare_tunnel_id', 'cloudflare_token', 'config_yml_path',
                 'tencent_secret_key', 'tencent_secret_id', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']