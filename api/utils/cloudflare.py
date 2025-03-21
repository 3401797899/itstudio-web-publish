import logging
from cloudflare import Cloudflare as CloudFlare
from ..models import ConfigurationModel
from .common import split_domain

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
            logger.error("CloudFlare: No configuration found for Cloudflare credentials")
            raise ValueError("CloudFlare: No configuration found for Cloudflare credentials")
        except Exception as e:
            logger.error(f"CloudFlare: Failed to initialize Cloudflare client: {str(e)}")
            raise e

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
            raise e

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
            logger.error(f"CloudFlare: Failed to update DNS record: {str(e)}")
            raise e
    
    def get_record_list(self):
        """获取域名列表"""
        try:
            return self.client.dns.records.get(zone_id=zone_id)
        except Exception as e:
            logger.error(f"CloudFlare: Failed to get DNS record list: {str(e)}")
            raise e

    def delete_record(self, sub_domain):
        """删除DNS记录"""
        try:
            record_id = self.check_domain_has_record(sub_domain)
            if record_id:
                self.client.dns.records.delete(dns_record_id=record_id, zone_id=self.zone_id)
        except Exception as e:
            logger.error(f"CloudFlare: Failed to delete DNS record: {str(e)}")
            raise e
    
    def check_domain_has_record(self, sub_domain):
        """检查域名前缀在Zone中是否已经存在记录"""
        try:
            records = self.client.dns.records.list(zone_id=self.zone_id)
            for record in records:
                record_sub_domain, record_main_domain = split_domain(record.name)
                if record_sub_domain == sub_domain:
                    return record.id
            return None
        except Exception as e:
            logger.error(f"CloudFlare: Failed to check domain has record: {str(e)}")
            raise e
    
    def update_record_by_domain(self, old_sub_domain, sub_domain, content, type='A'):
        """通过域名前缀更新记录"""
        try:
            record_id = self.check_domain_has_record(old_sub_domain) if old_sub_domain else None
            if record_id:
                return self.update_record(record_id, sub_domain, content, type)
            else:
                return self.create_record(sub_domain, content, type)
        except Exception as e:
            logger.error(f"CloudFlare: Failed to update record by domain: {str(e)}")
            raise e