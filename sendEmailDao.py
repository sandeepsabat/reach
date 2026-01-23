from pymongo import MongoClient
import datetime


username="gjgj_gyfg"
password="AmVf2ij8qdd6qm5"
host="localhost"
port="27017"
auth_database="admin"
client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}/{auth_database}')


def addSenderEmailDetails(senderEmail,password,smtpServer,port):
    return_message = ''
    data_record = {'senderEmail':senderEmail,'password':password,'smtpServer':smtpServer,'port':port}
    db = client['reach']
    collection = db['sender-emails']
    filter_query = {"senderEmail":senderEmail}
    sender_email_credential_record = list(collection.find(filter_query))
    if not sender_email_credential_record:
        insertion_result = collection.insert_one(data_record)
        return_message = 'Sender Email Credential added with Id:'+str(insertion_result.inserted_id)
    else:
        document = sender_email_credential_record[-1]
        return_message = 'Sender Email Credentials already exists with Id:' + str(document["_id"])
    return return_message

def getSenderEmailList():
    db = client['reach']
    collection = db['sender-emails']
    projection = {"_id":0,"senderEmail":1}
    result_cursor = collection.find({},projection)
    senderEmailList = [doc['senderEmail'] for doc in result_cursor]
    return senderEmailList
def getSenderEmailCredentialDetails(senderEmail):
    db = client['reach']
    collection = db['sender-emails']
    filter_query = {"senderEmail":senderEmail}
    document = collection.find_one(filter_query)
    senderEmail = document["senderEmail"]
    password = document["password"]
    smtpServer = document["smtpServer"]
    port = document["port"]
    return senderEmail,password,smtpServer,port



def createCampaigns(campaignName, subjectline, htmlFileName):

    data_record = {"name":campaignName,"subjectLine":subjectline,"htmlFile":htmlFileName,"status":'started',"campaignRunDateTime":datetime.datetime.now()}
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

def addEmailToCampaign(campaignName,CampaignId,firstName,lastName,recipientEmail,log_msg,sent_flag,sent_date_time):
    data_record = {}
    if sent_flag == True:
        data_record = {"campaignName":campaignName,"campaignOid":CampaignId,"firstName":firstName,"lastName":lastName,"emailId":recipientEmail,"logMessage":log_msg,"emailSentDateTime":sent_date_time}
    if sent_flag == False:
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
def updateEmailBounceStatus(recipientEmail):
    db = client['reach']
    collection = db['customer']
    filter_query = {"customerEmail":recipientEmail}
    new_values = {"$set":{"isActive":False,"deactivationReason":"Email Bounced"}}
    collection.update_one(filter_query,new_values)