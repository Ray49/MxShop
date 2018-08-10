import random
import uuid

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.mixins import CreateModelMixin
from rest_framework import status
from .serializers import SmsSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_encode_handler,jwt_payload_handler
from .serializers import UserRegSerializer
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


class SmsCodeViewset(CreateModelMixin,viewsets.GenericViewSet):
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


class UserViewset(CreateModelMixin,viewsets.GenericViewSet):
    """
    用户
    """
    serializer_class = UserRegSerializer
    queryset = User.objects.all()

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
