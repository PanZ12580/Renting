from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.db import connection
from django.core.paginator import Paginator

import json
import math
import operator
from random import randrange
from pyecharts.charts import Bar, WordCloud, Pie, Funnel, Line, BMap
from pyecharts import options as opts
from renting.decorator import auth_permission_required
from .models import *
from .redisDao import RedisClient
# Create your views here.

# --------------------------------------------定义数据返回格式---------------------------------------------------------


def json_success(data, statusCode=200, flag=True):
    data = {
        "statusCode": statusCode,
        "flag": flag,
        "data": data,
    }
    return JsonResponse(data)


def json_error(error="error", statusCode=500, flag=False, **kwargs):
    data = {
        "statusCode": statusCode,
        "flag": flag,
        "error": error,
        "data": {}
    }
    data.update(kwargs)
    return JsonResponse(data)

# --------------------------------------------登录相关---------------------------------------------------------

# 登录校验
@require_http_methods(['POST'])
def login(request):
    response = {}
    error = ""
    try:
        user = User.objects.filter(username=request.POST.get('username'))
        # 用户名不存在
        if user is None or len(user) == 0:
            error = '用户名或密码错误'
        # 用户名存在，校验密码
        else:
            loginPassword = request.POST.get('password')
            realPassword = user[0].password
            if loginPassword == realPassword:
                # 身份信息
                response['username'] = user[0].username
                response['id'] = user[0].id
                # 生成token
                response['token'] = user[0].token
                return json_success(response)
            # 用户名存在但密码错误
            else:
                error = "用户名或密码错误"
                return json_error(error=error, statusCode=200)
    except Exception as e:
        # 服务器错误
        error = str(e)

    return json_error(error=error)

# 根据token获取用户信息
@require_http_methods(['GET'])
def findUserByToken(request):
    response = {}
    try:
        auth = request.META.get('HTTP_AUTHORIZATION').split()
    except AttributeError:
        return json_error(statusCode=401, error="未携带token信息")

    # 用户通过API获取数据验证流程
    if auth[0].lower() == 'token':
        try:
            dict = jwt.decode(
                auth[1], settings.SECRET_KEY, algorithms=['HS256'])
            username = dict.get('data').get('username')
        except jwt.ExpiredSignatureError:
            return json_error(statusCode=401, error="Token过期")
        except jwt.InvalidTokenError:
            return json_error(statusCode=401, error="无效的token")
        except Exception as e:
            return json_error(statusCode=401, error="无法获取用户身份信息")

        try:
            user = User.objects.get(username=username)
            response['userId'] = user.id
            response['username'] = user.username
            return json_success(response)
        except User.DoesNotExist:
            return json_error(statusCode=401, error="用户不存在")

    else:
        return json_error(statusCode=401, error="不支持的认证类型")

# --------------------------------------------数据展示---------------------------------------------------------

# 获取租房基础数据
@require_http_methods(['GET'])
@auth_permission_required()
def findHouseList(request):
    response = {}
    error = ""
    try:
        currentPage = int(request.GET.get("currentPage")
                          ) if "currentPage" in request.GET else 1
        pageSize = int(request.GET.get(
            "pageSize")) if "pageSize" in request.GET else 10
        orderBy = request.GET.get(
            "orderBy") if "orderBy" in request.GET else "rent"
        condition = {}
        if "condition" in request.GET and request.GET.get("condition") != "":
            condition = {'city': request.GET.get("condition")}
        p = Paginator(House.objects.filter(
            **condition).order_by(orderBy), pageSize)

        houseList = p.page(currentPage).object_list
        total = p.count
        response = {
            "houseList": json.loads(serializers.serialize("json", houseList)),
            "total": total
        }
        return json_success(response)
    except Exception as e:
        error = str(e)

    return json_error(error=error)

# 删除租房数据
@require_http_methods(['GET'])
@auth_permission_required()
def removeHouse(request):
    response = {}
    error = ""
    try:
        pk = int(request.GET.get("pk")) if "pk" in request.GET else 0
        res = House.objects.get(id=pk).delete()
        response['row'] = res[0]
        return json_success(response)
    except Exception as e:
        error = str(e)
        response['row'] = 0
        return json_error(error=error, **response)


