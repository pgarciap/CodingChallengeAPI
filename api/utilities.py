import os
from sqlalchemy import create_engine 
from flask import abort
import pandas as pd

# Check file extension, the file must be in csv format
def checkFile_Extension(filename):
    checkfile = False
    try:
        file_extension = os.path.splitext(filename)
        if file_extension[1] == ".CSV" or file_extension[1] == ".csv":
                checkfile = True
    except Exception as error:
        return "An exception occurred:" + type(error).__name__
    return checkfile

# create a connection in posgrest by sqlalchemy
def connectionPosgress(engine):
    try:
        conn = engine.connect()
        return conn
    except:
        return "Something went wrong when creating the connection"

# insert records from csv to database by pandasdf and sqlalchemy
def insertRecords(file,tableName,engine,time_stamp,colnames):
    conn = connectionPosgress(engine)
    try:
        df = pd.read_csv(file,sep=',', names=colnames, header=None)
        df['last_update'] = time_stamp
        [df_def,df_nullRecords] = cleanNullRecords(df,tableName)
        if df_def.shape[0] >=1:
            df_def.to_sql(tableName, con=conn, if_exists='append',index=False)
        conn.close()
        return df_nullRecords
    except:
        conn.close()
        return "Something went wrong when inserting data in the " + tableName + " table."

# write csv file to s3
def writeCSVFileToS3(s3,bucket_name,file_name,file):
    try:
        s3.Object(bucket_name, file_name).put(Body=file)
    except:
        return "Something went wrong when writing csv file to S3."

# insert csv upload trace log
def insertTrackingRecord(OriginalFilelName,newFileName,tableName,engine,time_stamp):
    conn = connectionPosgress(engine)
    try:
        data = {'OriginalFilelName': [OriginalFilelName],
		'newFileName': [newFileName],
        'time_stamp':[time_stamp],
        'tableName':[tableName]}

        df = pd.DataFrame(data)
        df.to_sql('Traking_files', con=conn, if_exists='append',index=False)
        conn.close()
    except Exception as error:
        conn.close()
        return "Something went wrong when inserting data in the " + tableName + " table."
        
        
# upload csv file and inserd records into the database
def uploadFileAndInsertRecords(filename,newFileName,tableName,engine,s3,bucketName,file,time_stamp,colnames):
    try:
        writeCSVFileToS3(s3,bucketName,newFileName,file)
        df_nullRecords = insertRecords(file,tableName,engine,time_stamp,colnames)
        insertTrackingRecord(filename,newFileName,tableName,engine,time_stamp)
        return df_nullRecords
    except Exception as error:
        return "Something went wrong when uploading file in S3 or inserting Records. " + "An exception occurred:" + type(error).__name__

# Clean all null records
def cleanNullRecords(df,tableName):
    try:
        if df.shape[0] >=1:
            if tableName.lower() == "hired_employees" :
                df_def = df[df['job_id'].notnull() & df['department_id'].notnull() & df['id'].notnull()]
                df_def['job_id'] = df_def['job_id'].astype(int)
                df_def['department_id'] = df_def['department_id'].astype(int)
                df_nullRecords = df[df['job_id'].isnull() | df['department_id'].isnull() | df['id'].isnull()]
            elif tableName.lower() == "departments":
                df_def = df[df['department'].notnull() & df['id'].notnull()]
                df_nullRecords = df[df['department'].isnull() | df['id'].isnull()]
            elif tableName.lower() == "jobs":
                df_def = df[df['job'].notnull() & df['id'].notnull()]
                df_nullRecords = df[df['job'].isnull() | df['id'].isnull()]
            else:
                df_def = pd.DataFrame()
                df_nullRecords = pd.DataFrame()
            
        return [df_def,df_nullRecords]
    except Exception as error:
        return "Something went wrong when clean null records in the " + tableName + " table. " + "An exception occurred:", type(error).__name__
