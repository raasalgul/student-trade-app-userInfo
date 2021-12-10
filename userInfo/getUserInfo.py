import boto3
import logging
from userInfo import application
from flask import request
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
import json

''' Loading Environment files '''
load_dotenv()

''' Configuring AWS dynamo db '''
dynamoDbResource = boto3.resource(os.getenv("AWS_DYNAMO"), region_name=os.getenv("AWS_REGION"))
''' Configuring AWS Cognito '''
cognitoClient = boto3.client(os.getenv("AWS_COGNITO"), region_name=os.getenv("AWS_REGION"))
table_name = os.getenv("DYNAMO_USER_TABLE")

''' getUser() This method get the necessary user information from the user dynamo table. '''


@application.route('/get-user', methods=['POST'])
def getUser():
    response = None
    try:
        bearer = request.headers.get('Authorization')
        bearer = bearer.replace("Bearer ", "")
        responseUserData = cognitoClient.get_user(AccessToken=bearer)
        logging.info("Response user data {}".format(responseUserData))

        if responseUserData['ResponseMetadata']['HTTPStatusCode'] == 200:
            ''' Connect with User Info Dynamodb table '''
            table = dynamoDbResource.Table(table_name)
            logging.info("getUser: Connected to table")
            ''' The key field is used to query the table '''
            key = {"email": request.json['email'],
                   "institution": request.json['institution']
                   }
            ''' Get the entire items from the table '''
            response = table.get_item(Key=key)
            logging.info("getUser: Got response from table {}".format(response))
    except ClientError as e:
        logging.error(e)
    return response


@application.route("/health", methods=['GET'])
def healthCheck():
    return json.dumps({'status': 'healthy'}), 200, {'ContentType': 'application/json'}


@application.route("/", methods=['GET'])
def healthCheck():
    return json.dumps({'status': 'success'}), 200, {'ContentType': 'application/json'}
