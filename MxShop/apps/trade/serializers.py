
from rest_framework import serializers

from goods.models import Goods
from .models import ShoppingCart
from goods.serializers import GoodsSerializer


class ShopCartDetailSerializer(serializers.ModelSerializer):
    '''
    购物车商品详情信息
    '''
    # 一个购物车对应一个商品
    goods = GoodsSerializer(many=False,read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ("goods", "nums")


class ShopCartSerializer(serializers.Serializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(required=True,min_value=1,label='数量',
                                    error_messages={
                                        "min_value":"商品数量不能小于一",
                                        "required": "请选择购买数量"
                                    }
                                    )
    goods = serializers.PrimaryKeyRelatedField(required=True,queryset=Goods.objects.all())

    #Serializer是没有提供save功能的，所以我们要来重写create方法
    #create方法传入的validated_data是数据已经经过validate之后的数据。
    #而initial_data是未经validate处理过的原始值。需要我们自己进行类型转换等。
    #在view中是可以直接从request中取出用户的，但是在Serializer里面不能直接从request中取。
    def create(self, validated_data):
        # validated_data是已经处理过的数据
        # 获取当前用户
        # view中:self.request.user；serizlizer中:self.context["request"].user
        user = self.context["request"].user
        nums = validated_data['nums']
        goods = validated_data['goods']

        existed = ShoppingCart.objects.filter(user=user, goods=goods)
        # 如果购物车中有记录，数量+1
        # 如果购物车车没有记录，就创建
        if existed:
            existed = existed[0]
            existed.nums += nums
            existed.save()
        else:
            # 添加到购物车
            existed = ShoppingCart.objects.create(**validated_data)

        return existed

    def update(self, instance, validated_data):
        instance.nums = validated_data['nums']
        instance.save()
        return instance
