from rest_framework import generics, status
from rest_framework.response import Response
from .models import ConfigurationModel, DomainConfig
from .serializers import ConfigurationSerializer, DomainConfigSerializer
from .utils.cloudflare import CloudflareClient
from .utils.dnspod import DNSPodClient
from tencentcloud.dnspod.v20210323 import models
from django.conf import settings
import logging
import yaml
import os

logger = logging.getLogger(__name__)

class ConfigurationView(generics.GenericAPIView):
    serializer_class = ConfigurationSerializer
    
    def get(self, request, *args, **kwargs):
        try:
            config = ConfigurationModel.objects.latest('updated_at')
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        except ConfigurationModel.DoesNotExist:
            return Response({'detail': 'No configuration found.'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, *args, **kwargs):
        # 如果已存在配置，则更新最新的配置
        try:
            config = ConfigurationModel.objects.latest('updated_at')
            serializer = self.get_serializer(config, data=request.data)
        except ConfigurationModel.DoesNotExist:
            # 如果不存在配置，则创建新的配置
            serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DomainConfigListCreateView(generics.ListCreateAPIView):
    queryset = DomainConfig.objects.all()
    serializer_class = DomainConfigSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        try:
            # 更新CloudFlare DNS记录
            cf_client = CloudflareClient()
            domain_parts = instance.domain.split('.')
            if len(domain_parts) >= 2:
                sub_domain = '.'.join(domain_parts[:-2]) if len(domain_parts) > 2 else '@'
                cf_domain = f"{sub_domain}-it"
                config = ConfigurationModel.objects.latest('updated_at')
                cf_content = f"{config.cloudflare_tunnel_id}.cfargotunnel.com"
                cf_client.create_record(name=cf_domain, content=cf_content, type='CNAME')

                # 更新DNSPod DNS记录
                dnspod_client = DNSPodClient()
                main_domain = '.'.join(domain_parts[-2:])
                dnspod_client.create_record(
                    domain=main_domain,
                    sub_domain=sub_domain,
                    record_type='CNAME',
                    value='vhost.itstudio.club'
                )
        except Exception as e:
            logger.error(f"Failed to update DNS records: {str(e)}")
            raise

class DomainConfigPreviewView(generics.GenericAPIView):
    def generate_tunnel_config(self, config, domains):
        """生成Cloudflare Tunnel的配置

        Args:
            config (ConfigurationModel): 配置模型实例
            domains (QuerySet): DomainConfig查询集

        Returns:
            str: YAML格式的配置字符串
        """
        # 构建基础配置
        tunnel_config = {
            'tunnel': config.cloudflare_tunnel_id,
            'credentials-file': f'/etc/cloudflared/{config.cloudflare_tunnel_id}.json',
            'ingress': []
        }
        
        # 为每个域名生成配置
        for domain in domains:
            if domain.host:
                # 如果有host，添加httpHostHeader
                domain_config = {
                    'hostname': domain.domain,
                    'service': domain.proxy_pass,
                    'originRequest': {
                        'httpHostHeader': domain.host
                    }
                }
            else:
                # 如果没有host，使用基本配置
                domain_config = {
                    'hostname': domain.domain,
                    'service': domain.proxy_pass
                }
            tunnel_config['ingress'].append(domain_config)
        
        # 添加默认路由
        tunnel_config['ingress'].append({
            'service': 'http_status:404'
        })
        
        # 转换为YAML格式
        return yaml.dump(tunnel_config, allow_unicode=True, sort_keys=False)

    def get(self, request, *args, **kwargs):
        try:
            # 获取最新的配置
            config = ConfigurationModel.objects.latest('updated_at')
            # 获取所有域名配置
            domains = DomainConfig.objects.all()
            
            # 生成配置
            yaml_config = self.generate_tunnel_config(config, domains)
            
            return Response(yaml_config)
        except ConfigurationModel.DoesNotExist:
            return Response({'error': '未找到配置信息'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class DomainConfigWriteView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            # 获取最新的配置
            config = ConfigurationModel.objects.latest('updated_at')
            # 获取所有域名配置
            domains = DomainConfig.objects.all()
            
            # 生成配置
            preview_view = DomainConfigPreviewView()
            yaml_config = preview_view.generate_tunnel_config(config, domains)
            
            config_yml_path = os.path.join(settings.BASE_DIR, config.config_yml_path)

            # 确保配置文件路径存在
            config_dir = os.path.dirname(config_yml_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            # 写入配置文件
            with open(config_yml_path, 'w', encoding='utf-8') as f:
                f.write(yaml_config)
            
            return Response({'message': '配置文件已成功写入'})
        except ConfigurationModel.DoesNotExist:
            return Response({'error': '未找到配置信息'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        except Exception as e:
            logger.error(f"Failed to generate preview config: {str(e)}")
            return Response(
                {'detail': 'Failed to generate preview config.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DomainConfigRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DomainConfig.objects.all()
    serializer_class = DomainConfigSerializer

    def perform_update(self, serializer):
        # 获取原始实例数据
        original_instance = self.get_object()
        original_domain = original_instance.domain
        new_domain = serializer.validated_data.get('domain')
        cf_records = None
        dnspod_records = None
        
        # 只有当新域名与原域名不同时，才删除原有的DNS记录
        if original_domain != new_domain:
            original_domain_parts = original_domain.split('.')
            if len(original_domain_parts) >= 2:
                try:
                    # 删除CloudFlare DNS记录
                    cf_client = CloudflareClient()
                    original_sub_domain = '.'.join(original_domain_parts[:-2]) if len(original_domain_parts) > 2 else '@'
                    original_cf_domain = f"{original_sub_domain}-it"
                    cf_records = cf_client.client.dns.records.list(zone_id=cf_client.zone_id)
                    for record in cf_records:
                        record_parts = record.name.split('.')
                        record_subdomain = '.'.join(record_parts[:-2]) if len(record_parts) > 2 else record_parts[0]
                        if record_subdomain == original_cf_domain:
                            cf_client.client.dns.records.delete(zone_id=cf_client.zone_id, dns_record_id=record.id)
                            break
                    # 删除DNSPod DNS记录
                    dnspod_client = DNSPodClient()
                    original_main_domain = '.'.join(original_domain_parts[-2:])
                    records = dnspod_client.get_record_list(original_main_domain)
                    for record in dnspod_records.RecordList:
                        if record.Name == original_sub_domain:
                            request = models.DeleteRecordRequest()
                            request.Domain = original_main_domain
                            request.RecordId = record.RecordId
                            dnspod_client.client.DeleteRecord(request)
                            break
                except Exception as e:
                    logger.error(f"Failed to delete old DNS records: {str(e)}")
        
        # 保存新的实例数据
        instance = serializer.save()
        try:
            # 更新CloudFlare DNS记录
            cf_client = CloudflareClient()
            domain_parts = instance.domain.split('.')
            if len(domain_parts) >= 2:
                sub_domain = '.'.join(domain_parts[:-2]) if len(domain_parts) > 2 else '@'
                cf_domain = f"{sub_domain}-it"
                config = ConfigurationModel.objects.latest('updated_at')
                cf_content = f"{config.cloudflare_tunnel_id}.cfargotunnel.com"
                
                # 如果创建失败，尝试更新
                cf_records = cf_client.client.dns.records.list(zone_id=cf_client.zone_id) if cf_records is None else cf_records
                for record in cf_records:
                    # 提取记录的子域名部分
                    record_parts = record.name.split('.')
                    record_subdomain = '.'.join(record_parts[:-2]) if len(record_parts) > 2 else record_parts[0]
                    
                    if record_subdomain == cf_domain:
                        cf_client.update_record(
                            record_id=record.id,
                            name=cf_domain,
                            content=cf_content,
                            type='CNAME'
                        )
                        break
                else:
                    # 如果记录不存在，创建新记录
                    cf_client.create_record(name=cf_domain, content=cf_content, type='CNAME')

            # 更新DNSPod DNS记录
            dnspod_client = DNSPodClient()
            domain_parts = instance.domain.split('.')
            if len(domain_parts) >= 2:
                main_domain = '.'.join(domain_parts[-2:])
                sub_domain = '.'.join(domain_parts[:-2]) if len(domain_parts) > 2 else '@'
                
                # 获取记录列表
                dnspod_records = dnspod_client.get_record_list(main_domain) if dnspod_records is None else dnspod_records
                record_found = False
                
                for record in dnspod_records.RecordList:
                    if record.Name == sub_domain:
                        # 更新已存在的记录
                        dnspod_client.update_record(
                            domain=main_domain,
                            record_id=record.RecordId,
                            sub_domain=sub_domain,
                            record_type='CNAME',
                            value='vhost.itstudio.club'
                        )
                        record_found = True
                        break
                
                if not record_found:
                    # 如果记录不存在，创建新记录
                    dnspod_client.create_record(
                        domain=main_domain,
                        sub_domain=sub_domain,
                        record_type='CNAME',
                        value='vhost.itstudio.club'
                    )
        except Exception as e:
            logger.error(f"Failed to update DNS records: {str(e)}")
            raise

    def perform_destroy(self, instance):
        try:
            # 删除CloudFlare DNS记录
            cf_client = CloudflareClient()
            domain_parts = instance.domain.split('.')
            if len(domain_parts) >= 2:
                sub_domain = '.'.join(domain_parts[:-2]) if len(domain_parts) > 2 else '@'
                cf_domain = f"{sub_domain}-it"
                try:
                    records = cf_client.client.dns.records.list(zone_id=cf_client.zone_id)

                    for record in records:
                        # 提取记录的子域名部分
                        record_parts = record.name.split('.')
                        record_subdomain = '.'.join(record_parts[:-2]) if len(record_parts) > 2 else record_parts[0]
                        if record_subdomain == cf_domain:
                            cf_client.client.dns.records.delete(zone_id=cf_client.zone_id, dns_record_id=record.id)
                            break
                except Exception as e:
                    logger.error(f"Failed to delete CloudFlare DNS record: {str(e)}")

            # 删除DNSPod DNS记录
            dnspod_client = DNSPodClient()
            domain_parts = instance.domain.split('.')
            if len(domain_parts) >= 2:
                main_domain = '.'.join(domain_parts[-2:])
                sub_domain = '.'.join(domain_parts[:-2]) if len(domain_parts) > 2 else '@'
                
                try:
                    records = dnspod_client.get_record_list(main_domain)
                    for record in records.RecordList:
                        if record.Name == sub_domain:
                            request = models.DeleteRecordRequest()
                            request.Domain = main_domain
                            request.RecordId = record.RecordId
                            dnspod_client.client.DeleteRecord(request)
                            break
                except Exception as e:
                    logger.error(f"Failed to delete DNSPod DNS record: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to delete DNS records: {str(e)}")
        
        instance.delete()
