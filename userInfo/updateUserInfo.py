import boto3
import logging
from userInfo import app
from flask import request
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

''' Loading Environment files '''
load_dotenv()

''' Configuring AWS dynamo db '''
dynamoDbResource = boto3.resource(os.getenv("AWS_DYNAMO"), region_name=os.getenv("AWS_REGION"))
''' Configuring AWS Cognito '''
cognitoClient = boto3.client(os.getenv("AWS_COGNITO"), region_name=os.getenv("AWS_REGION"))
table_name = os.getenv("DYNAMO_USER_TABLE")

''' updateUser() Since the signup service will insert the necessary information like Username, Email, Institution into the
 table, this method will update that record when user is updating their information with other data. '''


@app.route('/update-user', methods=['POST'])
def updateUser():
    response = None
    try:
        ''' Connect with User Info Dynamodb table '''
        table = dynamoDbResource.Table(table_name)
        logging.log("updateUser: Connected to table")
        ''' The key field is used to query the table '''
        key = {"email": request.json['email'],
               "institution": request.json['institution']
               }
        ''' The updateString is the query string used to update the table dynamically with different column '''
        updateString = "set "

        expressionAttribute = {}
        try:
            response = table.get_item(Key=key)
            ''' Framing the dynamic query param values and query string '''
            if 'Item' in response:
                if "pictureUrl" in request.json:
                    updateString += "pictureUrl=:p,"
                    expressionAttribute[':p'] = request.json['pictureUrl']
                if "course" in request.json:
                    updateString += "course=:c,"
                    expressionAttribute[':c'] = request.json['course']
                if "address" in request.json:
                    updateString += "address=:a,"
                    expressionAttribute[':a'] = request.json['address']
                if "phoneNumber" in request.json:
                    updateString += "phoneNumber=:n,"
                    expressionAttribute[':n'] = request.json['phoneNumber']
                if "emailTemplate" in request.json:
                    updateString += "emailTemplate=:e,"
                    expressionAttribute[':e'] = request.json['emailTemplate']
                if "paymentInfo" in request.json:
                    updateString += "paymentInfo=:pm,"
                    expressionAttribute[':pm'] = request.json['paymentInfo']

                try:
                    ''' Remove the last comma from the query string '''
                    updateString = updateString[:-1]
                    logging.log('update String is {}'.format(updateString))
                    ''' Update the user info table '''
                    response=table.update_item(
                        Key=key,
                        UpdateExpression=updateString,
                        ExpressionAttributeValues=expressionAttribute,
                        ReturnValues="UPDATED_NEW"
                    )
                    logging.log("Value updated in the table {}".format(response))
                except ClientError as e:
                    logging.error(e)
        except ClientError as e:
            logging.error(e)
    except ClientError as e:
        logging.error(e)
    return response

@app.route('/health', methods=['get'])
def healthCheck():
    return {"message":"healthy"}