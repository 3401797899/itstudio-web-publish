import os
import django

# run this script by: 
# python -m api.utils.test_dnspod
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itstudio_web_publish.settings')
    django.setup()
    from .dnspod import DNSPodClient
    try:
        client = DNSPodClient()
        # 测试创建DNS记录
        response = client.create_record(
            domain='itstudio.club',
            sub_domain='test',
            record_type='CNAME',
            value='vhost.itstudio.club',
            ttl=600
        )
        print(f'Successfully created DNS record: {response} , type: {type(response)}')

        # 测试更新DNS记录
        response = client.update_record(
            domain='itstudio.club',
            record_id=response.RecordId,
            sub_domain='test',
            record_type='CNAME',
            value='www.itstudio.club',
            ttl=600
        )
        print(f'Successfully updated DNS record: {response}')
    except Exception as e:
        print(f'Failed to create or update DNS record: {str(e)}')