# -*-coding:utf-8 -*-
import json

from django.http import HttpResponse,JsonResponse
from django.views.generic import View

from goods.models import Goods

class GoodsListView(View):
    def get(self,request):
        json_list = []
        #获取所有商品
        goods = Goods.objects.all()[:10]

        # from django.forms.models import model_to_dict
        # for good in goods:
        # #     json_dict = {}
        # #     json_dict['name'] = good.name
        # #     json_dict['category'] = good.category.name
        # #     json_dict['market_price'] = good.market_price
        # #     json_list.append(json_dict)
        #
        #
        #     json_dict = model_to_dict(good)
        #     json_list.append(json_dict)
        from django.core import serializers
        json_data = serializers.serialize('json',goods)

        json_data = json.loads(json_data)


        # return HttpResponse(json_data,content_type='application/json')

        # return HttpResponse(json.dumps(json_list),content_type='application/json')
        return JsonResponse(json_data,safe=False)