#!/usr/bin/env python
#
# Copyright 2013 Jay Kline <jay@slushpupie.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi
import csv
import json
import iso8601
from urllib2 import Request, urlopen, HTTPError, URLError, HTTPHandler, build_opener

class MainHandler(webapp2.RequestHandler):
    def get(self):
        allowed_args = ["start", "end", "duration", "find_previous", "limit", "interval_type", "interval"]
        base_url = "http://api.cosm.com/v2"
        cosm_key = ""
        feed = "95557"


        if self.request.get('datastream') <> "":
            stream = self.request.get('datastream')
        else:
            stream = 'CurrentTemperature'
        url = base_url + '/feeds/'+feed+'/datastreams/'+stream+'.csv?utm_source=appengine'
        for arg in allowed_args:
            if self.request.get(arg) <> "":
                url = url + '&' + arg + '=' + self.request.get(arg)
      
        data = []
        try: 
            opener = build_opener(HTTPHandler)
            request = Request(url)
            request.add_header('X-ApiKey',cosm_key)
            result = opener.open(request)
   
            if 200 == 200: 
                csvr = csv.reader(result.read().splitlines())
                for row in csvr:
                   L = []
                   L.append( int(iso8601.parse_date(row[0]).strftime("%s"))*1000 )
                   L.append( float(row[1]))
                   data.append(L) 
        except HTTPError as e:
           data.append(["HTTPError",e.code, e.read()])
        except URLError as e:
           data.append(["URLError",e.reason])
        except Exception as e:
           data.append(["Error",e.args])

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(data))

app = webapp2.WSGIApplication([
    ('/data', MainHandler)
], debug=True)
