import os
import django

# 运行此脚本的命令：
# python -m api.utils.test_cloudflare
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itstudio_web_publish.settings')
    django.setup()
    from .cloudflare import CloudflareClient

    # 测试Cloudflare
    try:
        client = CloudflareClient()
        # 创建CNAME记录
        response = client.create_record(
            name='test-it',
            content='283c1e80-c7dc-4a2b-8842-6521b5414546.cfargotunnel.com',
            type='CNAME'
        )
        print(f'Successfully created Cloudflare DNS record: {response}')

        # 更新CNAME记录
        response = client.update_record(
            record_id=response.id,
            name='test-it',
            content='new-content.cfargotunnel.com',
            type='CNAME'
        )
        print(f'Successfully updated Cloudflare DNS record: {response}')
    except Exception as e:
        print(f'Failed to create or update Cloudflare DNS record: {str(e)}')