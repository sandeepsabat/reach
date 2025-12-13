from pymongo import MongoClient
import datetime
client = MongoClient('mongodb://localhost:27017')


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






