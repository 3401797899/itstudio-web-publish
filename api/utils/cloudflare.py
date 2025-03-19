import logging
from cloudflare import Cloudflare as CloudFlare
from ..models import ConfigurationModel

logger = logging.getLogger(__name__)

class CloudflareClient:
    def __init__(self):
        try:
            config = ConfigurationModel.objects.latest('updated_at')
            self.api_key = config.cloudflare_global_api_key
            self.email = config.cloudflare_email
            self.zone_id = config.cloudflare_zone_id
            self.client = CloudFlare(api_key=self.api_key, api_email=self.email)
        except ConfigurationModel.DoesNotExist:
            logger.error("No configuration found for Cloudflare credentials")
            raise ValueError("No configuration found for Cloudflare credentials")
        except Exception as e:
            logger.error(f"Failed to initialize Cloudflare client: {str(e)}")
            raise

    def create_record(self, name, content, type='A', proxied=True, ttl=1):
        """创建新的DNS记录，默认开启小黄云（代理状态）"""
        try:
            record = {
                'name': name,
                'content': content,
                'type': type,
                'proxied': proxied,
                'ttl': ttl
            }
            return self.client.dns.records.create(zone_id=self.zone_id, name=name, content=content, type=type, proxied=proxied, ttl=ttl)
        except Exception as e:
            logger.error(f"Failed to create DNS record: {str(e)}")
            raise

    def update_record(self, record_id, name, content, type='A', proxied=True, ttl=1):
        """更新DNS记录，默认保持小黄云（代理状态）"""
        try:
            record = {
                'name': name,
                'content': content,
                'type': type,
                'proxied': proxied,
                'ttl': ttl
            }
            return self.client.dns.records.update(dns_record_id=record_id, zone_id=self.zone_id, name=name, content=content, type=type, proxied=proxied, ttl=ttl)
        except Exception as e:
            logger.error(f"Failed to update DNS record: {str(e)}")
            raise