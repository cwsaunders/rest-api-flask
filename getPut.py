import json
import pymysql
import os
import sys
import logging
import boto3
from flask import Flask, render_template, request # make sure to package this in

app = Flask(__name__)


@app.route('/', methods=['PUT', 'GET'])
def apiPut(event):
    if request.method == 'PUT':
        db_name = "webforum"
        db_port = 3306
        db_user = 'admin'
        db_host = 'vd1ju04cu0pert8.cusyzimfrxgh.us-east-1.rds.amazonaws.com'
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        ssm_client = boto3.client('ssm')
        response = ssm_client.get_parameter(
            Name='web-forum-database',
            WithDecryption=True
        )
        db_password = response['Parameter']['Value']


        try:
            conn = pymysql.connect(
                user=db_user, password=db_password, host=db_host,
                port=db_port, database=db_name)
        except pymysql.MySQLError as e:
            logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
            logger.error(e)
            sys.exit()
        logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
        """
        This function PUTs content to a MySQL RDS instance
        """
        try:
            body = json.loads(request.form['body'])
            title = json.loads(request.form['title'])
            with conn.cursor() as cur:
                cur.execute("INSERT INTO thread (title, body) VALUES (%s, %s)", (title, body))
            conn.commit()
            statusCode = 200
        except Exception as e:
            logger.error('Fatal exception occurred.', exc_info=e)
            statusCode = 500
        return {
            "statusCode": statusCode,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,PUT"
            }
        }
    elif request.method == 'GET':
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        ssm_client = boto3.client('ssm')
        response = ssm_client.get_parameter(
            Name='web-forum-database',
            WithDecryption=True
        )
        db_password = response['Parameter']['Value']
        try:
            cnx = pymysql.connect(user=os.environ['USER'],
                                password=db_password,
                                host=os.environ['HOST'],
                                database='webforum',
                                port=3306)
        except pymysql.MySQLError as e:
            logger.error(
                "ERROR: Unexpected error: Could not connect to MySQL instance.")
            logger.error(e)
            sys.exit()
        logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
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
    app.run()
