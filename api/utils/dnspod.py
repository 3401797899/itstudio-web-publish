import logging
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models
from ..models import ConfigurationModel
from .common import split_domain

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

    def get_record_list(self, main_domain):
        """获取域名的解析记录列表"""
        try:
            request = models.DescribeRecordListRequest()
            request.Domain = main_domain
            response = self.client.DescribeRecordList(request)
            return response
        except TencentCloudSDKException as err:
            logger.error(f"Failed to get record list for domain {main_domain}: {str(err)}")
            raise 

    def update_record(self, main_domain, record_id, sub_domain, record_type, value, ttl=600):
        """更新域名解析记录"""
        try:
            request = models.ModifyRecordRequest()
            request.Domain = main_domain
            request.RecordId = record_id
            request.SubDomain = sub_domain
            request.RecordType = record_type
            request.RecordLine = "默认"
            request.Value = value
            request.TTL = ttl

            response = self.client.ModifyRecord(request)
            logger.info(f"Successfully updated DNS record for {sub_domain}.{main_domain}")
            return response
        except TencentCloudSDKException as err:
            logger.error(f"Failed to update record for {sub_domain}.{main_domain}: {str(err)}")
            raise

    def create_record(self, main_domain, sub_domain, record_type, value, record_line="默认", ttl=600):
        """创建新的DNS解析记录"""
        try:
            request = models.CreateRecordRequest()
            request.Domain = main_domain
            request.SubDomain = sub_domain
            request.RecordType = record_type
            request.RecordLine = record_line
            request.Value = value
            request.TTL = ttl

            response = self.client.CreateRecord(request)
            logger.info(f"Successfully created DNS record for {sub_domain}.{main_domain}")
            return response
        except TencentCloudSDKException as err:
            logger.error(f"Failed to create record for {sub_domain}.{main_domain}: {str(err)}")
            raise
    
    def delete_record(self, domain):
        """删除指定的DNS解析记录"""
        try:
            record_id = self.check_domain_has_record(domain)
            sub_domain, main_domain = split_domain(domain)
            if record_id:
                request = models.DeleteRecordRequest()
                request.Domain = main_domain
                request.RecordId = record_id
                response = self.client.DeleteRecord(request)
                logger.info(f"Successfully deleted DNS record for {record_id}")
        except TencentCloudSDKException as err:
            logger.error(f"Failed to delete record for {record_id}: {str(err)}")
            raise
    
    def check_domain_has_record(self, domain):
        """检查域名是否已经有解析记录"""
        try:
            sub_domain, main_domain = split_domain(domain)
            response = self.get_record_list(main_domain)
            for record in response.RecordList:
                if record.Name == sub_domain:
                    return record.RecordId
            return None
        except TencentCloudSDKException as err:
            logger.error(f"Failed to check domain {domain}: {str(err)}")
            raise
    
    def update_record_by_domain(self, old_domain, domain, record_type, value):
        """通过域名前缀更新记录"""
        try:
            record_id = self.check_domain_has_record(old_domain) if old_domain else None
            sub_domain, main_domain = split_domain(domain)
            if record_id:
                return self.update_record(main_domain, record_id, sub_domain, record_type, value)
            else:
                return self.create_record(main_domain, sub_domain, record_type, value)
        except TencentCloudSDKException as err:
            logger.error(f"Failed to update record for {domain}: {str(err)}")
            raise 
    