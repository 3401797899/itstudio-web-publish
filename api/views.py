from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import ConfigurationModel, DomainConfig
from .serializers import ConfigurationSerializer, DomainConfigSerializer
from .utils.cloudflare import CloudflareClient
from .utils.dnspod import DNSPodClient
from .utils.common import split_domain
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
        cf_client = CloudflareClient()
        dnspod_client = DNSPodClient()
        msg = None
        try:
            domain = serializer.validated_data['domain']
            sub_domain, main_domain = split_domain(domain)
            config = ConfigurationModel.objects.latest('updated_at')
            # 更新CloudFlare DNS记录
            msg = "更新CloudFlare DNS记录"
            cf_content = f"{config.cloudflare_tunnel_id}.cfargotunnel.com"
            cf_client.update_record_by_domain(old_sub_domain=None, sub_domain=f"{sub_domain}-it", content=cf_content, type='CNAME')
            # 更新DNSPod DNS记录
            msg = "更新DNSPod DNS记录"
            dnspod_client.update_record_by_domain(old_domain=None, domain=domain, record_type='CNAME', value='vhost.itstudio.club')
            # 更新数据库
            instance = serializer.save()
        except Exception as e:
            logger.error(f"Failed to update DNS records: {str(e)}")
            raise ValidationError({'msg': [f'{msg}失败: {e}']})

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
            _domain = domain.domain
            _sub_domain, _main_domain = split_domain(_domain)
            domain_config = {
                'hostname': f"{_sub_domain}{config.cloudflare_domain_suffix}",
                'service': "http://" + domain.proxy_pass
            }
            if domain.host:
                # 如果有host，添加httpHostHeader
                domain_config['originRequest'] = {
                    'httpHostHeader': domain.host
                }
            tunnel_config['ingress'].append(domain_config)
        
        # 添加默认路由
        tunnel_config['ingress'].append({
            'service': config.cloudflared_default_behavior
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

class DomainConfigRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DomainConfig.objects.all()
    serializer_class = DomainConfigSerializer

    def perform_update(self, serializer):
        # 如果只更新Host和备注，不更新DNS记录
        validated_data = serializer.validated_data
        original_instance = self.get_object()
        if validated_data['domain'] == original_instance.domain:
            instance = serializer.save()
            return
        msg = None
        # 更新DNS记录
        try:
            domain = serializer.validated_data['domain']
            sub_domain, main_domain = split_domain(domain)
            old_sub_domain, old_main_domain = split_domain(original_instance.domain)
            cf_client = CloudflareClient()
            dnspod_client = DNSPodClient()
            config = ConfigurationModel.objects.latest('updated_at')
            # 更新CloudFlare DNS记录
            msg = "更新CloudFlare DNS记录"
            cf_content = f"{config.cloudflare_tunnel_id}.cfargotunnel.com"
            cf_client.update_record_by_domain(
                old_sub_domain=f"{old_sub_domain}-it",
                sub_domain=f"{sub_domain}-it",
                content=cf_content,
                type='CNAME'
            )
            # 更新DNSPod DNS记录
            msg = "更新DNSPod DNS记录"
            dnspod_client.update_record_by_domain(
                old_domain=original_instance.domain,
                domain=domain,
                record_type='CNAME',
                value='vhost.itstudio.club'
            )
            serializer.save()
        except Exception as e:
            logger.error(f"Failed to update DNS records: {str(e)}")
            raise ValidationError({'msg': [f'{msg}失败: {e}']})

    def perform_destroy(self, instance):
        msg = None
        try:
            domain = instance.domain
            sub_domain, main_domain = split_domain(domain)
            # 删除CloudFlare DNS记录
            msg = "删除CloudFlare DNS记录"
            cf_client = CloudflareClient()
            cf_client.delete_record(sub_domain=f"{sub_domain}-it")
            # 删除DNSPod DNS记录
            msg = "删除DNSPod DNS记录"
            dnspod_client = DNSPodClient()
            dnspod_client.delete_record(domain=domain)
            instance.delete()
        except Exception as e:
            logger.error(f"Failed to delete DNS records: {str(e)}")
            raise ValidationError({'msg': [f'{msg}失败: {e}']})

class DomainConfigRestartView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            # 获取最新的配置
            config = ConfigurationModel.objects.latest('updated_at')
            container_id = config.cloudflared_container_id
            
            # 执行Docker重启命令
            import subprocess
            result = subprocess.run(['docker', 'restart', container_id], capture_output=True, text=True)
            
            if result.returncode == 0:
                return Response({'message': 'Container restarted successfully'})
            else:
                return Response(
                    f'重启失败: {result.stderr}', 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except ConfigurationModel.DoesNotExist:
            return Response({'error': 'No configuration found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Failed to restart container: {str(e)}")
            return Response(
                {'msg': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
