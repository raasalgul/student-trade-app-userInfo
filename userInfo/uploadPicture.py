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

''' Configuring AWS Cognito '''
cognitoClient = boto3.client(os.getenv("AWS_COGNITO"), region_name=os.getenv("AWS_REGION"))

''' Configuring AWS dynamo db '''
dynamoDbResource = boto3.resource(os.getenv("AWS_DYNAMO"), region_name=os.getenv("AWS_REGION"))

table_name = os.getenv("DYNAMO_USER_TABLE")

bucket_name = os.getenv("S3_BUCKET")

'''uploadProfilePicture() method is used to upload user profile picture to s3 and upload that url to DynamoDb'''


@application.route('/upload-profile-picture', methods=['POST'])
def uploadProfilePicture():
    logging.info('uploadProfilePicture: the request files parameter is {}'.format(request.files))
    try:
        bearer = request.headers.get('Authorization')
        bearer = bearer.replace("Bearer ", "")
        responseUserData = cognitoClient.get_user(AccessToken=bearer)
        logging.info("Response user data {}".format(responseUserData))
        print(responseUserData)
        userEmail = responseUserData['UserAttributes'][3]
        print(userEmail['Value'])
        userEmail = userEmail['Value']
        if responseUserData['ResponseMetadata']['HTTPStatusCode'] == 200:
            '''Check whether the file is in the request param and if it not return a message stating no file'''
            if 'file' not in request.files:
                logging.info('File not in the part')
                return {"message": "No file"}
            uploadedFile = request.files['file']
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            logging.info('Uploaded file name is {}'.format(uploadedFile.filename))
            s3_key='profile-picture/id-' + current_time + "-" + uploadedFile.filename
            '''We will be forming a folder like structure in S3 where profile-picture will be the folder and 
            the file name will start with Id (email Id) concatenate with current time followed by the uploaded file name'''
            response=s3.meta.client.upload_fileobj(uploadedFile,bucket_name,s3_key,
                                                ExtraArgs={"ACL": "public-read"})
            logging.info('Uploaded the picture to S3 {}'.format(response))
            s3Url="{0}.s3.amazonaws.com/{1}".format(bucket_name, s3_key)
            s3Url = "https://" + s3Url.replace(" ", "+").replace(":", "%3A")
            print('Uploaded the picture to S3 {}'.format(s3Url))
            #s3Url="bello"
            table = dynamoDbResource.Table(table_name)
            institution = request.form['institution']
            responseTable = table.update_item(
            Key={
                    "email": userEmail,
                    "institution": institution
                },
            UpdateExpression='SET pictureUrl = :s',
            ExpressionAttributeValues = {':s': s3Url},ReturnValues = "UPDATED_NEW")
            return {"status": "Success"}
        else:
            return {"status": "Failure"}
    except ClientError as e:
        logging.error(e)