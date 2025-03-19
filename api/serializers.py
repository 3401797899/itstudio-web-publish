from rest_framework import serializers
from .models import ConfigurationModel, DomainConfig

class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigurationModel
        fields = ['cloudflare_tunnel_id', 'cloudflare_global_api_key', 'cloudflare_email',
                 'cloudflare_zone_id', 'cloudflared_container_id', 'cloudflared_default_behavior',
                 'config_yml_path', 'tencent_secret_key', 'tencent_secret_id', 'created_at',
                 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class DomainConfigSerializer(serializers.ModelSerializer):
    host = serializers.CharField(required=False, allow_blank=True)
    note = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = DomainConfig
        fields = ['id', 'domain', 'proxy_pass', 'host', 'note', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']