# 获取代理池
@auth_permission_required()
@require_http_methods(['GET'])
def getProxyList(request):
    response = {}
    error = ""
    try:
        redis = RedisClient()
        reverse = request.GET.get(
            "reverse") == "true" if "reverse" in request.GET else False
        currentPage = int(request.GET.get("currentPage")
                          ) if "currentPage" in request.GET else 1
        pageSize = request.GET.get(
            "pageSize") if "pageSize" in request.GET else 10
        proList = redis.all(reverse)
        p = Paginator(proList, pageSize)

        ls = list(p.page_range)
        if currentPage <= 0:
            currentPage = 1
        elif currentPage > ls[-1]:
            currentPage = ls[-1]

        response['proxyList'] = p.page(currentPage).object_list
        response['total'] = p.count
        return json_success(response)

    except Exception as e:
        error = str(e)
    return json_error(error=error)

# 获取代理池总数
@auth_permission_required()
@require_http_methods(['GET'])
def getProxyCount(request):
    response = {}
    error = ""
    try:
        redis = RedisClient()
        response['total'] = redis.count()
        return json_success(response)
    except Exception as e:
        error = str(e)
    return json_error(error=error)

# 删除指定代理
@require_http_methods(['POST'])
@auth_permission_required()
def removeProxy(request):
    response = {}
    error = ""
    try:
        redis = RedisClient()
        proxy = list(request.POST.values()) if request.POST is not None else []
        response['row'] = redis.remove(proxy)
        return json_success(response)
    except Exception as e:
        error = str(e)
    return json_error(error=error)

# 以列表字典的形式返回查询结果
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

# --------------------------------------------数据可视化---------------------------------------------------------


# 各城市平均租金——柱状图
def avgRent() -> Bar:
    sql = "select city,AVG(rent) as avg_rent from house GROUP BY city order by avg_rent;"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    lists = [[], []]
    for row in rows:
        lists[0].append(row[0])
        lists[1].append(round(row[1], 2))
    c = (
        Bar()
        .add_xaxis(lists[0])
        .add_yaxis("平均月租金", lists[1])
        .set_global_opts(title_opts=opts.TitleOpts(title="各城市平均月租金"))
        .set_series_opts(
        label_opts=opts.LabelOpts(is_show=False),
        markline_opts=opts.MarkLineOpts(
            data=[
                opts.MarkLineItem(type_="min", name="最小值"),
                opts.MarkLineItem(type_="max", name="最大值"),
                opts.MarkLineItem(type_="average", name="平均值"),
                ]
            ),
        )
        .dump_options_with_quotes()
    )
    return c
# 各城市平均租金——柱状图
@require_http_methods(['GET'])
@auth_permission_required()
def getAvgRentBar(request):
    try:
        return json_success(json.loads(avgRent()))
    except Exception as e: 
        return json_error(error = str(e))


# 标签词云图
def tagsCloud(city) -> WordCloud:
    sql = "select tags from house where tags != '' and 1 = 1 "
    with connection.cursor() as cursor:
        if city is not None and city != "":
            sql += " and city = %s"
            cursor.execute(sql, [city])
        else:
            cursor.execute(sql)
            city = "所有"
        rows = cursor.fetchall()
    list1 = []
    for row in rows:
        list2 = row[0].split(';')
        for i in list2:
            list1.append(i)
    a = {}
    for i in set(list1):
        a[i] = list1.count(i)
    attr = a.keys()
    value = a.values()
    data = [z for z in zip(attr, value)]
    c = (
        WordCloud()
        .add(series_name=city, data_pair=data, word_size_range=[6, 66])
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=city, title_textstyle_opts=opts.TextStyleOpts(font_size=23)
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
        .dump_options_with_quotes()
    )
    return c
# 标签词云图
@require_http_methods(['GET'])
@auth_permission_required()
def getTagsCloud(request):
    try:
        city = request.GET.get("city") if "city" in request.GET else ""
        return json_success(json.loads(tagsCloud(city)))
    except Exception as e: 
        return json_error(error = str(e))

