# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql, time

class LianjiaspidersPipeline(object):


    def __init__(self):
        # 建立连接
        self.conn = pymysql.connect('localhost', 'root', '123456', 'renting')
        # 创建游标
        self.cursor = self.conn.cursor()


    def process_item(self, item, spider):
        print(item)
        insert_sql = """insert into house(city, region, position, area, rent, house_type, lease_method, tags, url, image
                        ,longitude, latitude) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        self.cursor.execute(insert_sql, (item['region'], item['areaName'], item['address'], item['area'], item['price'],
                                         item['door_model'], item['type'], item['tags'], item['detail_url'], item['img_url'],
                                         item['longitude'], item['latitude']))
        self.conn.commit()
        time.sleep(1)
        return item
