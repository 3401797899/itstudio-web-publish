import logging
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models
from ..models import ConfigurationModel

logger = logging.getLogger(__name__)

class DNSPodClient:
    def __init__(self):
        try:
            config = ConfigurationModel.objects.latest('updated_at')
            self.secret_id = config.tencent_secret_id
            self.secret_key = config.tencent_secret_key
            self.cred = credential.Credential(self.secret_id, self.secret_key)
            self.client = dnspod_client.DnspodClient(self.cred, "ap-guangzhou")
        except ConfigurationModel.DoesNotExist:
            logger.error("No configuration found for Tencent Cloud credentials")
            raise ValueError("No configuration found for Tencent Cloud credentials")
        except Exception as e:
            logger.error(f"Failed to initialize DNSPod client: {str(e)}")
            raise

    def get_record_list(self, domain):
        """获取域名的解析记录列表"""
        try:
            request = models.DescribeRecordListRequest()
            request.Domain = domain
            response = self.client.DescribeRecordList(request)
            return response
        except TencentCloudSDKException as err:
            logger.error(f"Failed to get record list for domain {domain}: {str(err)}")
            raise

    def update_record(self, domain, record_id, sub_domain, record_type, value, ttl=600):
        """更新域名解析记录"""
        try:
            request = models.ModifyRecordRequest()
            request.Domain = domain
            request.RecordId = record_id
            request.SubDomain = sub_domain
            request.RecordType = record_type
            request.RecordLine = "默认"
            request.Value = value
            request.TTL = ttl

            response = self.client.ModifyRecord(request)
            logger.info(f"Successfully updated DNS record for {sub_domain}.{domain}")
            return response
        except TencentCloudSDKException as err:
            logger.error(f"Failed to update record for {sub_domain}.{domain}: {str(err)}")
            raise

    def create_record(self, domain, sub_domain, record_type, value, record_line="默认", ttl=600):
        """创建新的DNS解析记录"""
        try:
            request = models.CreateRecordRequest()
            request.Domain = domain
            request.SubDomain = sub_domain
            request.RecordType = record_type
            request.RecordLine = record_line
            request.Value = value
            request.TTL = ttl

            response = self.client.CreateRecord(request)
            logger.info(f"Successfully created DNS record for {sub_domain}.{domain}")
            return response
        except TencentCloudSDKException as err:
            logger.error(f"Failed to create record for {sub_domain}.{domain}: {str(err)}")
            raise