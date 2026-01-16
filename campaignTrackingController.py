from flask import Blueprint,request, jsonify,render_template,redirect,url_for,Response,stream_with_context,send_file
import datetime
import os
import openpyxl
from sendEmailDao import createCampaigns
from trackCampaignDao import addTrackableLinkToCampaign,addEmailOpenEntryForCampaign,getSentEmailsForCampaign,getCampaignNameList,getCampaignsEmailStats,getDatewiseEmailStats,getBouncesCampaignWise
from bson import json_util
import operator
import json
import base64
import matplotlib
matplotlib.use('Agg')# Use the Agg backend for non-interactive image generation
#Using the above line of code suppresses the warning "UserWarning: Starting a Matplotlib GUI outside of the main thread will likely fail."
#Using the above line of code however will prevent from plt.show() to work if it is required
import matplotlib.pyplot as plt
import io
from textwrap import wrap
from PIL import Image



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
    img = Image.new('RGB',(100,100),color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr,format='PNG')
    img_byte_arr.seek(0)
    return send_file(img_byte_arr,mimetype='image/png',download_name='generated_image.')

@campaignTracker_bp.route('/getEmailListForCampaign',methods=['GET','POST'])
def getEmailListForCampaign():
    campaignNameList = getCampaignNameList()

    if request.method == 'POST':
        inputData = request.get_json()
        campaignName = inputData['data']
        sentEmailList = getSentEmailsForCampaign(campaignName)
        sentEmailList_json = json_util.dumps(sentEmailList)
        return jsonify({'message':sentEmailList_json})
    
    return render_template('sentEmailReport.html',campaignnames=campaignNameList)

#Define a function for returning an plot image by taking x and y values
def getBarGraphPlotImage(x_values,y_values,xlabel,ylabel,title):
    #Create the plot
    fig,ax = plt.subplots(figsize=(10,6)) # specifiy the size of the plot
    bar_var = ax.bar(x_values,y_values,color=['red', 'yellow', 'orange', 'purple','green','blue']) #Assign the bar plot to a variable
    ax.bar_label(bar_var,label_type='edge') #Add labels to rge bar, 'edge' places labels on top
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    # Wrap labels to a specified width (e.g., 10 characters)
    # ax.set_xticks(x_values) # Adding this line suppresses warning "UserWarning: set_ticklabels() should only be used with a fixed number of ticks, i.e. after set_ticks() or using a FixedLocator."
    # wrapped_labels = ['\n'.join(wrap(l, 10)) for l in x_values] #This line wraps the labels
    # ax.set_xticklabels(wrapped_labels) #This line adds the wrapped labels in X-axis
    ax.tick_params(axis='x',labelrotation=45)#Rotates the x-axis label by 45%

    #Save plot to a BytesIO object (in memory file)
    img_data = io.BytesIO()
    plt.savefig(img_data,format='png',bbox_inches='tight')
    plt.close(fig) # close the figure to free memory

    #Encode the image as Base64 for embedding into HTML
    img_data.seek(0)
    img_base64 = base64.b64encode(img_data.getvalue()).decode('utf8')
    return img_base64

#Create a page to render all the charts related to campaign
@campaignTracker_bp.route('/campaignsEmailStats',methods=['GET'])
def campaignEmailStats():
    #Create bar graph plot for 'Email Sent by Campaigns'
    campaignList = getCampaignsEmailStats()
    plt1_x_values = list(map(operator.itemgetter('campaignName'),campaignList))
    plt1_y_values = list(map(operator.itemgetter('emailCount'),campaignList))
    plt1_img = getBarGraphPlotImage(plt1_x_values,plt1_y_values,'Campaigns','Sent Email Count','Email Sent By Campaigns')

    #Create bar graph plot for 'Email sent by Date'
    datewiseList = getDatewiseEmailStats()
    plt2_x_values = list(map(operator.itemgetter('runDate'),datewiseList))
    plt2_y_values = list(map(operator.itemgetter('emailCount'),datewiseList))
    plt2_img = getBarGraphPlotImage(plt2_x_values,plt2_y_values,'Campaign Run Date','Sent Email Count','Email Sent By Date')

    #Create bar graph plot for 'Email Bounces by Campaigns'
    emailBounceList = getBouncesCampaignWise()
    plt3_x_values = list(map(operator.itemgetter('campaignName'),emailBounceList))
    plt3_y_values = list(map(operator.itemgetter('bounceCount'),emailBounceList))
    plt3_img = getBarGraphPlotImage(plt3_x_values,plt3_y_values,'Campaigns','Bounce Count','Email Bounces By Campaigns')
    
    
    return render_template('campaignEmailGraph.html',plot1_url=plt1_img,plot2_url=plt2_img,plot3_url=plt3_img)