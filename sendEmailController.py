from flask import Blueprint,request, jsonify,render_template,redirect,url_for,Response,stream_with_context
import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import openpyxl
import datetime
import os
from sendEmailDao import createCampaigns,addEmailToCampaign,updateCampaignStatus

sendEmail_bp = Blueprint("sendemail",__name__)

#Get the absolute path of teh directory containing the current script
bas_dir = os.path.dirname(os.path.abspath(__file__))

#Email credentials and details
sender_email = "harsha.n@mypace-learning.com"  # Replace with your email address
app_password = "RCszMsI1"  # Replace with your generated app password

# Set up the SMTP server and send the email
smtp_server = "us2.smtp.mailhostbox.com"  # For Gmail
port = 587  # For TLS

def sendEmail(recipient_email,subject_line,email_html_file,first_name,serial_no):
    log_msg = ""
    
    #Read and extract the email body from html file and pass params to the email body
    with open(email_html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    #Pass params to the html file
    html_content_with_params = html_content.format(first_name=first_name) 
    body = MIMEText(html_content_with_params,'html')

    # Create the email message by adding the sender address, recipient address, subject line,and the email body
    msg = MIMEMultipart('alternative')
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject_line
    msg.attach(body)

    #Send the email message to the recipient email id and capture the email sent time or capture error message if any
    try:
        # context = ssl.create_default_context()
        # with smtplib.SMTP(smtp_server, port) as server:
        #     server.starttls(context=context)
        #     server.login(sender_email, app_password)
        #     server.send_message(msg)
        
        log_msg = f"Sent email at slno {serial_no} at time: " + datetime.datetime.now().strftime("%d/%m/%Y,%H:%M:%S")
        return log_msg
        
    except Exception as e:
        log_msg = f"Error sending email at slno {serial_no}:" + e
        return log_msg

    

@sendEmail_bp.route('/startCampaign',methods=['GET','POST'])
def startCampaign():
        if request.method == 'POST':
            fileName = request.form.get('filenames')
            startRow = int(request.form['startrow'])
            endRow = int(request.form['endrow'])
            return render_template('campaignStarted.html',filename=fileName,startrow=startRow,endrow=endRow)

        file_directory = os.path.join(bas_dir,'files','excel')

        filenames = os.listdir(file_directory)
        return render_template('campaignForm.html',fileNames=filenames)

@sendEmail_bp.route('/stream')
def stream():
        
        #Collect all the arguments passed by the client html
        filename = request.args.get('fileName')
        startrow = int(request.args.get('startRow'))
        endrow = int(request.args.get('endRow'))
                    
        #Configure Directory Paths
        input_excel_path = os.path.join(bas_dir,'files','excel')
        hmtl_file_path = os.path.join(bas_dir,'files','html')
        excel_file_name = filename

        #Load the input excel file
        filename = os.path.join(input_excel_path,excel_file_name)
        workbook = openpyxl.load_workbook(filename)
        sheet = workbook['Sheet1']

        #From the input excel file extract the campaign name, the email html file name and subject line
        campaign_name = sheet['B1'].value
        html_file_name = sheet['B2'].value
        email_html_file = os.path.join(hmtl_file_path,html_file_name)
        subject_line = sheet['B3'].value

        #Create an entry for email campaign in database
        campaign_id = createCampaigns(campaign_name,excel_file_name,html_file_name)

          
        def generate():
           
            try:
                for row_cells in sheet.iter_rows(min_row=startrow,max_row=endrow):
                    serial_no = row_cells[2].value
                    recipient_email = row_cells[5].value
                    first_name = row_cells[3].value
                    last_name= row_cells[4].value
                    log_msg = sendEmail(recipient_email,subject_line,email_html_file,first_name,serial_no)
                    row_cells[7].value = log_msg
                    workbook.save(filename)
                    addEmailToCampaign(campaign_name,campaign_id,first_name,last_name,recipient_email,log_msg)
                    yield f"data: {log_msg}\n\n" #Sends message to the client html as server side events
                    
            finally:
                #This block executes code when the for loop in generate function ends
                #Send a close event to client to close the streaming. Also add a message to inform user that email sending is complete
                updateCampaignStatus(campaign_id)
                yield f"event: close\ndata: Email sending is complete\n\n"
        
        return Response(stream_with_context(generate()), content_type='text/event-stream')
        workbook.close()

            
            
            
        