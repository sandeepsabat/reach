#app.py
import os
from dotenv import load_dotenv
from flask import Flask, jsonify,render_template,request,redirect,url_for,Response,stream_with_context
from flask_jwt_extended import JWTManager
from datetime import timedelta, datetime
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from sendEmailDao import addSenderEmailDetails
from flask_cors import cross_origin,CORS

load_dotenv()


def create_app():
    app = Flask(__name__)
    CORS(app,resources={r"/*":{"origins":"http://localhost:5173","methods":["POST","OPTIONS","GET"],"allow_headers":["Content-Type","Authorization"]}})
  

    #Get the absolute path of teh directory containing the current script
    bas_dir = os.path.dirname(os.path.abspath(__file__))

    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['MONGO_MAIN'] = os.getenv('MONGO_MAIN')
    client = MongoClient(app.config['MONGO_URI'])
    app.db = client[app.config['MONGO_MAIN']]


    #Security-Keys
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')


    access_secs = int(os.getenv('JWT_ACCESS_EXPIRES'))
    refresh_secs = int(os.getenv('JWT_REFRESH_EXPIRES'))
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=access_secs)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(seconds=refresh_secs)

    

    # Create TTL index for token_blocklist
    ttl_seconds = refresh_secs + 60
    app.db.token_blocklist.create_index("created_at", expireAfterSeconds=ttl_seconds)
    app.db.token_blocklist.create_index("jti", unique=True)


    jwt = JWTManager(app)
    @jwt.token_in_blocklist_loader
    def check_if_revoked(jwt_header, jwt_payload):
        jti = jwt_payload.get("jti")
        return app.db.token_blocklist.find_one({"jti": jti}) is not None

    @jwt.revoked_token_loader
    def revoked(jwt_header, jwt_payload):
        return jsonify({"msg": "Token revoked"}), 401

    @jwt.expired_token_loader
    def expired(jwt_header, jwt_payload):
        return jsonify({"msg": "Token expired"}), 401
   

    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/uploadfile',methods=['POST','OPTIONS'])
    def fileUploadFromFrontEnd():
        if request.method == 'POST' or request.method =='OPTIONS':
            returnMessage = ''
            try:

                uploaded_file = request.files['file']
                fileType = request.form.get('filetype')
                filename = secure_filename(uploaded_file.filename)
                
                

                if fileType == 'customerlist':
                    uploaded_file.save(os.path.join(bas_dir,'files','customerlist', filename))
            
                if fileType == 'htmlformat':
                    uploaded_file.save(os.path.join(bas_dir,'files','html', filename))
                
                if fileType == 'emailbounces':
                    uploaded_file.save(os.path.join(bas_dir,'files','emailbounces', filename))
                

                returnMessage = {'message':"File uploaded successfully"}
                

            except Exception as e: 

                returnMessage = {'message':f'Error: {e}'}
    

            return returnMessage
        
            

        
    
    @app.route('/fileUpload',methods=['GET','POST']) # This method to be removed once the front end is fully functional
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
            

            returnMessage = {'message':"File uploaded successfully"}
            #return redirect(url_for('index'))
            return returnMessage

        fileTypeList=['customerlist','htmlformat','emailbounces']
        return render_template('fileUpload.html',fileTypes=fileTypeList)
    
    @app.route('/viewFileList',methods=['GET','OPTIONS'])
    def viewFileList():
        if request.method == 'GET' or request.method == 'OPTIONS':
            filetype = request.args.get('filetype')
            filenames = []
            

            if filetype == 'customerlist':
                file_directory = os.path.join(bas_dir,'files','customerlist')
                filenames_no_key = os.listdir(file_directory)
                filenames = [{"id":index,"filename":value} for index, value in enumerate(filenames_no_key)]
                

                
            if filetype == 'htmlformat':
                file_directory = os.path.join(bas_dir,'files','html')
                filenames_no_key = os.listdir(file_directory)
                filenames = [{"id":index,"filename":value} for index, value in enumerate(filenames_no_key)]
                
            if filetype == 'emailbounces':
                file_directory = os.path.join(bas_dir,'files','emailbounces')
                filenames_no_key = os.listdir(file_directory)
                filenames = [{"id":index,"filename":value} for index, value in enumerate(filenames_no_key)]
                
            
            return jsonify(filenames)


    
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
    @cross_origin(origins="http://localhost:5173",methods=['GET','POST'])
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

    
    from auth import auth_bp
    app.register_blueprint(auth_bp,url_prefix='/auth')

    from createCampaignController import createCampaign_bp
    app.register_blueprint(createCampaign_bp,url_prefix='/campaign')

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
