# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
import jwt

class User(models.Model):
    username = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username

    # 生成token
    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        token = jwt.encode({
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'data': {
                'username': self.username
            }
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')

    class Meta:
        db_table = ' user'

class House(models.Model):
    id = models.BigAutoField(primary_key=True)
    city = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    area = models.IntegerField()
    rent = models.IntegerField()
    house_type = models.CharField(max_length=255)
    lease_method = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    image = models.CharField(max_length=255)
    longitude = models.FloatField()
    latitude = models.FloatField()

    class Meta:
        db_table = 'house'
    
    def __str__(self):
        return self.city + self.region + self.position