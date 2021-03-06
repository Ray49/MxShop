"""VueDjangoFrameWorkShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, re_path, include
import xadmin
from django.views.static import serve
from .settings import MEDIA_ROOT
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token


from goods.views import GoodsListViewSet, CategoryViewset
from users.views import SmsCodeViewset,UserViewset
from user_operation.views import UserFavViewset,LeavingMessageViewset,AddressViewset
from trade.views import ShoppingCartViewset

router = DefaultRouter()

# 配置goods的url,这个basename是干啥的
router.register(r'goods', GoodsListViewSet, base_name="goods")

# 配置Category的url
router.register(r'categorys', CategoryViewset, base_name="categorys")
router.register(r'code',SmsCodeViewset,base_name="code")

router.register(r'users', UserViewset, base_name="users")
# 配置用户收藏的url
router.register(r'userfavs', UserFavViewset, base_name="userfavs")
# 配置用户留言的url
router.register(r'messages', LeavingMessageViewset, base_name="messages")
# 配置收货地址
router.register(r'address',AddressViewset , base_name="address")
# 配置购物车的url
router.register(r'shopcarts', ShoppingCartViewset, base_name="shopcarts")

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    path('ueditor/', include('DjangoUeditor.urls')),
    # rest 登录的
    path('api-auth/', include('rest_framework.urls')),
    # 处理图片显示的url,使用Django自带serve,传入参数告诉它去哪个路径找，我们有配置好的路径MEDIAROOT
    re_path('media/(?P<path>.*)', serve, {"document_root": MEDIA_ROOT}),

    re_path('^', include(router.urls)),

    path('docs/', include_docs_urls(title='慕学生鲜文档')),
    path('api-token-auth/',views.obtain_auth_token),

    # jwt的token认证接口
    # path('jwt-auth/', obtain_jwt_token),
    # jwt的认证接口
    path('login/', obtain_jwt_token),

]

