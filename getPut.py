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
        db_name = "webforum"
        db_port = 3306
        db_user = 'admin'
        db_host = 'vd1qir7pjuw93jl.cusyzimfrxgh.us-east-1.rds.amazonaws.com'
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        secretsclient = boto3.client('secretsmanager')
        response = secretsclient.get_secret_value(SecretId='web-forum-database-saunders')
        db_secrets = json.loads(response['SecretString'])
        db_password = db_secrets['password']
        print(request.form)
        print(request.get_json())
        print(request.form.to_dict())
        print(request)
        print(request.on_json_loading_failed())
        print(request.get_data())
        print(request.headers)
        print(request.json)
        print(request.values)
        try:
            conn = pymysql.connect(
                user=db_user, password=db_password, host=db_host,
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
                print('enter json load try block')
                body = json.loads(request.form['params']['body'])
                title = json.loads(request.form['params']['title'])
                print(title, body)
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO thread (title, body) VALUES (%s, %s)", (title, body))
                conn.commit()
                statusCode = 200
            except Exception as e:
                logger.error('Fatal exception occurred.', exc_info=e)
                statusCode = 500
        elif:
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


@app.route('/health', methods=['GET'])
def apiHealth():
    if request.method == 'GET':
        return '200'


@app.route('/saved', methods=['GET'])
def apiGet():
    if request.method == 'GET':
        statusCode = 200
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        db_host = 'vd1qir7pjuw93jl.cusyzimfrxgh.us-east-1.rds.amazonaws.com'
        db_user = 'admin'
        secretsclient = boto3.client('secretsmanager')
        response = secretsclient.get_secret_value(SecretId='web-forum-database-saunders')
        db_secrets = json.loads(response['SecretString'])
        db_password = db_secrets['password']
        if statusCode == 200:
            try:
                cnx = pymysql.connect(user=db_user,
                                    password=db_password,
                                    host=db_host,
                                    database='webforum',
                                    port=3306)
            except pymysql.MySQLError as e:
                logger.error(
                    "ERROR: Unexpected error: Could not connect to MySQL instance.")
                logger.error(e)
                statusCode = 505
            logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
        if statusCode == 200:
            try:
                with cnx.cursor() as cur:
                    cur.execute("create table if not exists thread ( id int NOT NULL AUTO_INCREMENT, title varchar(255) NOT NULL, body varchar(255) NOT NULL, PRIMARY KEY (id))")
                    cur.execute('select * from thread limit 100')
                    return_body = [{'id': thread_id, 'title': title, 'body': body}
                                for thread_id, title, body in cur]
                statusCode = 200
            except Exception as e:
                logger.error('Fatal exception occurred.', exc_info=e)
                statusCode = 500
                return_body = []
        return {
            "statusCode": statusCode,
            "headers": { 
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,GET"
            },
            "body": json.dumps(return_body)
        }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