# 住房类型分布内外饼图
def typeNestedPie() -> Pie:
    sql1 = "select house_type from house;"
    sql2 = "select lease_method from house where lease_method = '整租' or lease_method = '合租';"
    with connection.cursor() as cursor:
        cursor.execute(sql1)
        rows = cursor.fetchall()
    list1 = []
    for row in rows:
        list1.append(row[0])
    # print(list1)
    a = {}
    for i in set(list1):
        a[i] = list1.count(i)
    attr1 = a.keys()
    value1 = a.values()
    data1 = [list(z) for z in zip(attr1, value1)]

    with connection.cursor() as cursor:
        cursor.execute(sql2)
        rows = cursor.fetchall()
    list2 = []
    for row in rows:
        list2.append(row[0])
    a = {}
    for i in set(list2):
        a[i] = list2.count(i)
    attr2 = a.keys()
    value2 = a.values()
    data2 = [list(z) for z in zip(attr2, value2)]

    c = (
        Pie(init_opts=opts.InitOpts(width="1600px", height="800px"))
        .add(
            series_name="租赁方式",
            data_pair=data2,
            radius=[0, "30%"],
            label_opts=opts.LabelOpts(position="inner"),
            tooltip_opts=opts.TooltipOpts(is_show=False)
        )
        .add(
            series_name="住房类型",
            radius=["40%", "55%"],
            data_pair=data1,
            label_opts=opts.LabelOpts(
               is_show=False
            ),
        )
        .set_global_opts(legend_opts=opts.LegendOpts(is_show=False), title_opts=opts.TitleOpts(title="住房类型及租赁方式分布"))
        .set_series_opts(
            tooltip_opts=opts.TooltipOpts(
                trigger="item", formatter="{a} <br/>{b}: {c} ({d}%)"
            )
        )
        .dump_options_with_quotes()
    )
    return c
# 住房类型分布内外饼图
@require_http_methods(['GET'])
@auth_permission_required()
def getTypeNestedPie(request):
    try:
        return json_success(json.loads(typeNestedPie()))
    except Exception as e: 
        return json_error(error = str(e))

# 租房金额分布漏斗图
def costFunnel(city) -> Funnel:
    sql = "select rent from house where 1 = 1"
    with connection.cursor() as cursor:
        if city is not None and city != "":
            sql += " and city = %s"
            cursor.execute(sql, [city])
        else:
            cursor.execute(sql)
            city = "所有"
        rows = cursor.fetchall()
    list=[]
    for row in rows:
        list.append(row[0])
    a=0;b=0;c=0;d=0;e=0;f=0;g=0
    for i in list:
        if i<1000:
            a+=1
        elif i<2000:
            b+=1
        elif i<3000:
            c+=1
        elif i<4000:
            d+=1
        elif i<5000:
            e+=1
        elif i<8000:
            f+=1
        else:
            g+=1
    x_data=['1000以下','1000-2000','1000-3000','3000-4000','4000-5000','5000-8000','8000以上'] 
    y_data=[a,b,c,d,e,f,g]
    data = [[x_data[i], y_data[i]] for i in range(len(x_data))]
    c = (
        Funnel()
        .add(
            series_name=city,
            data_pair=data,
            gap=2,
            tooltip_opts=opts.TooltipOpts(trigger="item", formatter="{a} <br/>{b} : {c}%"),
            label_opts=opts.LabelOpts(is_show=True, position="inside"),
            itemstyle_opts=opts.ItemStyleOpts(border_color="#fff", border_width=1),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=city, title_textstyle_opts=opts.TextStyleOpts(font_size=23)
            )
        )
        .dump_options_with_quotes()
    )
    return c
# 租房金额分布漏斗图
@require_http_methods(['GET'])
@auth_permission_required()
def getCostFunnel(request):
    try:
        city = request.GET.get("city") if "city" in request.GET else ""
        return json_success(json.loads(costFunnel(city)))
    except Exception as e: 
        return json_error(error = str(e))

