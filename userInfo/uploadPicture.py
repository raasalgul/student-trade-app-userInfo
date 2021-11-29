import boto3
import logging
from userInfo import app
from flask import request
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from datetime import datetime

''' Loading Environment files '''
load_dotenv()

''' Configuring AWS S3 '''
s3 = boto3.resource(os.getenv('AWS_S3'), region_name=os.getenv('AWS_REGION'))

'''uploadProfilePicture() method is used to upload user profile picture to s3 and upload that url to DynamoDb'''


@app.route('/upload-profile-picture', methods=['POST'])
def uploadProfilePicture():
    logging.log('uploadProfilePicture: the request files parameter is {}'.format(request.files))
    try:
        '''Check whether the file is in the request param and if it not return a message stating no file'''
        if 'file' not in request.files:
            logging.log('File not in the part')
            return {"message": "No file"}
        uploadedFile = request.files['file']
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        logging.log('Uploaded file name is {}'.format(uploadedFile.filename))
        '''We will be forming a folder like structure in S3 where profile-picture will be the folder and 
        the file name will start with Id (email Id) concatenate with current time followed by the uploaded file name'''
        response=s3.meta.client.upload_file(Filename=uploadedFile.filename, Bucket='test-cool',
                                            Key='profile-picture/id-' + current_time + "-" + uploadedFile.filename)
        logging.log('Uploaded the picture to S3 {}'.format(response))
    except ClientError as e:
        logging.error(e)
    #return {"message": "Bellow! Success"}
    return response