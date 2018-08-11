import random
import uuid

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import mixins
from rest_framework import status
from .serializers import SmsSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_encode_handler,jwt_payload_handler
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .serializers import UserRegSerializer,UserDetailSerializer
import demo_sms_send
from .models import VerifyCode
User = get_user_model()


class CustomBackend(ModelBackend):
    """
    自定义用户验证
    """
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            #用户名和手机都能登录
            user = User.objects.get(
                Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SmsCodeViewset(mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
        手机验证码
    '''
    serializer_class = SmsSerializer

    def generate_code(self):
        """
        生成四位数字的验证码
        """
        str1 = ""
        for i in range(4):
            str1 += str(random.randint(0,9))
        return str1

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # 验证合法
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data["mobile"]
        code = self.generate_code()

        params = {"code":code}
        sms_status = demo_sms_send.send_sms(uuid.uuid1(),mobile,params)
        #字节转字符串
        sms_status = sms_status.decode()
        #字符串转字典
        sms_status = eval(sms_status)
        print(sms_status)

        if sms_status["Code"] != "OK":
            return Response({
                "mobile": sms_status["Message"]
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                "mobile": mobile
            }, status=status.HTTP_201_CREATED)


class UserViewset(mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    """
    用户
    """
    serializer_class = UserRegSerializer
    queryset = User.objects.all()

    # permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication,SessionAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["name"] = user.name if user.name else user.username

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # 虽然继承了Retrieve可以获取用户详情，但是并不知道用户的id，所有要重写get_object方法
    # 重写get_object方法，就知道是哪个用户了
    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()

     # 这里需要动态权限配置
     # 1.用户注册的时候不应该有权限限制
     # 2.当想获取用户详情信息的时候，必须登录才行

    def get_permissions(self):
        if self.action == "retrieve":
            return [IsAuthenticated()]
        elif self.action == "create":
            return []

        return []

    # 这里需要动态选择用哪个序列化方式
    # 1.UserRegSerializer（用户注册），只返回username和mobile   会员中心页面需要显示更多字段，所以要创建一个UserDetailSerializer
    # 2.问题又来了，如果注册的使用userdetailSerializer，又会导致验证失败，所以需要动态的使用serializer
    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return UserRegSerializer

        return UserDetailSerializer


