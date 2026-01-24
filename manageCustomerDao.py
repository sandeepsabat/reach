from pymongo import MongoClient
import datetime


username="gjgj_gyfg"
password="AmVf2ij8qdd6qm5"
host="localhost"
port="27017"
auth_database="admin"
client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}/{auth_database}')


def createCustomerCohort(name,description,shortCode):
    data_record = {"name":name,"description":description,"shortCode":shortCode,"status":'active',"creationDateTime":datetime.datetime.now()}
    db = client['reach']
    collection = db['cohorts']
    filter_query = {"name":name}
    cohort_records = list(collection.find(filter_query))
    if not cohort_records:
        result = db['cohorts'].insert_one(data_record)
        return_message = 'Inserted new cohort with Id:' + str(result.inserted_id)
        return return_message
    else:
        document = cohort_records[-1]
        return_message = 'A chort with this name already exists with Id:' + str(document["_id"])
        return return_message

def getCustomerCohortList():
    db = client['reach']
    collection = db['cohorts']
    projection = {"_id":0,"name":1}
    result_cursor = collection.find({},projection)
    cohortList = [doc["name"] for doc in result_cursor]
    return cohortList

def getNextSerialNoForCohort(cohortname):
    db = client['reach']
    collection = db['cohort-customer']
    find_query = {"cohortName":cohortname}
    result_cursor = list(collection.find(find_query).sort("serialNo",1))
    if not result_cursor:
        return 1
    else:
        last_record = result_cursor[-1]
        next_serial_no = int(last_record["serialNo"]) + 1
        return next_serial_no


def mapCustomerToCohort(cohortname,customer_id,serial_no):
    data_record = {"cohortName":cohortname,"customerOid":customer_id,"serialNo":serial_no}
    db = client['reach']
    collection = db['cohort-customer']
    find_query = {"cohortName":cohortname,"customerOid":customer_id}
    result_cursor = collection.find_one(find_query)
    if not result_cursor:
        collection.insert_one(data_record)
        return_message = "Uploaded customer at serial no:" + str(serial_no)
        return return_message
    else:
        return_message = "Did not upload customer at serial no:" + str(serial_no) + ", as it is already uploaded"
        return return_message
    
def addCustomer(first_name,last_name,customer_email,organization_name):
    data_record = {"firstName":first_name,"lastName":last_name,"customerEmail":customer_email,"organizationName":organization_name,"isActive":True,"deactivationReason":None}
    db = client['reach']
    collection = db['customer']
    find_query = {"customerEmail":customer_email}
    result_cursor = list(collection.find(find_query))
    if not result_cursor:
        result = collection.insert_one(data_record)
        customer_id = result.inserted_id
        return customer_id
    else:
        customer_record = result_cursor[-1]
        customer_id = customer_record["_id"]
        return customer_id

def getCohortEmailList(cohortname):
    
    db = client['reach']
    collection = db['cohort-customer']


    pipeline = [
        {"$match":{
            
            "cohortName":cohortname
        }
      },
       {"$lookup":{
            "from": "customer",
            "localField": "customerOid",
            "foreignField": "_id",
            "as": "customerDetails"
        }
      },
     {"$unwind":{
            "path": "$customerDetails"
        }
     },
     {"$match":{
            
            "customerDetails.isActive":True
        }
     },
    {"$project":{
            "_id": 0,
            "firstName": "$customerDetails.firstName",
            "lastName": "$customerDetails.lastName",
            "email": "$customerDetails.customerEmail",
            "organizationName":"$customerDetails.organizationName",
            "serialNo": "$serialNo"
        }
     }
    ]

    cohortEmailList= collection.aggregate(pipeline)

    return cohortEmailList

def getCampaignName(cohortname,emailShortCode):
    db = client['reach']
    collection = db['cohorts']
    filter_query = {"name":cohortname}
    datestring = datetime.datetime.now().strftime("%d%m%Y")
    cohort_records = list(collection.find(filter_query))
    if not cohort_records:
        campaign_name = 'CMPG-NOGRP-' + emailShortCode + '-'+ datestring
        return campaign_name
    else:
        cohort_record = cohort_records[-1]
        short_code = cohort_record["shortCode"]
        campaign_name = 'CMPG-' + short_code + "-" +emailShortCode+ '-'+ datestring
        return campaign_name

