from flask import Blueprint,request, jsonify,render_template,redirect,url_for,Response,stream_with_context
import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import openpyxl
import datetime
import os
from createCampaignDao import createEmailTemplate



createCampaign_bp = Blueprint("createcampaign",__name__)

#Get the absolute path of teh directory containing the current script
bas_dir = os.path.dirname(os.path.abspath(__file__))


@createCampaign_bp.route('/addEmailTemplate',methods=['GET','POST'])
def addEmailTemplate():
    

    if request.method == 'POST':
            inputData = request.get_json()
            templateName = inputData['templateName']
            description = inputData['description']
            subjectLine = inputData['subjectLine']
            fileName = inputData['fileName']
            shortCode = inputData['shortCode']

            return_message = createEmailTemplate(templateName,description,subjectLine,fileName,shortCode)
            return jsonify({'message':return_message})
    
    file_directory = os.path.join(bas_dir,'files','html')
    fileNames = os.listdir(file_directory)
    return render_template('emailTemplateForm.html',fileNames=fileNames)


    