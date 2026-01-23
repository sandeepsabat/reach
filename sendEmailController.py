from flask import Blueprint,request, jsonify,render_template,redirect,url_for,Response,stream_with_context
import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import openpyxl
import datetime
import os
from sendEmailDao import (createCampaigns,addEmailToCampaign,updateCampaignStatus,
                          updateEmailBounceStatus,getSenderEmailList,getSenderEmailCredentialDetails)
from manageCustomerDao import getCustomerCohortList,getCohortEmailList,getCampaignName
from createCampaignDao import getEmailTemplateList,getEmailTemplateDetails

sendEmail_bp = Blueprint("sendemail",__name__)

#Get the absolute path of teh directory containing the current script
bas_dir = os.path.dirname(os.path.abspath(__file__))



def sendEmail(recipient_email,subject_line,campaign_link,email_html_file,first_name,serial_no,sender_email,app_password,smtp_server,port):
    log_msg = ""
    
    #Read and extract the email body from html file and pass params to the email body
    with open(email_html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    #Pass params to the html file
    
    html_content_with_params = html_content.format(first_name=first_name,campaign_link=campaign_link)
    body = MIMEText(html_content_with_params,'html')

    # Create the email message by adding the sender address, recipient address, subject line,and the email body
    msg = MIMEMultipart('alternative')
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject_line
    msg.attach(body)

    #Send the email message to the recipient email id and capture the email sent time or capture error message if any
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender_email, app_password)
            server.send_message(msg)
        
        sent_date_time = datetime.datetime.now()
        log_msg = 'email sent successfully'
        disp_msg = f"Email sent to {first_name} at email:{recipient_email}"
        sent_flag = True
        return log_msg,disp_msg,sent_flag,sent_date_time
        
    except Exception as e:
        log_msg = f"Error sending email:{e}"
        disp_msg = f"Failed to sent email to {first_name} at email:{recipient_email}. Error:{e}"
        sent_flag = False
        sent_date_time = datetime.datetime.now()
        return log_msg,disp_msg,sent_flag,sent_date_time



@sendEmail_bp.route('/getCampaignInitiationData',methods=['GET']) 
def getCampaignInitationData():
        

        
        senderEmailList_wo_id = getSenderEmailList()
        senderEmailList = [{'id':index,'value':value} for index,value in enumerate(senderEmailList_wo_id)]
        cohortList_wo_id = getCustomerCohortList()
        cohortList = [{'id':index,'value':value} for index,value in enumerate(cohortList_wo_id)]
        emailTemplateList_wo_id = getEmailTemplateList()
        emailTemplateList = [{'id':index,'value':value} for index,value in enumerate(emailTemplateList_wo_id)]

        campaignInitiationDetails = {'senderEmailList':senderEmailList,'cohortList':cohortList,'emailTemplateList':emailTemplateList}

        
        return jsonify(campaignInitiationDetails)


@sendEmail_bp.route('/startCampaign',methods=['GET','POST']) # To be removed when the front end is fully functional
def startCampaign():
        if request.method == 'POST':
            cohortName = request.form.get('cohortname')
            senderEmail = request.form.get('senderemail')
            emailTemplates = request.form.get('emailtemplates')
            return render_template('campaignStarted.html',cohortname=cohortName,senderemail=senderEmail,emailtemplates=emailTemplates)

        
        senderEmailList = getSenderEmailList()
        cohortList = getCustomerCohortList()
        emailTemplateList = getEmailTemplateList()

        file_directory = os.path.join(bas_dir,'files','html')
        fileNames = os.listdir(file_directory)
        return render_template('campaignForm.html',cohortlist=cohortList,senderemails=senderEmailList,filenames=fileNames,emailtemplatelist=emailTemplateList)

