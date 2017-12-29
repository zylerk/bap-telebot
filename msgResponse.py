# coding: utf-8

import os
import datetime
import MySQLdb

# These environment variables are configured in app.yaml.
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')

def connect_to_cloudsql():
    # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
    # will be set to 'Google App Engine/version'.
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at
        # /cloudsql/cloudsql-connection-name.
        cloudsql_unix_socket = os.path.join(
            '/cloudsql', CLOUDSQL_CONNECTION_NAME)

        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            passwd=CLOUDSQL_PASSWORD)

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        db = MySQLdb.connect(
            host='127.0.0.1', user=CLOUDSQL_USER, passwd=CLOUDSQL_PASSWORD)

    return db


def process_msg(text):
    if 'who' in text:
        return 1, u'I am Bitoin Trade Bot'

    elif 'time' in text or u'시간' in text:
        time_utc = datetime.datetime.now().replace(microsecond=0).isoformat(' ')
        time_seoul = datetime.datetime.now() + datetime.timedelta(hours=9)
        time_seoul = time_seoul.replace(microsecond=0).isoformat(' ')
        time_result = u'utc = {0} <p> seoul = {1}'.format(time_utc, time_seoul)
        return 1, time_result

    elif 'btc' in text:
        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute('SHOW VARIABLES')

        result = ''
        for r in cursor.fetchall():
            result = result + r

        return 1, result

    return -1, ''