# 各区域租房数量分布饼图
def multiPie() -> Pie:
    sql1 = "SELECT region, COUNT(*) AS COUNT FROM house WHERE city = '北京' GROUP BY region;"
    sql2 = "SELECT region, COUNT(*) AS COUNT FROM house WHERE city = '上海' GROUP BY region;"
    sql3 = "SELECT region, COUNT(*) AS COUNT FROM house WHERE city = '广州' GROUP BY region;"
    sql4 = "SELECT region, COUNT(*) AS COUNT FROM house WHERE city = '深圳' GROUP BY region;"
    with connection.cursor() as cursor:
        cursor.execute(sql1)
        rows1 = cursor.fetchall()
        data1 = [list(r) for r in rows1] if len(rows1) != 0 else [['无', 0]]

        cursor.execute(sql2)
        rows2 = cursor.fetchall()
        data2 = [list(r) for r in rows2] if len(rows2) != 0 else [['无', 0]]
        
        cursor.execute(sql3)
        rows3 = cursor.fetchall()
        data3 = [list(r) for r in rows3] if len(rows3) != 0 else [['无', 0]]
        
        cursor.execute(sql4)
        rows4 = cursor.fetchall()
        data4 = [list(r) for r in rows4] if len(rows4) != 0 else [['无', 0]]

    c = (
        Pie()
        .add(
            "北京",
            data1,
            center=["20%", "30%"],
            radius=["10%", "35%"],
            rosetype="area"
        )
        .add(
            "上海",
            data2,
            center=["60%", "30%"],
            radius=["10%", "35%"],
            rosetype="area"
        )
        .add(
            "广州",
            data3,
            center=["20%", "77%"],
            radius=["10%", "35%"],
            rosetype="area"
        )
        .add(
            "深圳",
            data4,
            center=["60%", "77%"],
            radius=["10%", "35%"],
            rosetype="area"
        )
        .set_global_opts(legend_opts=opts.LegendOpts(is_show=False), title_opts=opts.TitleOpts(title="各区域租房数量分布"
            ),
        )
        .dump_options_with_quotes()
    )
    return c
# 各区域租房数量分布饼图
@require_http_methods(['GET'])
@auth_permission_required()
def getMultiPie(request):
    try:
        return json_success(json.loads(multiPie()))
    except Exception as e:
        return json_error(error = str(e))

# 面积性价比折线图
def costEffectiveLine() -> Line:
    sql = "select area,AVG(rent)/area from house where area >= 5 group by area;"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        rows = sorted(rows)
    data = dict(rows)

    x_data = data.keys()
    y_data = data.values()
    # 画图
    c = (
        Line()
        .add_xaxis(xaxis_data=x_data)
        .add_yaxis(
            series_name="面积性价比",
            y_axis=y_data,
            is_smooth=True,
            is_symbol_show=True,
            symbol="circle",
            symbol_size=6,
            linestyle_opts=opts.LineStyleOpts(color="#c82c42"),
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(
                color="red", border_color="#c82c42", border_width=3
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True, background_color = "#196286"),
            areastyle_opts=opts.AreaStyleOpts(
                opacity=0.5, color="#c82c42"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="面积性价比折线图",
                pos_top="3%",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(
                    color="#666666", font_size=16),
            ),
            xaxis_opts=opts.AxisOpts(
                name="面积",
                type_="category",
                boundary_gap=False,
                axislabel_opts=opts.LabelOpts(margin=30, color="#666666"),
                axisline_opts=opts.AxisLineOpts(is_show=True),
                axistick_opts=opts.AxisTickOpts(
                    is_show=True,
                    length=25,
                    linestyle_opts=opts.LineStyleOpts(color="#666666"),
                ),
            ),
            yaxis_opts=opts.AxisOpts(
                name="价格/（月租金/平方米）",
                type_="value",
                position="left",
                axislabel_opts=opts.LabelOpts(margin=20, color="#666666"),
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(width=2, color="#666666")
                ),
                axistick_opts=opts.AxisTickOpts(
                    is_show=True,
                    length=15,
                    linestyle_opts=opts.LineStyleOpts(color="#666666"),
                ),
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
        .dump_options_with_quotes()
    )
    return c

# 面积性价比折线图
@require_http_methods(['GET'])
@auth_permission_required()
def getCostEffectiveLine(request):
    try:
        return json_success(json.loads(costEffectiveLine()))
    except Exception as e:
        return json_error(error = str(e))

# 小区每平米租金最低Top10条形图
def costEffectiveBar(city) -> Line:
    sql = "SELECT POSITION, rent/AREA AS cost FROM house WHERE area >= 5 and 1 = 1 "
    with connection.cursor() as cursor:
        if city is not None and city != "":
            sql += " and city = %s"
            sql += " ORDER BY cost ASC LIMIT 10"
            cursor.execute(sql, [city])
        else:
            sql += " ORDER BY cost ASC LIMIT 10"
            cursor.execute(sql)
            city = "所有城"
        rows = cursor.fetchall()
    list1=[]
    list2=[]
    for row in reversed(rows):
        list1.append(row[0])
        list2.append(row[1])
    c = (
        Bar()
        .add_xaxis(list1)
        .add_yaxis("小区", list2)
        .reversal_axis()
        .set_series_opts(label_opts=opts.LabelOpts(position="right"))
        .set_global_opts(
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-25)),
            xaxis_opts=opts.AxisOpts(
                name="月租金/平方米",
            ),
            title_opts=opts.TitleOpts(title = city + "市小区每平米租金最低Top10"))
        .dump_options_with_quotes()
    )
    return c

