from flask import Blueprint,request, jsonify,render_template,redirect,url_for,Response,stream_with_context
from bson import json_util
import openpyxl
import datetime
import os
from manageUserDao import getUserList



manageUser_bp = Blueprint("manageuser",__name__)

#Get the absolute path of teh directory containing the current script
bas_dir = os.path.dirname(os.path.abspath(__file__))

@manageUser_bp.route('/getUserList',methods=['GET'])
def getUsers():

    users = getUserList()
    user_json = json_util.dumps(users)
    return jsonify(user_json)