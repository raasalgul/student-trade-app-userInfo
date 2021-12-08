import boto3
import logging
from userInfo import application
from flask import request
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from datetime import datetime

''' Loading Environment files '''
load_dotenv()

''' Configuring AWS S3 '''
s3 = boto3.resource(os.getenv('AWS_S3'), region_name=os.getenv('AWS_REGION'))

'''verificationDoc() method is used to upload user college verification document to s3 and 
the admin will verify them based on this document'''


@application.route('/verification-doc',methods=['POST'])
def verificationDoc():
    try:
        '''Check whether the file is in the request param and if it not return a message stating no file'''
        if 'file' not in request.files:
            logging.info('File not in the part')
            return {"message":"No file"}
        uploadedFile=request.files['file']
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        logging.info('Uploaded file name is {}'.format(uploadedFile.filename))
        '''We will be forming a folder like structure in S3 where profile-picture will be the folder and 
        the file name will start with Id (email Id) concatenate with current time followed by the uploaded file name'''
        response = s3.meta.client.upload_file(Filename=uploadedFile.filename,Bucket='test-cool',
                                   Key='verification-doc/id-'+current_time+"-"+uploadedFile.filename)
        logging.info('Uploaded the picture to S3 {}'.format(response))
    except ClientError as e:
        logging.error(e)
    #return {"message": "Bellow! Success"}
    return response