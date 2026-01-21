from flask import Blueprint,request, jsonify,render_template,redirect,url_for,Response,stream_with_context
import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import openpyxl
import datetime
import os
import urllib.parse
from manageCustomerDao import (createCustomerCohort,getCustomerCohortList,mapCustomerToCohort,addCustomer,getNextSerialNoForCohort)


manageCustomer_bp = Blueprint("managecustomer",__name__)

#Get the absolute path of teh directory containing the current script
bas_dir = os.path.dirname(os.path.abspath(__file__))

@manageCustomer_bp.route('/addCohort',methods=['POST'])
def addCohort():
    if request.method == 'POST':
        inputData = request.get_json()
        cohortName = inputData['cohortName']
        description = inputData['description']
        shortCode = inputData['shortCode']

        return_message = createCustomerCohort(cohortName,description,shortCode)
        return jsonify({'message':return_message})
    return jsonify({'message':"accept application/json"})
    
    

@manageCustomer_bp.route('/createCohort',methods=['GET','POST']) # To be removed when front end is fully built
def createCohort():
    if request.method == 'POST':
            inputData = request.get_json()
            cohortName = inputData['cohortName']
            description = inputData['description']
            shortCode = inputData['shortCode']

            return_message = createCustomerCohort(cohortName,description,shortCode)
            return jsonify({'message':return_message})
    
    return render_template('createCohort.html')

@manageCustomer_bp.route('/addCustomerToCohort',methods=['GET','POST'])
def addCustomerToCohort():
    if request.method == 'POST':
            cohortName = request.form.get('cohortname')
            fileName = request.form.get('filenames')
            startRow = int(request.form['startrow'])
            endRow = int(request.form['endrow'])
            return render_template('cohortFill.html',cohortname=cohortName,filename=fileName,startrow=startRow,endrow=endRow)
      
    cohortlist = getCustomerCohortList()
    file_directory = os.path.join(bas_dir,'files','customerlist')
    filenames = os.listdir(file_directory)
    return render_template('customerCohortForm.html',cohortList=cohortlist,fileNames=filenames)

@manageCustomer_bp.route('/custUploadStream')
def custUploadStream():
        
        #Collect all the arguments passed by the client html
        cohortname = request.args.get('cohortName')
        filename = request.args.get('fileName')
        startrow = int(request.args.get('startRow'))
        endrow = int(request.args.get('endRow'))
        
                    
        #Configure Directory Paths
        input_excel_path = os.path.join(bas_dir,'files','customerlist')
        excel_file_name = filename

        #Load the input excel file
        filename = os.path.join(input_excel_path,excel_file_name)
        workbook = openpyxl.load_workbook(filename,data_only=True)
        sheet = workbook['Sheet1']

        

          
        def generate():
           
            try:
                for row in sheet.iter_rows(min_row=startrow,max_row=endrow):
                    serial_no = getNextSerialNoForCohort(cohortname)
                    first_name = row[3].value
                    last_name = row[4].value
                    customer_email = row[5].value
                    organization_name= row[6].value
                    customer_id = addCustomer(first_name,last_name,customer_email,organization_name)
                    
                    log_msg = mapCustomerToCohort(cohortname,customer_id,serial_no)
                    yield f"data: {log_msg}\n\n" #Sends message to the client html as server side events
                    
            finally:
                #This block executes code when the for loop in generate function ends
                #Send a close event to client to close the streaming. Also add a message to inform user that email sending is complete
                yield f"event: close\ndata: Customer upload to cohort complete\n\n"
        
        return Response(stream_with_context(generate()), content_type='text/event-stream')
        workbook.close()