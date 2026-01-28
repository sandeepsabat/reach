from pymongo import MongoClient
import datetime


username="gjgj_gyfg"
password="AmVf2ij8qdd6qm5"
host="localhost"
port="27017"
auth_database="admin"
client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}/{auth_database}')


def getUserList():
    db = client['reach']
    collection = db['users']
    projection = {"_id":1,"name":1,"email":1,"role":1,"created_at":1,"updated_at":1}
    userList = list(collection.find({},projection))
    print (userList)
    return userList