# -*- coding: utf-8 -*-

__version__ = "0.0.3"

def main(event, context):
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "statusDescription": "200 OK",
        "headers": {
            "Set-cookie": "cookies",
            "Content-Type": "application/json"
        },
        "body": "version = {}".format(__version__)
    }
