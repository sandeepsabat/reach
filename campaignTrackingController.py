from flask import Blueprint,request, jsonify,render_template,redirect,url_for,Response,stream_with_context
import datetime
import os
import openpyxl
from sendEmailDao import createCampaigns
from trackCampaignDao import addTrackableLinkToCampaign,addEmailOpenEntryForCampaign


campaignTracker_bp = Blueprint("campaigntracker",__name__)

#Get the absolute path of teh directory containing the current script
bas_dir = os.path.dirname(os.path.abspath(__file__))

@campaignTracker_bp.route('/generateTrackableLink',methods=['GET','POST'])
def generateTrackableLink():

    if request.method == 'POST':
        fileName = request.form.get('filenames')

        #Configure Directory Paths
        input_excel_path = os.path.join(bas_dir,'files','excel')
        excel_file_name = fileName

        #Load the input excel file
        filename = os.path.join(input_excel_path,excel_file_name)
        workbook = openpyxl.load_workbook(filename)
        sheet = workbook['Sheet1']

        #From the input excel file extract the campaign name and html file name
        campaign_name = sheet['B1'].value
        html_file_name = sheet['B2'].value

        #Create an entry for campaign
        campaign_id = createCampaigns(campaign_name,excel_file_name,html_file_name)
        campaign_link = url_for(f'campaigntracker.trackCampaign',_external=True,name=f'{campaign_name}')
        # final_link = campaign_link + f'?name={campaign_name}'
        addTrackableLinkToCampaign(campaign_name,campaign_link)
        return render_template('trackableLink.html',campaignName=campaign_name,trackableLink=campaign_link)



    file_directory = os.path.join(bas_dir,'files','excel')
    filenames = os.listdir(file_directory)
    return render_template('generateTrackLinkForm.html',fileNames=filenames)

@campaignTracker_bp.route('/trackCampaign',methods=['GET'])
def trackCampaign():
    campaignName = request.args.get('name')
    addEmailOpenEntryForCampaign(campaignName)
    return '',204