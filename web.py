#Copyright [2017] [Blanca Nieto Petinal]

#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import http.client
import http.server
import json

#el codigo ejecutable va lo ultimo
# HTTPRequestHandler class
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def send_html(self):
        path=self.path
        html=''
        items=[]
        event=OpenFDAClient().get_events(path)
        if path == '/':
            html=OpenFDAhtml().get_main_page()

        elif '/listDrugs' in self.path:
            drugs=OpenFDAParser().get_items(event)
            html=OpenFDAhtml().event_html(drugs)

        elif '/listCompanies' in self.path:
            companies=OpenFDAParser().get_companies(event)
            html=OpenFDAhtml().event_html(companies)

        elif '/listGender' in self.path:
            gender=OpenFDAParser().get_gender(event)
            html=OpenFDAhtml().event_html(gender)

        elif '/search' in self.path:
            if 'Company' in path:
                items=OpenFDAParser().get_items(event)
            else:
                items=OpenFDAParser().get_companies(event)
            if items==-1:
                html=''
            else:
                html=OpenFDAhtml().event_html(items)
        return (html)

    def do_GET(self):
        html=self.send_html()

        if self.path=='/secret':
            self.send_response(401)
            self.send_header('WWW-Authenticate ','Basic realm=\"Test\"')

        elif self.path=='/redirect':
            self.send_response(302)
            self.send_header('Location', 'http://localhost:8000/')

        elif html=='':
            self.send_response(404)
            self.send_header('Content-type','text/html')
            html=OpenFDAhtml.html_error404()

        else:
            self.send_response(200)
            self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes(html, "utf8"))
        return

class OpenFDAParser():
    def get_gender(self,event):
        genders=[]
        eventstr=json.loads(event)
        result=eventstr["results"]
        for gender in result:
            genders+=[gender["patient"]["patientsex"]]
        return genders

    def get_items(self,event):
        drugs=[]
        try:
            eventstr=json.loads(event)
            result=eventstr["results"]
            for i in result:
                drugs += [i["patient"]["drug"][0]["medicinalproduct"]]
        except KeyError:
            drugs=-1
        return drugs

    def get_companies(self,event):
        companies_list=[]
        try:
            companies_dicc=json.loads(event)
            result=companies_dicc["results"]
            for i in result:
                companies_list+=[i["companynumb"]]
        except KeyError:
            companies_list=-1
        return companies_list


class OpenFDAClient():
    OPENFDA_API_URL="api.fda.gov"
    OPENFDA_API_EVENT="/drug/event.json"

    def get_events(self,path):
        limit=''
        event=''
        QUERY=''
        connection = http.client.HTTPSConnection(self.OPENFDA_API_URL)
        if '/list' in path:
            limit=path.split('=')[-1]
            QUERY=self.OPENFDA_API_EVENT+"?limit="+limit
        elif '/searchDrug' in path:
            limit='10'
            item_searched = path.split("=")[1].split('&')[0]
            QUERY=self.OPENFDA_API_EVENT+'?search=patient.drug.medicinalproduct:'+item_searched+'&limit='+limit
        elif '/searchCompany' in path:
            limit='10'
            item_searched = path.split("=")[1].split('&')[0]
            QUERY=self.OPENFDA_API_EVENT+'?search=companynumb:'+item_searched+'&limit='+limit
        connection.request("GET",QUERY) 
        r1 = connection.getresponse()
        data1 = r1.read()
        data1 = data1.decode("utf8")
        event=data1
        return event

class OpenFDAhtml():
    def event_html(self,items):
        html='''
        <html>
        <head></head>
        <body>
            <ol>
        '''
        for item in items:
            html+="<li>"+item+"</li>"
        html+='''
            </ol>
        </body>
        </html>
        '''
        return html

    def get_main_page(self):
        html='''<html>
            <head>
                <title>OpenFDA Client</title>
            </head>
            <body>
                <h1>OpenFDA client</h1>
                <form method="get" action="listDrugs">
                    List Drugs: <input type="submit" value='Limit:'></input>
                    <input type="text" name='limit'></input>
                </form>
                <form method="get" action="listCompanies">
                    List Companies: <input type="submit" value="Limit:"></input>
                    <input type="text" name="limit"></input>
                </form>
                <form method="get" action="listGender">
                    List Gender: <input type="submit" value="Limit:"></input>
                    <input type="text" name="limit"></input>
                </form>
                <form method="get" action="searchDrug">
                    <input type="text" name="drug"></input>
                    <input type="submit" value="Ask for Companies"></input>
                </form>
                <form method="get" action="searchCompany">
                    <input type="text" name="company"></input>
                    <input type="submit" value="Ask for drugs"></input>
                </form>
            </body>
        </html>
        '''
        return html
    def html_error404():
        html='''
        <html>
            <head>
                <h1> Error 404 </h1>
            </head>
            <body>
            </body>
        </html>
        '''
        return html
