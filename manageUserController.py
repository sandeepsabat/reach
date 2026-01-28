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
    userJSONList =[]

    for index, value in enumerate(users):
        item = {
            'id':index+1,
            'name':value['name'],
            'email':value['email'],
            'role':value['role'],
            'created_at':value['created_at'].strftime('%d-%m-%Y %H:%M:%S'),
            'updated_at':value['updated_at'].strftime('%d-%m-%Y %H:%M:%S')
        }
        userJSONList.append(item)

    
    return jsonify(userJSONList)