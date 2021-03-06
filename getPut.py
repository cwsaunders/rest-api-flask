import json
import pymysql
import os
import sys
import logging
import boto3
from flask import Flask, render_template, request 
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/create', methods=['PUT'])
def apiPut():
    if request.method == 'PUT':
        continueProgram = True
        # set mysql connect parameters
        db_name = "webforum"
        db_port = 3306
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        reqDecode = request.data.decode('UTF-8')
        reqDict = json.loads(reqDecode)
        try: # code to avoid overriding connection object that already exists (future refactor)
            conn = pymysql.connect(
                user=os.environ['user'], password=os.environ['password'], host=os.environ['host'],
                port=db_port, database=db_name)
        except pymysql.MySQLError as e:
            logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
            logger.error(e)
            statusCode = 505
            continueProgram = False
        logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
        """
        This function PUTs content to a MySQL RDS instance
        """
        if continueProgram == True:
            try:
                body = reqDict['body']
                title = reqDict['title']
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO thread (title, body) VALUES (%s, %s)", (title, body))
                conn.commit()
                statusCode = 200
            except Exception as e:
                logger.error('Fatal exception occurred.', exc_info=e)
                statusCode = 500
        elif continueProgram == False:
            print("not entering body & title try block area")
        return {
            "statusCode": statusCode, 
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,PUT"
            }
        }

# logger 67-68
@app.route('/health', methods=['GET'])
def apiHealth():
    if request.method == 'GET':
        return '200'


@app.route('/saved', methods=['GET'])
def apiGet():
    if request.method == 'GET':
        continueProgram = True
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        if continueProgram == True:
            try:
                cnx = pymysql.connect(user=os.environ['user'],
                                    password=os.environ['password'],
                                    host=os.environ['host'],
                                    database='webforum',
                                    port=3306)
                statusCode = 200
            except pymysql.MySQLError as e:
                logger.error(
                    "ERROR: Unexpected error: Could not connect to MySQL instance.")
                logger.error(e)
                statusCode = 505
                continueProgram = False
            logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
        if continueProgram == True:
            try:
                with cnx.cursor() as cur:
                    cur.execute("create table if not exists thread ( id int NOT NULL AUTO_INCREMENT, title varchar(255) NOT NULL, body varchar(255) NOT NULL, PRIMARY KEY (id))")
                    cnx.commit()
                    cur.execute('select * from thread limit 100')
                    return_body = [{"id": thread_id, "title": title, "body": body}
                                for thread_id, title, body in cur]
            except Exception as e:
                logger.error('Fatal exception occurred.', exc_info=e)
                statusCode = 500
                return_body = []
                continueProgram = False
        return {
            "statusCode": statusCode,
            "headers": { 
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,GET"
            },
            "body": return_body
        }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
