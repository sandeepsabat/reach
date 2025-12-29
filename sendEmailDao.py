from pymongo import MongoClient
import datetime


username="gjgj_gyfg"
password="AmVf2ij8qdd6qm5"
host="localhost"
port="27017"
auth_database="admin"
client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}/{auth_database}')

def createCampaigns(campaignName, fileName, htmlFileName):

    data_record = {"name":campaignName,"inputFile":fileName,"htmlFile":htmlFileName,"status":'started',"campaignRunDateTime":datetime.datetime.now()}
    db = client['reach']
    collection = db['campaigns']
    filter_query = {"name":campaignName}
    campaign_records = list(collection.find(filter_query))
    if not campaign_records:
        result = db['campaigns'].insert_one(data_record)
        return result.inserted_id
    else:
        document = campaign_records[-1]
        return document["_id"]

def addEmailToCampaign(campaignName,CampaignId,firstName,lastName,recipientEmail,log_msg):
    data_record = {"campaignName":campaignName,"campaignOid":CampaignId,"firstName":firstName,"lastName":lastName,"emailId":recipientEmail,"logMessage":log_msg}
    db = client['reach']
    db['campaign-emails'].insert_one(data_record)

def getEmailSentForCampaign(campaignName):
    db = client['reach']
    collection = db['campaign-emails']
    relevant_documents = collection.find({"campaignName":campaignName})
    return list(relevant_documents)

def updateCampaignStatus(campaign_id):
    db = client['reach']
    collection = db['campaigns']
    filter_query = {"_id":campaign_id}
    new_values = {"$set":{"status":'completed'}}
    collection.update_one(filter_query,new_values)

def getCampaignStatus(campaignName):
    db = client['reach']
    collection = db['campaigns']
    filter_query = {"name":campaignName}
    projection = {"_id":0,"name":0,"inputFile":0,"htmlFile":0,"status":1,"campaignRunDateTime":0}
    document = collection.find_one(filter_query, projection)
    return document
def updateEmailBounceStatus(campaignName,campaignId,recipientEmail,bounceStatus):
    db = client['reach']
    collection = db['campaign-emails']
    filter_query = {"campaignName":campaignName,"campaignOid":campaignId,"emailId":recipientEmail}
    new_values = {"$set":{"bounceStatus":bounceStatus}}
    collection.update_one(filter_query,new_values)