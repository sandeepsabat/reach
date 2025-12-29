from pymongo import MongoClient
import datetime


username="gjgj_gyfg"
password="AmVf2ij8qdd6qm5"
host="localhost"
port="27017"
auth_database="admin"
client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}/{auth_database}')


def addTrackableLinkToCampaign(campaignName,link):

    db = client['reach']
    collection = db['campaigns']
    filter_query = {"name":campaignName}
    new_values = {"$set":{"trackableLink":link}}
    collection.update_one(filter_query,new_values)

def addEmailOpenEntryForCampaign(campaignName):
    db = client['reach']
    collection1 = db['campaigns']
    filter_query = {"name":campaignName}
    documentList = list(collection1.find(filter_query))
    document = documentList[-1]
    campaignId = document['_id']
    data_record = {"campaignOid":campaignId,"campaignName":campaignName,"emailOpenDateTime":datetime.datetime.now()}
    collection2 = db['campaign-email-open-tracker']
    collection2.insert_one(data_record)

def getSentEmailsForCampaign(campaignName):
    db = client['reach']
    collection = db['campaign-emails']
    filter_query = {"campaignName":campaignName}
    projection = {"_id":0,"firstName":1,"lastName":1,"emailId":1,"logMessage":1}
    sentEmailList = list(collection.find(filter_query,projection))
    return sentEmailList

def getCampaignNameList():
    db = client['reach']
    collection = db['campaigns']
    campaignNameList = list(collection.distinct("name"))
    return campaignNameList

def getCampaignsEmailStats():
    db = client['reach']
    collection = db['campaigns']

   

    pipeline = [
                {
                    "$lookup":{
                        "from": "campaign-emails",
                        "localField": "_id",
                        "foreignField": "campaignOid",
                        "as": "emailList"
                    }
                },
                {
                    "$unwind":{
                        "path": "$emailList"
                    }
                },
                
                {
                    "$group":{
                        "_id": {
                            "name":"$emailList.campaignName",
                            "runDate":"$campaignRunDateTime"
                        },
                       
                        "emailCount": {
                        "$sum": 1
                        }
                    }
                },
                {
                    "$sort":{
                        "_id.runDate":1
                    }
                },
                {
                    "$project":{
                        "_id": 0,
                        "campaignName": "$_id.name",
                        "emailCount": "$emailCount"
                    }
                }
                ]

    campaignEmailStat =  collection.aggregate(pipeline)
    
    campaignEmailStatList = list(campaignEmailStat)
    return campaignEmailStatList


def getDatewiseEmailStats():
    db = client['reach']
    collection = db['campaigns']

   

    pipeline = [
                {
                    "$lookup":{
                        "from": "campaign-emails",
                        "localField": "_id",
                        "foreignField": "campaignOid",
                        "as": "emailList"
                    }
                },
                {
                    "$unwind":{
                        "path": "$emailList"
                    }
                },
                
                {
                    "$group":{
                        "_id": {
                            "$dateToString":{
                                "format":"%Y-%m-%d",
                                "date":"$campaignRunDateTime"}
                            },
                       
                        "emailCount": {
                        "$sum": 1
                        }
                    }
                },
                {
                    "$project":{
                        "_id": 0,
                        "runDate": "$_id",
                        "emailCount": "$emailCount"
                    }
                },
                {
                    "$sort":{
                        "runDate":1
                    }
                }
                ]

    datewiseEmailStat =  collection.aggregate(pipeline)
    
    datewiseEmailStatList = list(datewiseEmailStat)
    return datewiseEmailStatList

def getBouncesCampaignWise():

    db = client['reach']
    collection = db['campaigns']

   

    pipeline = [
            {
                "$lookup":
                
                {
                    "from": "campaign-emails",
                    "localField": "_id",
                    "foreignField": "campaignOid",
                    "as": "emailList"
                }
            },
            {
                "$unwind":
                
                {
                    "path": "$emailList"
                }
            },
            {
                "$match":
                
                {
                    "emailList.bounceStatus": True
                }
            },
            {
                "$group":
                
                {
                    "_id": {
                        "name": "$name",
                        "runDate": "$campaignRunDateTime"
                        },
                    "bounceCount": {
                        "$sum": 1
                        }
                }
            },
            {
                    "$sort":{
                        "_id.runDate":1
                    }
                },
            {
                    "$project":{
                        "_id": 0,
                        "campaignName": "$_id.name",
                        "bounceCount": "$bounceCount"
                    }
                }
            ]

    emailBounces =  collection.aggregate(pipeline)
    
    emailBounceList = list(emailBounces)
    return emailBounceList

    






