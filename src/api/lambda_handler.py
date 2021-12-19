import json
import boto3
from boto3.dynamodb.conditions import Key
import random
import string

# global dynamodb client
dynamo = boto3.client('dynamodb')

# Constants
BAD_REQUEST_MESSAGE = 'Bad Request: Unsupported HTTP operation'
BASE_URI = 'https://tes7ayyf28.execute-api.us-east-1.amazonaws.com/v0/url-shortener/'
HTTP_200 = 200
HTTP_302 = 302
HTTP_500 = 500
HTTP_GET = 'GET'
HTTP_POST = 'POST'
INTERNAL_ERROR_MESSAGE = 'Internal Server Error: There was an issue processing the request'
NOT_FOUND_MESSAGE = 'Not Found: The requested url was not found in our system'
PROJECTION_COLUMN = 'original'
SUCCESS_MESSAGE = 'ok'
TABLE_NAME = 'url-shortener'
UNKNOWN_URL = 'unknown'

def lambda_handler(event, context):
    originalUrl = event.get('originalUrl', '')
    shortenedUrl = event.get('shortenedUrl', '')
    httpMethod = event.get('httpMethod')
    if httpMethod == HTTP_GET:
        queryResult = executeQuery(shortenedUrl)
        original = queryResult.get('Item', {}).get('original', {}).get('S', UNKNOWN_URL)
        statusCode = queryResult.get('ResponseMetadata', {}).get('HTTPStatusCode', HTTP_500)
        if statusCode == HTTP_200:
            if original == UNKNOWN_URL:
                raise Exception(NOT_FOUND_MESSAGE)
            return buildResponse(HTTP_302, original)
        raise Exception(INTERNAL_ERROR_MESSAGE)
    elif httpMethod == HTTP_POST:
        shortenedUrl = generateShortenedUrl()
        putResult = dynamo.put_item(
            TableName=TABLE_NAME,
            Item={
                'shortened': {
                    'S': shortenedUrl
                },
                'original': {
                    'S': originalUrl
                }
            })
        statusCode = putResult.get('ResponseMetadata', {}).get('HTTPStatusCode', HTTP_500)
        if statusCode == HTTP_200:
            return buildResponse(HTTP_200, BASE_URI+shortenedUrl)
        raise Exception(INTERNAL_ERROR_MESSAGE)
    else:
        raise Exception(BAD_REQUEST_MESSAGE)

# using ascii letters (case-sensitive) and digits 0-9
# this allows for 62^6 (~56.8 billion) unique shortened url paths
# we generate a random path until we find one that is not in use
def generateShortenedUrl():
    while True:
        path = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        original = executeQuery(path).get('Item', {}).get('original', {}).get('S', UNKNOWN_URL)
        if original == UNKNOWN_URL:
            return path

# executes a dynamodb query based on the partition key (shortenedUrl) and maps the
# response to the corresponding originalUrl 
def executeQuery(shortenedUrl):
    keyMap = {'shortened': {'S': shortenedUrl}}
    return dynamo.get_item(TableName=TABLE_NAME, Key=keyMap, ProjectionExpression=PROJECTION_COLUMN)
    
def buildResponse(code, body):
    return {
        'statusCode': code,
        'body': body
    }
