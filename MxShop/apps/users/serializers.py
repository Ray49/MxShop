import re
from datetime import datetime,timedelta

from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import VerifyCode
from MxShop.settings import REGEX_MOBILE
from rest_framework.validators import UniqueValidator
from django.contrib.auth.hashers import make_password

User = get_user_model()


class SmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)


    def validate_mobile(self, mobile):
        """
        手机号码验证
        """
        # 是否已经注册
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("用户已经存在")

        # 是否合法
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码非法")

            # 验证码发送频率
            # 60s内只能发送一次
        one_minutes_ago = datetime.now()-timedelta(hours=0,minutes=1,seconds=0)
        if VerifyCode.objects.filter(add_time__gt=one_minutes_ago,mobile=mobile).count():
            raise serializers.ValidationError("距离上一次发送未超过60s")

        return mobile


class UserRegSerializer(serializers.ModelSerializer):
    code = serializers.CharField(label="验证码",write_only=True,required=True,max_length=4,min_length=4,help_text="验证码",
                                        error_messages={
                                        "blank": "请输入验证码",
                                        "required": "请输入验证码",
                                        "max_length": "验证码格式错误",
                                        "min_length": "验证码格式错误"
                                 },
                                 )
    # 验证用户名是否存在
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])

    # 输入密码的时候不显示明文
    password = serializers.CharField(
        style={'input_type': 'password'}, label="密码", write_only=True,help_text="密码"
    )

    # 密码加密保存
    # def create(self, validated_data):
    #     user = super(UserRegSerializer,self).create(validated_data=validated_data)
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user

    def validate_code(self, code):
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data["username"],code=code).order_by("-add_time")

        if verify_records:
            last_record = verify_records[0]
            # 有效期为五分钟。
            five_minutes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            print(five_minutes_ago)
            print(last_record.add_time)
            if five_minutes_ago > last_record.add_time:
                raise serializers.ValidationError("验证码过期")
        else:
            raise serializers.ValidationError("验证码错误")

    # 不加字段名的验证器作用于所有字段之上。attrs是字段 validate之后返回的总的dict
    def validate(self, attrs):
        # 前端没有传mobile值到后端，这里添加进来
        attrs["mobile"] = attrs["username"]
        # code是自己添加得，数据库中并没有这个字段，验证完就删除u掉
        del attrs["code"]
        return attrs

    class Meta:
        model = User
        fields = ("username","code","mobile","password")


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情
    """
    class Meta:
        model = User
        fields = ("name", "gender", "birthday", "email","mobile")