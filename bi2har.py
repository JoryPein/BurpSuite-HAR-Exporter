import xml.etree.cElementTree as ET
from base64 import b64encode, b64decode
from datetime import datetime
from urllib import parse
from http import cookies
import sys
import time
import json


class HarTimeFormat:

    @staticmethod
    def timestampToHarTime(timestamp):
        # '2021-05-02T11:38:56.000Z'
        return datetime.fromtimestamp(timestamp).isoformat(timespec='milliseconds')+'Z'

    def transBsToHarTime(self, bs_timeformat):
        # translate burpsuite http items time format likes 'Sun May 02 11:38:56 CST 2021' into 
        # HAR time format likes '2021-05-02T11:38:56.000Z'
        timestamp = time.mktime(time.strptime(bs_timeformat, "%a %b %d %X CST %Y"))
        return self.timestampToHarTime(timestamp)

    def getNowHarTime(self):
        return self.timestampToHarTime(time.time())


class HarLogStructure:

    def constructEntryRequest(self, request_method, request_url, request_httpVersion, 
            request_headers, request_queryString, request_cookies, 
            request_headersSize, request_bodySize):
        return {
            'method':request_method,
            'url': request_url,
            'httpVersion': request_httpVersion,
            'headers': request_headers,
            'queryString': request_queryString,
            'cookies': request_cookies,
            'headersSize': request_headersSize,
            'bodySize': request_bodySize
        }

    def constructEntryResponse(self, data_status, data_statusText, data_httpVersion, 
            data_headers, data_content, data_headersSize, data_bodySize):
        return {
            'status': data_status,
            'statusText': data_statusText,
            'httpVersion': data_httpVersion,
            'headers': data_headers,
            'cookies': [],
            'content': data_content,
            'redirectURL': '',
            'headersSize': data_headersSize,
            'bodySize': data_bodySize,
            "_transferSize": 0,
            "_error": None
        }

    def constructEntry(self, entry_resourceType, entry_request, entry_response, 
            entry_serverIPAddress, entry_startedDateTime):
        return {
            '_initiator': {
                'type': 'other'
            },
            '_priority': 'VeryHigh',
            '_resourceType': entry_resourceType,
            'cache': {},
            'connection': '6442',
            'pageref': 'page_2',
            'request': entry_request,
            'response': entry_response,
            'serverIPAddress': entry_serverIPAddress,
            'startedDateTime': entry_startedDateTime,
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

    def constructHarLog(self, pages_startedDateTime, pages_title, entries):
        return {
            'log': {
                'version': '1.2',
                'creator': {
                    'name': 'WebInspector',
                    'version': '537.36'
                },
                'pages': [
                    {
                        'startedDateTime': pages_startedDateTime,
                        'id': 'page_2',
                        'title': pages_title,
                        'pageTimings': {
                            'onContentLoad': 1511.0180000010587,
                            'onLoad': 1507.1220000008907
                        }
                    }
                ],
                'entries': entries
            }
        }


class HarLog(HarLogStructure):

    def __init__(self):
        super(HarLog, self).__init__()

        self.plains = [
            'application/json', 
            'application/javascript', 
            'application/x-javascript', 
            'text/css', 
            'text/html'
        ]
        self.binaries = [
            'image/x-icon', 
            'image/png', 
            'image/gif', 
            'image/jpeg'
        ]

        self.data_mimeType = {
            'json': 'application/json',
            'js': 'application/javascript',
            'css': 'text/css',
            'html': 'text/html',
            'icon': 'image/x-icon',
            'png': 'image/png',
            'gif': 'image/gif',
            'jpg': 'image/jpeg'
        }

    @staticmethod
    def getHeadersList(headers_text):
        headers_dict = []
        for headers_item in headers_text:
            header_item = headers_item.split(b': ')
            headers_dict.append({
                'name': header_item[0].decode('utf-8').lower(),
                'value': header_item[1].decode('utf-8'),
            })
        return headers_dict

    @staticmethod
    def getQueryList(url):
        query_list = []
        for item in parse.parse_qsl(parse.urlparse(url).query):
            query_list.append({'name':item[0],'value':parse.quote_plus(item[1])})
        return query_list

    @staticmethod
    def getCookiesList(cookiesText):
        simple_cookie = cookies.SimpleCookie()
        cookiesList = []
        simple_cookie.load(cookiesText)
        for name in simple_cookie:
            cookiesList.append({
                'name': name,
                'value': simple_cookie[name].value,
                'expires': None,
                'httpOnly': False,
                'secure': False
            })
        return cookiesList

    @staticmethod
    def getCookiesText(headers_list):
        cookiesText = ''
        for item in headers_list:
            if item['name'] == 'cookie':
                cookiesText = item['value']
        return cookiesText

    @staticmethod
    def getDictValueByKey(dict_, key):
        for item in dict_:
            if item['name'] == key:
                return item['value'].split(';',1)[0]
        return None

    @staticmethod
    def getResourceType(extension):
        if extension in ['js']:
            return 'script'
        elif extension in ['css']:
            return 'stylesheet'
        elif extension in ['ico', 'png', 'jpg','gif']:
            return 'image'
        else:
            return 'document'

    @staticmethod
    def saveJsonFile(filename, data):
        with open(filename, 'w', encoding='utf-8') as fp:
            json.dump(data, fp, indent=2, ensure_ascii=False)

    @staticmethod
    def readFile(filename):
        with open(filename, 'r', encoding='utf-8') as fp:
            text = fp.read()
        return text

    def getRequestDict(self, item_request, item_url):
        headers_items, body = b64decode(item_request).split(b'\r\n\r\n', 1)
        headers_items_split = headers_items.split(b'\r\n')
        method, _url, version = headers_items_split[0].split(b' ', 2)

        request_method      = method.decode('utf-8')
        request_url         = item_url
        request_httpVersion = version.decode('utf-8')
        request_headers     = self.getHeadersList(headers_items_split[1:])
        request_queryString = self.getQueryList(item_url)
        request_cookies     = self.getCookiesList(self.getCookiesText(request_headers))
        request_headersSize = len(headers_items) + 4
        request_bodySize    = len(body)

        return request_method, request_url, request_httpVersion, request_headers, request_queryString, request_cookies, request_headersSize, request_bodySize

    def makeResponseContent(self, body, content_type, item_extension):
        responseContent = dict()
        responseContent['size'] = len(body)
        responseContent['compression'] = 0

        type_flag = None

        if content_type in self.plains:
            type_flag = 'plain'
            responseContent['mimeType'] = content_type
        elif content_type in self.binaries:
            type_flag = 'binary'
            responseContent['mimeType'] = content_type
        elif item_extension in ['js', 'css']:
            type_flag = 'plain'
            responseContent['mimeType'] = self.data_mimeType.get(item_extension)
        elif item_extension in ['png', 'gif', 'jpg']:
            type_flag = 'binary'
            responseContent['mimeType'] = self.data_mimeType.get(item_extension)
        else:
            type_flag = None
            responseContent['mimeType'] = 'x-unknown'

        if type_flag == 'plain':
            responseContent['text'] = body.decode('utf-8')
        elif type_flag == 'binary':
            responseContent['text'] = b64encode(body).decode('utf-8')
            responseContent['encoding'] = 'base64'

        return responseContent

    def getResponseDict(self, item_response, item_extension):
        if not isinstance(item_response, str):
            item_response = b64encode(b'HTTP/1.1 400 \r\nContent-Length: 0\r\nConnection: close\r\n\r\n')

        headers_items, body             = b64decode(item_response).split(b'\r\n\r\n', 1)
        headers_items_split             = headers_items.split(b'\r\n')
        httpVersion, status, statusText = headers_items_split[0].split(b' ', 2)
        headers_text                    = headers_items_split[1:]

        data_httpVersion = httpVersion.decode('utf-8')
        data_status      = int(status.decode('utf-8'))
        data_statusText  = statusText.decode('utf-8')
        data_headers     = self.getHeadersList(headers_text)
        data_content     = self.makeResponseContent(body, self.getDictValueByKey(data_headers, 'content-type'), item_extension)
        data_headersSize = len(headers_items) + 4
        data_bodySize    = len(body)
        return data_status, data_statusText, data_httpVersion, data_headers, data_content, data_headersSize, data_bodySize

    def get_entries(self, xml_text):    
        root = ET.fromstring(xml_text)
        entries = []
        for item in root.iter('item'):
            item_extension = item.find('extension').text
            item_url       = item.find('url').text
            item_request   = item.find('request').text
            item_response  = item.find('response').text
            item_ip        = item.find('host').attrib.get('ip', None)
            item_time      = item.find('time').text

            entry_resourceType    = self.getResourceType(item_extension)
            entry_request         = self.constructEntryRequest(*self.getRequestDict(item_request, item_url))
            entry_response        = self.constructEntryResponse(*self.getResponseDict(item_response, item_extension))
            entry_serverIPAddress = item_ip
            entry_startedDateTime = HarTimeFormat().transBsToHarTime(item_time)

            entry = self.constructEntry(entry_resourceType, entry_request, entry_response, entry_serverIPAddress, entry_startedDateTime)
            entries.append(entry)
        return entries

    def getHarLog(self, xml_text):
        entries = self.get_entries(xml_text)
        pages_startedDateTime = HarTimeFormat().getNowHarTime()
        pages_title = HarTimeFormat().getNowHarTime()
        return self.constructHarLog(pages_startedDateTime, pages_title, entries)

    def generate_har(self, xml_path, result_path):
        xml_text = self.readFile(xml_path)
        har_log = self.getHarLog(xml_text)
        self.saveJsonFile(result_path, har_log)

def main():
    if len(sys.argv) == 3:
        xml_path = sys.argv[1]
        result_path = sys.argv[2]
        HarLog().generate_har(xml_path, result_path)
    elif len(sys.argv) == 2 and sys.argv[1] == '--help':
    	print(f'Please use this program like {sys.argv[0]} "in.xml" "out.har".')
    else:
        print(f'Arguments error!!!\nPlease use this program like {sys.argv[0]} "in.xml" "out.har".')

if __name__ == '__main__':
    main()