# 小区每平米租金最低Top10条形图
@require_http_methods(['GET'])
@auth_permission_required()
def getCostEffectiveBar(request):
    try:
        city = request.GET.get("city") if "city" in request.GET else ""
        return json_success(json.loads(costEffectiveBar(city)))
    except Exception as e:
        return json_error(error = str(e))

# 房价热力图
def heatmap() -> Line:
    sql1 = """
    SELECT 
    CONCAT(city, '市', region, POSITION) AS pos, 
    longitude, 
    latitude, 
    AVG(rent) 
    FROM 
    house 
    WHERE city = '北京' 
    AND longitude != 0 
    AND latitude != 0 
    GROUP BY pos;
    """
    sql2 = """
    SELECT 
    CONCAT(city, '市', region, POSITION) AS pos, 
    longitude, 
    latitude, 
    AVG(rent) 
    FROM 
    house 
    WHERE city = '上海' 
    AND longitude != 0 
    AND latitude != 0 
    GROUP BY pos;
    """
    sql3 = """
    SELECT 
    CONCAT(city, '市', region, POSITION) AS pos, 
    longitude, 
    latitude, 
    AVG(rent) 
    FROM 
    house 
    WHERE city = '广州' 
    AND longitude != 0 
    AND latitude != 0 
    GROUP BY pos;
    """
    sql4 = """
    SELECT 
    CONCAT(city, '市', region, POSITION) AS pos, 
    longitude, 
    latitude, 
    AVG(rent) 
    FROM 
    house 
    WHERE city = '深圳' 
    AND longitude != 0 
    AND latitude != 0 
    GROUP BY pos;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql1)
        rows1 = cursor.fetchall()
        cursor.execute(sql2)
        rows2 = cursor.fetchall()
        cursor.execute(sql3)
        rows3 = cursor.fetchall()
        cursor.execute(sql4)
        rows4 = cursor.fetchall()

    data1 = []
    coord = []
    for row in rows1:
        coord.append([
            row[0],
            row[1],
            row[2]
        ])
        data1.append((
            row[0],
            row[3]
        ))

    data2 = []
    for row in rows2:
        coord.append([
            row[0],
            row[1],
            row[2]
        ])
        data2.append((
            row[0],
            row[3]
        ))
    data3 = []
    for row in rows3:
        coord.append([
            row[0],
            row[1],
            row[2]
        ])
        data3.append((
            row[0],
            row[3]
        ))
    data4 = []
    for row in rows4:
        coord.append([
            row[0],
            row[1],
            row[2]
        ])
        data4.append((
            row[0],
            row[3]
        ))
    # 添加坐标
    b = BMap()
    for item in coord:
        b.add_coordinate(item[0], item[1], item[2])
    sql1 = ""
    c = (
        b
        .add_schema(
            baidu_ak="ecW4FwdyIvse01ZzuQpYeiFsqOlTqmnv",
            center=[120.13066322374, 30.240018034923],
            zoom=5,
            is_roam=True
        )
        .add(
            "北京",
            data1,
            type_="heatmap",
            label_opts=opts.LabelOpts(formatter="{b}"),
        )
        .add(
            "上海",
            data2,
            type_="heatmap",
            label_opts=opts.LabelOpts(formatter="{b}"),
        )
        .add(
            "广州",
            data3,
            type_="heatmap",
            label_opts=opts.LabelOpts(formatter="{b}"),
        )
        .add(
            "深圳",
            data4,
            type_="heatmap",
            label_opts=opts.LabelOpts(formatter="{b}"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="各地小区租房均价热力图"), 
            visualmap_opts=opts.VisualMapOpts(max_ = 10000, min_=900)
        )
        .dump_options_with_quotes()
    )
    return c

# 房价热力图
@require_http_methods(['GET'])
@auth_permission_required()
def getHeatmap(request):
    try:
        return json_success(json.loads(heatmap()))
    except Exception as e:
        return json_error(error = str(e))

