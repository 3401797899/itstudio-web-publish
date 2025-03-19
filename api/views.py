from rest_framework import generics, status
from rest_framework.response import Response
from .models import ConfigurationModel, DomainConfig
from .serializers import ConfigurationSerializer, DomainConfigSerializer

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

class DomainConfigRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DomainConfig.objects.all()
    serializer_class = DomainConfigSerializer
