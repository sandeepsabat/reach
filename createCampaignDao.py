from pymongo import MongoClient
import datetime


username="gjgj_gyfg"
password="AmVf2ij8qdd6qm5"
host="localhost"
port="27017"
auth_database="admin"
client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}/{auth_database}')

def createEmailTemplate(templateName,description,subjectLine,fileName,shortCode):
    data_record = {"templateName":templateName,"description":description,"subjectLine":subjectLine,"fileName":fileName,"shortCode":shortCode,"status":'active',"creationDateTime":datetime.datetime.now()}
    db = client['reach']
    collection = db['email-templates']
    name_filter_query = {"templateName":templateName}
    email_template_records = list(collection.find(name_filter_query))
    file_filter_query = {"fileName":fileName}
    file_name_records = list(collection.find(file_filter_query))
    if not email_template_records and not file_name_records:
        result = collection.insert_one(data_record)
        return_message = 'Inserted new email template with Id:' + str(result.inserted_id)
        return return_message
    if email_template_records and not file_name_records:
        email_template = email_template_records[-1]
        return_message = 'A template with this name already exists with Id:' + str(email_template["_id"])
        return return_message
    if not email_template_records and file_name_records:
        file_name_record = file_name_records[-1]
        return_message = 'A template with this filename already exists with templateName:' + str(file_name_record["templateName"])
        return return_message
    else:
        #if we reach this branch then only possibility is a record already exist with same name and same file name
        email_template = email_template_records[-1]
        return_message = 'A template with this name and filename already exists with Id:' + str(email_template["_id"])
        return return_message
        
def getEmailTemplateList():
    db = client['reach']
    collection = db['email-templates']
    projection = {"templateName":1}
    emailTemplateDictList = list(collection.find({},projection))
    emailTemplateList = [template['templateName'] for template in emailTemplateDictList]
    return emailTemplateList

def getEmailTemplateDetails(templateName):
    db = client['reach']
    collection = db['email-templates']
    find_query = {"templateName":templateName}
    template_record = collection.find_one(find_query)
    subjectLine = template_record['subjectLine']
    htmlFileName = template_record['fileName']
    emailShortCode = template_record["shortCode"]

    return subjectLine,htmlFileName,emailShortCode
