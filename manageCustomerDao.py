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

def mapCustomerToCohort(cohortname,first_name,last_name,customer_email,serial_no,organization_name):
    data_record = {"cohortName":cohortname,"firstName":first_name,"lastName":last_name,"customerEmail":customer_email,"serialNo":serial_no,"organizationName":organization_name}
    db = client['reach']
    collection = db['cohort-customer']
    find_query = {"cohortName":cohortname,"customerEmail":customer_email}
    result_cursor = collection.find_one(find_query)
    if not result_cursor:
        collection.insert_one(data_record)
        return_message = "Uploaded customer at serial no:" + str(serial_no)
        return return_message
    else:
        return_message = "Did not upload customer at serial no:" + str(serial_no) + ", as it is alrady uploaded"
        return return_message
