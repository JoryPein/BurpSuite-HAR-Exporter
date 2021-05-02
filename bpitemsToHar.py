import xml.etree.cElementTree as ET
from base64 import b64encode, b64decode
import json
import time
from datetime import datetime
import traceback
import sys


def transBsToHarTime(bs_timeformat):
    # translate burpsuite items time format that likes 'Sun May 02 11:38:56 CST 2021' to 
    # HAR time format like '2021-05-02T11:38:56.000Z'
    timestamp = time.mktime(time.strptime(bs_timeformat, "%a %b %d %X CST %Y"))
    return datetime.fromtimestamp(timestamp).isoformat(timespec='milliseconds')+'Z'

def get_now_format_time():
    return datetime.fromtimestamp(time.time()).isoformat(timespec='milliseconds')+'Z'

def getHeaderDict(headers_text):
    headers_dict = []
    for headers_item in headers_text:
        header_item = headers_item.split(b': ')
        headers_dict.append({
            'name': header_item[0].decode('utf-8'),
            'value': header_item[1].decode('utf-8'),
        })
    return headers_dict

def getRequestDict(item):
    dic_request = {
        'method':'',
        'url': '',
        'httpVersion': '',
        'headers': [],
        'queryString': [],
        'cookies': [],
        'headersSize': 0,
        'bodySize': 0
    }
    try:
        request = b64decode(item.find('request').text)
        headers_items, body = request.split(b'\r\n\r\n', 1)
        headers_items_split = headers_items.split(b'\r\n')
        method, url, version = headers_items_split[0].split(b' ', 2)
        headers_text = headers_items_split[1:]
        dic_request['method'] = method.decode()
        dic_request['url'] = item.find('url').text
        dic_request['httpVersion'] = version.decode()
        dic_request['headers'] = getHeaderDict(headers_text)
        dic_request['headersSize'] = len(headers_items)+4
        dic_request['bodySize'] = len(body)
    except:
        traceback.print_exc()
    return dic_request

def translage_mimetype(name):
    return {
        'json': 'application/json',
        'js': 'application/javascript',
        'css': 'text/css',
        'html': 'text/html',
        'icon': 'image/x-icon',
        'png': 'image/png',
        'gif': 'image/gif',
        'jpg': 'image/jpeg'
    }.get(name)

def makeResponseContent(item, body, content_type):
    responseContent = dict()
    responseContent['size'] = len(body)
    responseContent['compression'] = 0

    mimetype = item.find('mimetype').text
    extension = item.find('extension').text

    plains = ['application/json', 'application/javascript', 'application/x-javascript', 'text/css', 'text/html']
    binaries = ['image/x-icon', 'image/png', 'image/gif', 'image/jpeg']

    type_flag = None

    if content_type in plains:
        type_flag = 'plain'
        responseContent['mimeType'] = content_type
    elif content_type in binaries:
        type_flag = 'binary'
        responseContent['mimeType'] = content_type
    elif extension in ['js', 'css']:
        type_flag = 'plain'
        responseContent['mimeType'] = translage_mimetype(extension)
    elif extension in ['png', 'gif', 'jpg']:
        type_flag = 'binary'
        responseContent['mimeType'] = translage_mimetype(extension)
    else:
        type_flag = None
        responseContent['mimeType'] = 'x-unknown'
        # print(b64decode(item.find('response').text.encode()))

    if type_flag == 'plain':
        responseContent['text'] = body.decode('utf-8')
    elif type_flag == 'binary':
        responseContent['text'] = b64encode(body).decode('utf-8')
        responseContent['encoding'] = 'base64'
    else:
        pass

    return responseContent

def getDictValueByKey(dict_, key):
    for item in dict_:
        if item['name'] == key:
            return item['value'].split(';',1)[0]
    return None

def make_dic_response(dic_response, response_text, item):
    response = b64decode(response_text)
    headers_items, body = response.split(b'\r\n\r\n', 1)
    headers_items_split = headers_items.split(b'\r\n')
    httpVersion, status, statusText = headers_items_split[0].split(b' ', 2)
    headers_text = headers_items_split[1:]
    dic_response['httpVersion'] = httpVersion.decode('utf-8')
    dic_response['status'] = int(status.decode('utf-8'))
    dic_response['statusText'] = statusText.decode('utf-8')
    header_dict = getHeaderDict(headers_text)
    dic_response['headers'] = header_dict
    content = makeResponseContent(item, body, getDictValueByKey(header_dict, 'Content-Type'))
    dic_response['content'] = content
    dic_response['headersSize'] = len(headers_items)+4
    dic_response['bodySize'] = len(body)
    return dic_response


def getResponseDict(item):
    dic_response = {
        'status': 0,
        'statusText': '',
        'httpVersion': '',
        'headers': [],
        'cookies': [],
        'content': {},
        'redirectURL': '',
        'headersSize': 0,
        'bodySize': 0,
        "_transferSize": 0,
        "_error": None
    }
    try:
        response_text = item.find('response').text
        if isinstance(response_text, str):
            dic_response = make_dic_response(dic_response, response_text, item)
        else:
            response_text = b64encode(b'HTTP/1.1 400 \r\nContent-Length: 0\r\nConnection: close\r\n\r\n')
            dic_response = make_dic_response(dic_response, response_text, item)
    except:
        traceback.print_exc()
    return dic_response

def get_resource_type(extension):
    if extension in ['js']:
        return 'script'
    elif extension in ['css']:
        return 'stylesheet'
    elif extension in ['ico', 'png', 'jpg','gif']:
        return 'image'
    else:
        return 'document'

def generate_har(xml_path, result_path, title=''):
    tree = ET.parse(xml_path)
    entries = []
    for item in list(tree.getroot().iter('item')):
        try:
            entry = {
                '_initiator': {
                    'type': 'other'
                },
                '_priority': 'VeryHigh',
                '_resourceType': get_resource_type(item.find('extension').text),
                'cache': {},
                'connection': '6442',
                'pageref': 'page_1',
                'request': getRequestDict(item),
                'response': getResponseDict(item),
                'serverIPAddress': item.find('host').attrib.get('ip', None),
                'startedDateTime': transBsToHarTime(item.find('time').text),
                'time': 1560.849000000031,
                'timings': {
                    "blocked": 19.2170000002833,
                    "dns": 0.927999999999999,
                    "ssl": 226.468,
                    "connect": 429.833,
                    "send": 1.9359999999999786,
                    "wait": 851.9689999998276,
                    "receive": 256.9659999999203,
                    "_blocked_queueing": 6.462000000283297
                }
            }
            entries.append(entry)
        except:
            traceback.print_exc()
    data = {
        'log': {
            'version': '1.2',
            'creator': {
                'name': 'WebInspector',
                'version': '537.36'
            },
            'pages': [
                {
                    'startedDateTime': get_now_format_time(),
                    'id': 'page_2',
                    'title': title,
                    'pageTimings': {
                        'onContentLoad': 1511.0180000010587,
                        'onLoad': 1507.1220000008907
                    }
                }
            ],
            'entries': entries
        }
    }
    with open(result_path,'w',encoding='utf-8') as fp:
        json.dump(data, fp, indent=2, ensure_ascii=False)


def main():
	if len(sys.argv) == 3:
	    xml_path = sys.argv[1]
	    result_path = sys.argv[2]
	    generate_har(xml_path, result_path)
	else:
		print(f'Arguments error!!!\nPlease use this program like {sys.argv[0]} "items.xml" "result.har".')

if __name__ == '__main__':
    main()
