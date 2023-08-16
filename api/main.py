from utilities import checkFile_Extension,uploadFileAndInsertRecords
from flask import Flask,jsonify, request,abort
from sqlalchemy import create_engine 
from boto3 import client,session,resource
from pandas import json_normalize
from json import loads, dumps
import pandas as pd
import json
import os

#config variables
app = Flask(__name__)
connection_db = 'postgresql://postgres_user_pg:postgres_pwd_pg@localhost/company_pg'
app.config["SQLALCHEMY_DATABASE_URI"] = connection_db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = create_engine(connection_db)

#create s3 object
s3 = resource(
    's3',
    aws_access_key_id='AKIA5NEVWXTGKGDAEVPG',
    aws_secret_access_key='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'
)

# Receive historical data from CSV files and Upload these files to the new DB, and upload the file in S3
@app.route('/files',methods=["POST"])
def uploadRecordsAndCSVfileInS3():
    try:
        responseTxt = ""
        data = request.get_json()
        file = data['file']
        head, filename = os.path.split(file)
        time_stamp = pd.Timestamp.now()
        strTime = str(time_stamp.year)+str(time_stamp.month)+str(time_stamp.day)+str(time_stamp.hour)+str(time_stamp.minute)+str(time_stamp.second)
        if checkFile_Extension(filename):
            if 'hired' in filename.lower() :
                tableName = 'hired_employees'
                bucketName = 'pghired'
                newFileName = tableName+strTime+'.csv'
                colnames=['id', 'name', 'datetime', 'department_id','job_id'] 
                df_nullRecords = uploadFileAndInsertRecords(filename,newFileName,tableName,engine,s3,bucketName,file,time_stamp,colnames)
            elif 'departments' in filename.lower():
                tableName = 'departments'
                bucketName = 'pgdepartments'
                newFileName = tableName+strTime+'.csv'
                colnames=['id', 'department'] 
                df_nullRecords = uploadFileAndInsertRecords(filename,newFileName,tableName,engine,s3,bucketName,file,time_stamp,colnames)
            elif 'jobs' in filename.lower():
                tableName = 'jobs'
                bucketName = 'pgjobs'
                newFileName = tableName+strTime+'.csv'
                colnames=['id', 'job'] 
                df_nullRecords = uploadFileAndInsertRecords(filename,newFileName,tableName,engine,s3,bucketName,file,time_stamp,colnames)
            else:
                df_nullRecords = pd.DataFrame()
                responseTxt = jsonify({"message":"Please check the file name contain the word: job,department or hire_employee"})

            if df_nullRecords.shape[0] >=1:
                df_nullRecords = df_nullRecords.drop(['last_update'], axis=1)
                result = df_nullRecords.to_json(orient="records")
                parsed = loads(result)
                responseTxt= jsonify(message=f"{df_nullRecords.shape[0]} records have not been inserted because some records are null, please check all of them and try again.",
                            category="Error",
                            data=parsed,
                            status=400
                )
            else:
                if responseTxt == "":
                    responseTxt = jsonify({"Success":"CSV File and records have been inserted successfully"})
            
    except:
        return jsonify({"Error Message":"CSV File and records have not been inserted"})
    return responseTxt

if __name__=="__main__":
    app.run(host="0.0.0.0",port=80)