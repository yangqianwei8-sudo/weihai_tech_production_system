# -*- coding: utf-8 -*-
"""
初始化高德地图API信息到后台API管理
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from backend.apps.api_management.models import ExternalSystem, ApiInterface

User = get_user_model()


class Command(BaseCommand):
    help = '初始化高德地图API信息到后台API管理'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='如果系统已存在，则更新信息',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='指定创建人用户ID（默认为第一个超级用户）',
        )

    def handle(self, *args, **options):
        update = options.get('update', False)
        user_id = options.get('user_id')
        
        # 获取创建人
        if user_id:
            try:
                creator = User.objects.get(id=user_id, is_staff=True)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'用户ID {user_id} 不存在或不是员工'))
                return
        else:
            # 获取第一个超级用户
            creator = User.objects.filter(is_superuser=True, is_staff=True).first()
            if not creator:
                # 如果没有超级用户，获取第一个员工用户
                creator = User.objects.filter(is_staff=True).first()
            if not creator:
                self.stdout.write(self.style.ERROR('未找到可用的用户，请先创建管理员用户'))
                return
        
        self.stdout.write(f'使用用户: {creator.username} (ID: {creator.id})')
        
        # 从环境变量获取API配置
        api_key = getattr(settings, 'AMAP_API_KEY', '')
        base_url = getattr(settings, 'AMAP_API_BASE_URL', 'https://restapi.amap.com/v3')
        timeout = getattr(settings, 'AMAP_API_TIMEOUT', 10)
        
        # 检查是否已存在高德地图系统
        amap_system, created = ExternalSystem.objects.get_or_create(
            code='AMAP',
            defaults={
                'name': '高德地图',
                'description': '高德地图开放平台，提供地理编码、逆地理编码、行政区域查询、IP定位、地址解析、输入提示等服务',
                'base_url': base_url,
                'status': 'active',
                'is_active': True,
                'created_by': creator,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ 已创建外部系统: {amap_system.name}'))
        elif update:
            # 更新系统信息
            amap_system.name = '高德地图'
            amap_system.description = '高德地图开放平台，提供地理编码、逆地理编码、行政区域查询、IP定位、地址解析、输入提示等服务'
            amap_system.base_url = base_url
            amap_system.status = 'active'
            amap_system.is_active = True
            amap_system.save()
            self.stdout.write(self.style.SUCCESS(f'✓ 已更新外部系统: {amap_system.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ 外部系统已存在: {amap_system.name} (使用 --update 参数可更新)'))
        
        # 创建或更新API接口
        api_interfaces = [
            {
                'code': 'AMAP-00001',
                'name': '地理编码 API',
                'url': '/geocode/geo',
                'method': 'GET',
                'auth_type': 'api_key',
                'auth_config': {
                    'api_key': api_key if api_key else '请在后台配置AMAP_API_KEY',
                    'key_param': 'key',
                    'description': '高德地图API使用Key作为查询参数进行认证'
                },
                'request_headers': {
                    'Content-Type': 'application/json'
                },
                'request_params': {
                    'key': '高德地图API Key（必填）',
                    'address': '地址字符串，如"北京市朝阳区阜通东大街6号"（必填）',
                    'city': '城市名称或城市编码，限制搜索范围，提高准确性（可选）',
                    'output': '返回格式，默认json'
                },
                'response_schema': {
                    'status': '状态码（1表示成功）',
                    'info': '状态信息',
                    'count': '结果数量',
                    'geocodes': [
                        {
                            'formatted_address': '格式化地址',
                            'province': '省份',
                            'city': '城市',
                            'district': '区县',
                            'township': '街道',
                            'neighborhood': '社区',
                            'building': '建筑',
                            'adcode': '区域编码',
                            'location': '经纬度坐标（经度,纬度）',
                            'level': '地址级别'
                        }
                    ]
                },
                'description': '地理编码API，将地址字符串转换为经纬度坐标。支持通过地址查询获取精确的地理位置坐标。',
                'timeout': timeout,
                'retry_count': 1,
                'version': '3.0',
            },
            {
                'code': 'AMAP-00002',
                'name': '逆地理编码 API',
                'url': '/geocode/regeo',
                'method': 'GET',
                'auth_type': 'api_key',
                'auth_config': {
                    'api_key': api_key if api_key else '请在后台配置AMAP_API_KEY',
                    'key_param': 'key',
                    'description': '高德地图API使用Key作为查询参数进行认证'
                },
                'request_headers': {
                    'Content-Type': 'application/json'
                },
                'request_params': {
                    'key': '高德地图API Key（必填）',
                    'location': '经纬度坐标，格式：经度,纬度（必填）',
                    'extensions': '返回结果控制，base：返回基本信息；all：返回全部信息（可选，默认base）',
                    'output': '返回格式，默认json'
                },
                'response_schema': {
                    'status': '状态码（1表示成功）',
                    'info': '状态信息',
                    'regeocode': {
                        'formatted_address': '格式化地址',
                        'addressComponent': {
                            'province': '省份',
                            'city': '城市',
                            'district': '区县',
                            'township': '街道',
                            'street': '街道名称',
                            'streetNumber': '街道门牌号'
                        },
                        'adcode': '区域编码',
                        'neighborhood': {
                            'name': '社区名称'
                        },
                        'building': {
                            'name': '建筑名称'
                        }
                    }
                },
                'description': '逆地理编码API，将经纬度坐标转换为地址信息。支持通过坐标查询获取详细的地址信息，包括省市区、街道、社区等。',
                'timeout': timeout,
                'retry_count': 1,
                'version': '3.0',
            },
            {
                'code': 'AMAP-00003',
                'name': '行政区域查询 API',
                'url': '/config/district',
                'method': 'GET',
                'auth_type': 'api_key',
                'auth_config': {
                    'api_key': api_key if api_key else '请在后台配置AMAP_API_KEY',
                    'key_param': 'key',
                    'description': '高德地图API使用Key作为查询参数进行认证'
                },
                'request_headers': {
                    'Content-Type': 'application/json'
                },
                'request_params': {
                    'key': '高德地图API Key（必填）',
                    'keywords': '查询关键字，支持：行政区名称、citycode、adcode（可选）',
                    'subdistrict': '子级行政区，0：不返回下级行政区；1：返回下一级行政区；2：返回下两级行政区；3：返回下三级行政区（可选，默认0）',
                    'level': '查询行政级别，可选值：country、province、city、district、street（可选）',
                    'extensions': '返回结果控制，base：返回基本信息；all：返回全部信息（可选，默认base）',
                    'output': '返回格式，默认json'
                },
                'response_schema': {
                    'status': '状态码（1表示成功）',
                    'info': '状态信息',
                    'count': '结果数量',
                    'districts': [
                        {
                            'name': '行政区名称',
                            'adcode': '区域编码',
                            'citycode': '城市编码',
                            'level': '行政级别',
                            'center': '中心点坐标（经度,纬度）',
                            'districts': '下级行政区列表'
                        }
                    ]
                },
                'description': '行政区域查询API，查询省、市、区县信息。支持按关键字、级别查询，可返回多级行政区划数据。',
                'timeout': timeout,
                'retry_count': 1,
                'version': '3.0',
            },
            {
                'code': 'AMAP-00004',
                'name': 'IP定位 API',
                'url': '/ip',
                'method': 'GET',
                'auth_type': 'api_key',
                'auth_config': {
                    'api_key': api_key if api_key else '请在后台配置AMAP_API_KEY',
                    'key_param': 'key',
                    'description': '高德地图API使用Key作为查询参数进行认证'
                },
                'request_headers': {
                    'Content-Type': 'application/json'
                },
                'request_params': {
                    'key': '高德地图API Key（必填）',
                    'ip': 'IP地址，不传则使用请求IP（可选）',
                    'output': '返回格式，默认json'
                },
                'response_schema': {
                    'status': '状态码（1表示成功）',
                    'info': '状态信息',
                    'province': '省份',
                    'city': '城市',
                    'adcode': '区域编码',
                    'rectangle': '边界坐标（min_lon,min_lat;max_lon,max_lat）'
                },
                'description': 'IP定位API，根据IP地址获取位置信息。支持通过IP地址查询获取城市级别的定位信息。',
                'timeout': timeout,
                'retry_count': 1,
                'version': '3.0',
            },
            {
                'code': 'AMAP-00005',
                'name': '输入提示 API',
                'url': '/assistant/inputtips',
                'method': 'GET',
                'auth_type': 'api_key',
                'auth_config': {
                    'api_key': api_key if api_key else '请在后台配置AMAP_API_KEY',
                    'key_param': 'key',
                    'description': '高德地图API使用Key作为查询参数进行认证'
                },
                'request_headers': {
                    'Content-Type': 'application/json'
                },
                'request_params': {
                    'key': '高德地图API Key（必填）',
                    'keywords': '查询关键词（必填）',
                    'city': '城市名称或城市编码，限制搜索范围（可选）',
                    'location': '经纬度坐标，格式：经度,纬度，用于排序（可选）',
                    'datatype': '返回数据类型，all：返回所有类型；poi：仅返回POI；bus：仅返回公交站；busline：仅返回公交线路（可选，默认all）',
                    'output': '返回格式，默认json'
                },
                'response_schema': {
                    'status': '状态码（1表示成功）',
                    'info': '状态信息',
                    'count': '结果数量',
                    'tips': [
                        {
                            'name': '名称',
                            'district': '区县',
                            'adcode': '区域编码',
                            'location': '经纬度坐标（经度,纬度）',
                            'type': '类型'
                        }
                    ]
                },
                'description': '输入提示API，根据关键词获取搜索建议。支持地址、POI、公交站、公交线路等类型的搜索建议。',
                'timeout': timeout,
                'retry_count': 1,
                'version': '3.0',
            },
            {
                'code': 'AMAP-00006',
                'name': '距离测量 API',
                'url': '/distance',
                'method': 'GET',
                'auth_type': 'api_key',
                'auth_config': {
                    'api_key': api_key if api_key else '请在后台配置AMAP_API_KEY',
                    'key_param': 'key',
                    'description': '高德地图API使用Key作为查询参数进行认证'
                },
                'request_headers': {
                    'Content-Type': 'application/json'
                },
                'request_params': {
                    'key': '高德地图API Key（必填）',
                    'origins': '起点坐标，格式：经度,纬度，多个点用|分隔（必填）',
                    'destination': '终点坐标，格式：经度,纬度，多个点用|分隔（必填）',
                    'type': '计算类型，1：直线距离；0：驾车距离（需要路径规划服务）（可选，默认1）',
                    'output': '返回格式，默认json'
                },
                'response_schema': {
                    'status': '状态码（1表示成功）',
                    'info': '状态信息',
                    'count': '结果数量',
                    'results': [
                        {
                            'origin_id': '起点ID',
                            'dest_id': '终点ID',
                            'distance': '距离（米）',
                            'duration': '时间（秒，仅驾车距离有）'
                        }
                    ]
                },
                'description': '距离测量API，计算两点或多点之间的距离。支持直线距离和驾车距离计算。',
                'timeout': timeout,
                'retry_count': 1,
                'version': '3.0',
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for api_data in api_interfaces:
            api_interface, created = ApiInterface.objects.get_or_create(
                code=api_data['code'],
                defaults={
                    'name': api_data['name'],
                    'external_system': amap_system,
                    'url': api_data['url'],
                    'method': api_data['method'],
                    'auth_type': api_data['auth_type'],
                    'auth_config': api_data['auth_config'],
                    'request_headers': api_data['request_headers'],
                    'request_params': api_data['request_params'],
                    'response_schema': api_data['response_schema'],
                    'description': api_data['description'],
                    'timeout': api_data['timeout'],
                    'retry_count': api_data['retry_count'],
                    'version': api_data['version'],
                    'status': 'active',
                    'is_active': True,
                    'created_by': creator,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ 已创建API接口: {api_interface.name}'))
            elif update:
                # 更新API接口信息
                api_interface.name = api_data['name']
                api_interface.url = api_data['url']
                api_interface.method = api_data['method']
                api_interface.auth_type = api_data['auth_type']
                api_interface.auth_config = api_data['auth_config']
                api_interface.request_headers = api_data['request_headers']
                api_interface.request_params = api_data['request_params']
                api_interface.response_schema = api_data['response_schema']
                api_interface.description = api_data['description']
                api_interface.timeout = api_data['timeout']
                api_interface.retry_count = api_data['retry_count']
                api_interface.version = api_data['version']
                api_interface.status = 'active'
                api_interface.is_active = True
                api_interface.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ 已更新API接口: {api_interface.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠ API接口已存在: {api_interface.name}'))
        
        # 总结
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('初始化完成！'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(f'外部系统: {amap_system.name} (编码: {amap_system.code})')
        self.stdout.write(f'API接口: 创建 {created_count} 个, 更新 {updated_count} 个')
        self.stdout.write('')
        self.stdout.write('下一步操作:')
        self.stdout.write('1. 访问后台管理: /admin/api_management/externalsystem/')
        self.stdout.write('2. 编辑高德地图系统，确认基础URL配置')
        self.stdout.write('3. 编辑各个API接口，确认认证配置中的api_key')
        if not api_key:
            self.stdout.write(self.style.WARNING('⚠ 注意: 环境变量中未配置AMAP_API_KEY，请在后台手动配置'))
        self.stdout.write('')
        self.stdout.write('已添加的API接口:')
        for api_data in api_interfaces:
            self.stdout.write(f'  - {api_data["name"]} ({api_data["code"]})')

