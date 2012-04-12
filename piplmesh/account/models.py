import datetime

import mongoengine
from mongoengine.django import auth

from piplmesh.account import fields

LOWER_DATE_LIMIT = 366 * 120

class User(auth.User):
    birthdate = fields.LimitedDateTimeField(upper_limit=datetime.datetime.today(), lower_limit=datetime.datetime.today() - datetime.timedelta(LOWER_DATE_LIMIT))
    gender = fields.GenderField()
    language = fields.LanguageField()
    channel = mongoengine.DictField()
    lastaccess = mongoengine.DateTimeField()
    timeout_counter = mongoengine.StringField()
    connections = mongoengine.IntField(default=1)
    
    facebook_id = mongoengine.IntField()
    facebook_token = mongoengine.StringField(max_length=150)