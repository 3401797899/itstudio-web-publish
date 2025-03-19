from django.db import models
from django.utils.translation import gettext_lazy as _

class ConfigurationModel(models.Model):
    cloudflare_tunnel_id = models.CharField(_('CloudFlare Tunnel ID'), max_length=255)
    cloudflare_global_api_key = models.CharField(_('CloudFlare Global API Key'), max_length=255)
    cloudflare_email = models.CharField(_('CloudFlare Email'), max_length=255)
    cloudflare_zone_id = models.CharField(_('CloudFlare Zone ID'), max_length=255)
    config_yml_path = models.CharField(_('Config.yml Path'), max_length=255)
    tencent_secret_key = models.CharField(_('Tencent Cloud SecretKey'), max_length=255)
    tencent_secret_id = models.CharField(_('Tencent Cloud SecretID'), max_length=255)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Configuration')
        verbose_name_plural = _('Configurations')

    def __str__(self):
        return f'Configuration (Last updated: {self.updated_at})'
