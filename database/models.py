from peewee import *

db = SqliteDatabase('database/database.db')

class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db
        order_by = 'id'


class User(BaseModel):
    tg_id = IntegerField()
    name = CharField()
    username = CharField(null=True)
    query_command = CharField() #Команда для запроса
    datetime_query = DateTimeField() #Время и дата запроса
    currency = CharField()
    city = CharField()
    id_location = IntegerField()
    adults = IntegerField()
    children = IntegerField(null=True)
    checkin = DateField()
    checkout = DateField()
    count_days = IntegerField()
    count_result = IntegerField()
    filter = CharField(null=True)
    min_price = CharField(null=True)
    max_price = CharField(null=True)


    class Meta:
        db_table = 'users'

class Hotel(BaseModel):
    hotel_id = IntegerField()
    user_id = ForeignKeyField(User)
    name = CharField()
    price = IntegerField()
    link = CharField()
    rating = IntegerField()
    address = CharField()

    class Meta:
        db_table = 'hotels'


class Photo(BaseModel):
    hotel_id = ForeignKeyField(Hotel, null=True)
    user_id = ForeignKeyField(User)
    link = CharField(null=True)

    class Meta:
        db_table = 'photos'

