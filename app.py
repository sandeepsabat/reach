#app.py
import os
from flask import Flask, jsonify,render_template,request,redirect,url_for,Response,stream_with_context
from pymongo import MongoClient
from werkzeug.utils import secure_filename




def create_app():
    app = Flask(__name__)
  

    #Get the absolute path of teh directory containing the current script
    bas_dir = os.path.dirname(os.path.abspath(__file__))
   

    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/fileUpload')
    def fileUploadEndpoint():
        return render_template('fileUpload.html')
    
    @app.route('/fileUpload', methods=['POST'])
    def upload_files():
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        root,extension = os.path.splitext(filename)

        if extension == '.xlsx':
            uploaded_file.save(os.path.join(bas_dir,'files','excel', filename))
        
        if extension == '.html':
            uploaded_file.save(os.path.join(bas_dir,'files','html', filename))

        return redirect(url_for('index'))
    
    @app.route('/inputFilesList')
    def inputFilesList():
        file_directory = os.path.join(bas_dir,'files','excel')

        filenames = os.listdir(file_directory)

        return render_template("fileList.html",files=filenames,header='Uploaded Input Files')
    
    @app.route('/htmlEmailTemplatesList')
    def htmlEmailTemplatesList():
        file_directory = os.path.join(bas_dir,'files','html')

        filenames = os.listdir(file_directory)

        return render_template("fileList.html",files=filenames,header='Uploaded HTML Email Templates')
    
    from sendEmailController import sendEmail_bp
    app.register_blueprint(sendEmail_bp,url_prefix='/run')

    from campaignTrackingController import campaignTracker_bp
    app.register_blueprint(campaignTracker_bp,url_prefix='/track')
    

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000,use_reloader=True)
