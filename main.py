import pytz
import json

from wsgiref.simple_server import make_server
from datetime import datetime
from dateutil import parser
from pytz import UnknownTimeZoneError

SERVER_TIMEZONE = "ASIA/TOMSK"


def parse_datetime_with_timezone(date_str, tz_name):
    date_obj = parser.parse(date_str)
    server_tz = pytz.timezone(tz_name) if tz_name else pytz.timezone(SERVER_TIMEZONE)
    date_obj = date_obj.astimezone(server_tz)
    return date_obj


def application(environ, start_response):
    path = environ['PATH_INFO']
    method = environ['REQUEST_METHOD']

    if path == '/' and method == 'GET':
        server_tz = pytz.timezone(SERVER_TIMEZONE)
        current_time = datetime.now(server_tz)
        response_body = f"<html><body><h1>Current Time in {SERVER_TIMEZONE}</h1><p>{current_time.strftime('%Y-%m-%d %H:%M:%S')}</p></body></html>"
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [response_body.encode('utf-8')]
    elif path.startswith('/') and len(path) > 1 and method == 'GET':
        tz_name = path[1:]
        try:
            tz = pytz.timezone(tz_name)
            current_time = datetime.now(tz)
            response_body = f"<html><body><h1>Current Time in {tz_name}</h1><p>{current_time.strftime('%Y-%m-%d %H:%M:%S')}</p></body></html>"
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [response_body.encode('utf-8')]
        except UnknownTimeZoneError:
            response_body = "<html><body><h1>400 Bad Request</h1><p>Invalid timezone specified.</p></body></html>"
            start_response('400 Bad Request', [('Content-Type', 'text/html')])
            return [response_body.encode('utf-8')]
    elif path == '/api/v1/time' and method == 'POST':
        length = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(length) if length > 0 else b'{}'
        data = json.loads(request_body)

        tz_name = data.get('tz', SERVER_TIMEZONE) if 'tz' in data else SERVER_TIMEZONE
        tz = pytz.timezone(tz_name)

        current_time = datetime.now(tz)

        response_data = {
            'current_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'timezone': tz_name
        }
        response_body = json.dumps(response_data)

        start_response('200 OK', [('Content-Type', 'application/json')])
        return [response_body.encode('utf-8')]
    elif path == '/api/v1/date' and method == 'POST':
        length = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(length) if length > 0 else b'{}'
        data = json.loads(request_body)

        tz_name = data.get('tz', SERVER_TIMEZONE) if 'tz' in data else SERVER_TIMEZONE
        tz = pytz.timezone(tz_name)
        current_time = datetime.now(tz)

        response_data = {
            'current_date': current_time.strftime('%Y-%m-%d'),
            'timezone': tz_name
        }
        response_body = json.dumps(response_data)

        start_response('200 OK', [('Content-Type', 'application/json')])
        return [response_body.encode('utf-8')]
    elif path == '/api/v1/datediff' and method == 'POST':
        length = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(length)
        data = json.loads(request_body)

        start_data = data.get('start')
        end_data = data.get('end')

        start_date_str = start_data['date']
        start_tz = start_data.get('tz', SERVER_TIMEZONE)

        end_date_str = end_data['date']
        end_tz = end_data.get('tz', SERVER_TIMEZONE)

        start_date = parse_datetime_with_timezone(start_date_str, start_tz)
        end_date = parse_datetime_with_timezone(end_date_str, end_tz)

        time_diff = end_date - start_date

        response_data = {
            "diff": time_diff.total_seconds(),
        }

        response_body = json.dumps(response_data)
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [response_body.encode('utf-8')]
    else:
        response_body = "<html><body><h1>400 Bad Request</h1><p>Invalid endpoint or method.</p></body></html>"
        start_response('400 Bad Request', [('Content-Type', 'text/html')])
        return [response_body.encode('utf-8')]


if __name__ == "__main__":
    with make_server('', 8080, application) as server:
        print("Serving on port 8080...")
        server.serve_forever()