@sendEmail_bp.route('/streamCampaign')
def streamCampaign():
        
        #Collect all the arguments passed by the client html
        cohortname = request.args.get('cohortName')
        senderemail = request.args.get('senderEmail')
        emailtemplates = request.args.get('emailTemplates')

        
        #Prepare for running the campaign
        subject_line,htmlFileName,emailShortCode= getEmailTemplateDetails(emailtemplates)
        campaign_name = getCampaignName(cohortname,emailShortCode)
        cohortEmailList = getCohortEmailList(cohortname)
        senderEmail,password,smtpServer,port = getSenderEmailCredentialDetails(senderemail) # Get sender mail credentails from db based on user selection of email

        #Build directory path for getting the html email template
        hmtl_file_path = os.path.join(bas_dir,'files','html')
        email_html_file = os.path.join(hmtl_file_path,htmlFileName)
        
        #Create an entry for email campaign in database
        campaign_id = createCampaigns(campaign_name,subject_line,htmlFileName) 

          
        def generate():
           
            try:
                for row in cohortEmailList:
                    serial_no = row['serialNo'] 
                    recipient_email = row['email'] 
                    first_name = row['firstName'] 
                    last_name= row['lastName']
                    # disp_msg = "Customer Details:" + first_name + " " + last_name + ",Email:" + recipient_email + ",Serial No:" + str(serial_no) + "Subject Line:" + subject_line
                    campaign_link = url_for(f'campaigntracker.trackCampaign',_external=True,name=f'{campaign_name}',timestamp=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
                    
                    log_msg,disp_msg,sent_flag,sent_date_time = sendEmail(recipient_email,subject_line,campaign_link,email_html_file,first_name,serial_no,senderEmail,password,smtpServer,port)
                    addEmailToCampaign(campaign_name,campaign_id,first_name,last_name,recipient_email,log_msg,sent_flag,sent_date_time)
                    yield f"data: {disp_msg}\n\n" #Sends message to the client html as server side events
                    
            finally:
                #This block executes code when the for loop in generate function ends
                #Send a close event to client to close the streaming. Also add a message to inform user that email sending is complete
                updateCampaignStatus(campaign_id)
                yield f"event: close\ndata: Email sending is complete\n\n"
        
        return Response(stream_with_context(generate()), content_type='text/event-stream')
        

            
@sendEmail_bp.route('/uploadEmailBounce',methods=['GET','POST'])
def uploadEmailBounce():
        if request.method == 'POST':
            fileName = request.form.get('filenames')
            startRow = int(request.form['startrow'])
            endRow = int(request.form['endrow'])
            return render_template('emailBounceUpdateStarted.html',filename=fileName,startrow=startRow,endrow=endRow)

        file_directory = os.path.join(bas_dir,'files','emailbounces')

        filenames = os.listdir(file_directory)
        return render_template('emailBounceForm.html',fileNames=filenames)    


@sendEmail_bp.route('/bounceStream')
def bounceStream():
        
        #Collect all the arguments passed by the client html
        filename = request.args.get('fileName')
        startrow = int(request.args.get('startRow'))
        endrow = int(request.args.get('endRow'))
                    
        #Configure Directory Paths
        input_excel_path = os.path.join(bas_dir,'files','emailbounces')
        excel_file_name = filename

        #Load the input excel file
        filename = os.path.join(input_excel_path,excel_file_name)
        workbook = openpyxl.load_workbook(filename,data_only=True)
        sheet = workbook['Sheet1']

        

          
        def generate():
           
            try:
                for row_cells in sheet.iter_rows(min_row=startrow,max_row=endrow):
                    recipient_email = row_cells[2].value
                    bounce_status = row_cells[8].value
                    log_msg = f"Updated bounce status of email@ {recipient_email}"
                    updateEmailBounceStatus(recipient_email)
                    yield f"data: {log_msg}\n\n" #Sends message to the client html as server side events
                    
            finally:
                #This block executes code when the for loop in generate function ends
                #Send a close event to client to close the streaming. Also add a message to inform user that email sending is complete
                yield f"event: close\ndata: Email bounce status update complete\n\n"
        
        return Response(stream_with_context(generate()), content_type='text/event-stream')
        workbook.close()
            
        