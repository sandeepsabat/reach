#app.py
import os
from flask import Flask, jsonify,render_template,request,redirect,url_for,Response,stream_with_context
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from sendEmailDao import addSenderEmailDetails




def create_app():
    app = Flask(__name__)
  

    #Get the absolute path of teh directory containing the current script
    bas_dir = os.path.dirname(os.path.abspath(__file__))
   

    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/fileUpload',methods=['GET','POST'])
    def fileUploadEndpoint():
        if request.method == 'POST':
            uploaded_file = request.files['file']
            fileType = request.form.get('filetype')
            filename = secure_filename(uploaded_file.filename)
            
            

            if fileType == 'customerlist':
                uploaded_file.save(os.path.join(bas_dir,'files','customerlist', filename))
        
            if fileType == 'htmlformat':
                uploaded_file.save(os.path.join(bas_dir,'files','html', filename))
            
            if fileType == 'emailbounces':
                uploaded_file.save(os.path.join(bas_dir,'files','emailbounces', filename))
            


            return redirect(url_for('index'))

        fileTypeList=['customerlist','htmlformat','emailbounces']
        return render_template('fileUpload.html',fileTypes=fileTypeList)
    
   
    
    @app.route('/inputFilesList')
    def inputFilesList():
        file_directory = os.path.join(bas_dir,'files','customerlist')

        filenames = os.listdir(file_directory)

        return render_template("fileList.html",files=filenames,header='Uploaded Customer Files')
    
    @app.route('/htmlEmailTemplatesList')
    def htmlEmailTemplatesList():
        file_directory = os.path.join(bas_dir,'files','html')

        filenames = os.listdir(file_directory)

        return render_template("fileList.html",files=filenames,header='Uploaded HTML Email Templates')
    
    @app.route('/emailBouncesList')
    def emailBouncesList():
        file_directory = os.path.join(bas_dir,'files','emailbounces')

        filenames = os.listdir(file_directory)

        return render_template("fileList.html",files=filenames,header='Uploaded Email Bounce Files')
    
    @app.route('/addSenderEmailCredentials',methods=['GET','POST'])
    def addSenderEmailCredentials():
        if request.method == 'POST':
            inputData = request.get_json()
            senderEmail = inputData['senderEmail']
            password = inputData['password']
            smtpServer = inputData['smtpServer']
            port = int(inputData['port'])
            return_message = addSenderEmailDetails(senderEmail,password,smtpServer,port)
            return jsonify({'message':return_message})
        return render_template('senderCredentialsForm.html')

    
    from sendEmailController import sendEmail_bp
    app.register_blueprint(sendEmail_bp,url_prefix='/run')

    from campaignTrackingController import campaignTracker_bp
    app.register_blueprint(campaignTracker_bp,url_prefix='/track')

    from manageCustomerController import manageCustomer_bp
    app.register_blueprint(manageCustomer_bp,url_prefix='/customer')
    

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000,use_reloader=True)
