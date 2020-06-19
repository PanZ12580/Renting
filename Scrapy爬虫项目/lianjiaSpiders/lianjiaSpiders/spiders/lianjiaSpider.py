# -*- coding: utf-8 -*-
import scrapy, re, time

class LianjiaspiderSpider(scrapy.Spider):
    name = 'lianjiaSpider'
    allowed_domains = ['lianjia.com']
    start_urls = [
        "https://sh.lianjia.com/zufang/jingan/",
        "https://bj.lianjia.com/zufang/dongcheng/",
        "https://sz.lianjia.com/zufang/luohuqu/",
        "https://gz.lianjia.com/zufang/tianhe/"
    ]

    def parse(self, resp):
        base_url = resp.url.split("/zufang")[0]
        try:
            # 城市名
            areaName = resp.meta['areaName']
            # 市
            region = resp.meta['region']
        except:
            url = resp.url
            if url.endswith("/jingan/"):
                areaName = '静安'
                region = '上海'
            elif url.endswith("/dongcheng/"):
                areaName = '东城'
                region = '北京'
            elif url.endswith("/luohuqu/"):
                areaName = '罗湖区'
                region = '深圳'
            elif url.endswith("/tianhe/"):
                areaName = '天河'
                region = '广州'
            else:
                areaName = None
                region = None
        areas = resp.xpath("//ul[@data-target='area']")
        citys = areas[1].xpath("./li[@data-type='bizcircle']/a")
        for city in citys[1:]:
            cityName = city.xpath("./text()").extract_first()
            href = base_url + city.xpath("./@href").extract_first()
            yield scrapy.Request(
                href,
                meta={"region":region, "base_url": base_url, "areaName": areaName, "cityName": cityName, 'flag': True},
                callback=self.parse_list
            )
        # 第一次进入
        if areaName in ['静安', '东城', '罗湖区', '天河']:
            areass = areas[0].xpath("./li/a")
            for area in areass[1:]:
                name = area.xpath("./text()").extract_first()
                if name != areaName:
                    href = base_url + area.xpath("./@href").extract_first()
                    yield scrapy.Request(
                        href,
                        meta={"region":region, "areaName": name},
                        callback=self.parse
                    )


    def parse_list(self, resp):
        divs = resp.xpath("//div[@class='content__list']/div")
        for div in divs:
            try:
                item = {}
                # 市
                item['region'] = resp.meta['region']
                # 地区
                item['areaName'] = resp.meta['areaName']
                # 标题
                title = div.xpath("./div/p[1]/a/text()").extract_first().strip()
                # 类型
                try:
                    item['type'] = title.split("·")[0]
                except:
                    item['type'] = ''
                info = re.sub('\s', '',''.join(div.xpath("./div/p[2]//text()").extract()))
                infos = info.split("/")
                # 地址
                item['address'] = '-'.join(infos[0].split('-')[1:])
                # 面积
                item['area'] = infos[1].replace('㎡', '')
                # 户型
                item['door_model'] = infos[3]
                # 标签
                item['tags'] = ';'.join(div.xpath("./div/p[3]/i/text()").extract())
                # 价格
                item['price'] = div.xpath("./div/span/em/text()").extract_first()
                # 图片地址
                item['img_url'] = div.xpath("./a/img/@data-src").extract_first()
                # 详情页地址
                item['detail_url'] = resp.meta['base_url'] + div.xpath("./a/@href").extract_first()
                resp.meta['item'] = item
                yield scrapy.Request(
                    item['detail_url'],
                    meta=resp.meta,
                    callback=self.parse_detail
                )
            except:
                pass
        if resp.meta['flag']:
            resp.meta['flag'] = False
            # 翻页
            next_hrefs = resp.xpath("//ul[@style='display:hidden']/li/a/@href").extract()
            for next_url in next_hrefs:
                next_url = resp.meta['base_url'] + next_url
                yield scrapy.Request(
                    next_url,
                    callback=self.parse_list,
                    meta=resp.meta
                )


    def parse_detail(self, resp):
        item = resp.meta['item']
        content = resp.body.decode()
        longitudes = re.findall("longitude: '(.*?)',", content)
        if longitudes != []:
            latitudes = re.findall("latitude: '(.*?)'", content)
            item['longitude'] = longitudes[0]
            item['latitude'] = latitudes[0]
            time.sleep(1)
            return item
