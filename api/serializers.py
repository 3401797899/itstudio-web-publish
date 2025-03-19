from rest_framework import serializers
from .models import ConfigurationModel

class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigurationModel
        fields = ['cloudflare_tunnel_id', 'cloudflare_global_api_key', 'cloudflare_email',
                 'cloudflare_zone_id', 'config_yml_path', 'tencent_secret_key',
                 'tencent_secret_id', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']