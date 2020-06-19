# -*- coding: utf-8 -*-
import scrapy


class DankespiderSpider(scrapy.Spider):
    name = 'dankeSpider'
    allowed_domains = ['danke.com']
    start_urls = [
        # 上海
        'https://www.danke.com/room/sh',
        # 北京
        'https://www.danke.com/room/bj',
        # 广州
        'https://www.danke.com/room/gz',
        # 深圳
        'https://www.danke.com/room/sz'
    ]


    def parse(self, resp):
        if resp.url.endswith('sh'):
            region = '上海'
        elif resp.url.endswith('bj'):
            region = '北京'
        elif resp.url.endswith('sz'):
            region = '深圳'
        elif resp.url.endswith('gz'):
            region = '广州'
        else:
            region = None
        divs = resp.xpath("//div[@class='filter_options']/dl[@class='dl_lst list area']/dd/div/div")
        for div in divs:
            # 区域
            cityName = div.xpath("./a/text()").extract_first().strip()
            # 地址
            a_s = div.xpath("./div/a")
            for a in a_s:
                areaName = a.xpath("./text()").extract_first().strip()
                areaHref = a.xpath("./@href").extract_first()
                yield scrapy.Request(
                    areaHref,
                    meta={'areaName': areaName, 'cityName': cityName, 'region': region, 'flag':True},
                    callback=self.parse_list
                )


    def parse_list(self, resp):
        divs = resp.xpath("//div[@class='r_ls_box']/div")
        # 进行循环遍历
        for div in divs:
            # 详情页url
            href = div.xpath("./div[1]/div[1]/a/@href").extract_first()
            yield scrapy.Request(
                href,
                meta=resp.meta,
                callback=self.parse_detail
            )
        if resp.meta['flag']:
            resp.meta['flag'] = False
            next_a = resp.xpath("//div[@class='page']/a")
            for a in next_a[1:]:
                next_url = a.xpath("./@href").extract_first()
                yield scrapy.Request(
                    next_url,
                    meta=resp.meta,
                    callback=self.parse_list
                )

            
    def parse_detail(self, resp):
        try:
            item = {}
            room_detail = resp.xpath("//div[@class='room-detail-right']")[0]
            # 市
            item['region'] = resp.meta['region']
            # 城市
            item['cityName'] = resp.meta['cityName']
            # 标签 例如：独立阳台 不是所有的都有 独立阳台 这种数据
            item['tags'] = room_detail.xpath("./div[2]/span[1]/text()").extract_first()
            if not item['tags']:
                item['tags'] = ''
            # 月租金
            item['room_price_sale'] = room_detail.xpath("./div[3]/div[2]/div[1]//div[@class='room-price-sale']/text()").extract_first().strip()
            div1 = room_detail.xpath("./div[@class='room-list-box']/div[1]")[0]
            # 建筑面积
            item['construction'] = div1.xpath("./div[1]/label/text()").extract_first().replace("约", "").replace("㎡", "")\
                .replace("建筑面积：", "").replace("（以现场勘察为准）", "")
            # 户型
            item['door_model'] = div1.xpath("./div[3]/label/text()").extract_first().replace("户型：", "").strip()
            div2 = room_detail.xpath("./div[@class='room-list-box']/div[2]")[0]
            # 区域
            d = div2.xpath("./div[4]/label/div/a")[-1]
            item['area'] = d.xpath("./text()").extract_first().replace("区域：", "")
            # 图片地址
            item['img_url'] = resp.xpath("//div[@id='myCarousel']/div/div[1]/img/@src").extract_first()
            if item['img_url'].startswith("//"):
                item['img_url'] = 'https:' + item['img_url']
            # 链接地址
            item['detail_url'] = resp.url
            return item
        except:
            pass
