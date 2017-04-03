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
    OPENFDA_API_URL="api.fda.gov"
    OPENFDA_API_EVENT="/drug/event.json"
    def send_smg(self):
        limit=self.path.split('=')[-1]
        html=''
        if self.path == '/':
            html=self.get_main_page()
        elif self.path.startswith('/listDrugs'):
            QUERY=self.OPENFDA_API_EVENT+"?limit="+limit
            event=self.get_events(QUERY)
            items=self.get_items(event)
            html=self.event_html(items)
        elif self.path.startswith('/listCompanies'):
            QUERY=self.OPENFDA_API_EVENT+"?limit="+limit
            event=self.get_events(QUERY)
            items=self.get_companies(event)
            html=self.event_html(items)
        elif 'Gender' in self.path:
            QUERY=self.OPENFDA_API_EVENT+"?limit="+limit
            event=self.get_events(QUERY)
            genders=self.get_gender(event)
            html=self.event_html(genders)
        elif '/search' in self.path:
            item_searched = self.path.split("=")[1].split('&')[0]
            if 'drug' in self.path:
                QUERY=self.OPENFDA_API_EVENT+'?search=patient.drug.medicinalproduct:'+item_searched+'&limit='+limit
                event=self.get_events(QUERY)
                if self.path.split("=")[1].split('&')[0] in event:
                    items=self.get_companies(event)
                    html=self.event_html(items)
                else:
                    html=''
            elif 'company' in self.path:
                QUERY=self.OPENFDA_API_EVENT+'?search=companynumb:'+item_searched+'&limit='+limit
                event=self.get_events(QUERY)
                if self.search_path()[1].split('&')[0] in event:
                    items=self.get_companies(event)
                    html=self.event_html(items)
                else:
                    html=''
        return (html)

    def get_events(self,QUERY):
        event=''
        connection = http.client.HTTPSConnection(self.OPENFDA_API_URL) #asi indicamos que es parte de tu clase
        connection.request("GET",QUERY) #PARA CAMBIAR EL EVENTO CAMBIAMOS EL NUMERO DESPUES DEL =
        r1 = connection.getresponse()
        data1 = r1.read() #te devuelve la informacion en bytes
        data1 = data1.decode("utf8") #para pasar de bytes a string
        event=data1
        return event

    def get_items(self,event):
        drug=[]
        eventstr=json.loads(event)
        result=eventstr["results"]
        for i in result:
            drug += [i["patient"]["drug"][0]["medicinalproduct"]]
        return drug

    def get_companies(self,event):
        drug=[]
        eventstr=json.loads(event)
        result=eventstr["results"]
        for i in result:
            drug+=[i["companynumb"]]
        return drug

    def get_gender(self,event):
        genders=[]
        eventstr=json.loads(event)
        result=eventstr["results"]
        for gender in result:
            genders+=[gender["patient"]["patientsex"]]
        return genders

    def search_path(self):
        return (self.path.split("="))

    def in_event(self,event):
        return (self.search_path()[1] in event)

    def do_GET(self):
        html=self.send_smg()
        if html=='':
            self.send_response(404)
            html=self.html_error404()
        else:
            self.send_response(200)
        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes(html, "utf8"))
        return

#-----------------HTML--------------------
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
                    <input type="submit" value="List Drugs"></input>
                    <input type="submit" value='Limit:'></input>
                    <input type="text" name='limit'></input>
                </form>
                <form method="get" action="listCompanies">
                    <input type="submit" value="List Companies"></input>
                    <input type="submit" value="Limit:"></input>
                    <input type="text" name="limit"></input>
                </form>
                <form method="get" action="listGender">
                    <input type="submit" value="Search Gender"></input>
                    <input type="submit" value="Limit:"></input>
                    <input type="text" name="limit"></input>
                </form>
                <form method="get" action="searchDrug">
                    <input type="text" name="drug"></input>
                    <input type="submit" value="Ask for Companies"></input>
                    <input type="submit" value="Limit:"></input>
                    <input type="text" name="limit"></input>
                </form>
                <form method="get" action="searchCompany">
                    <input type="text" name="company"></input>
                    <input type="submit" value="Ask for drugs"></input>
                    <input type="submit" value="Limit:"></input>
                    <input type="text" name="limit"></input>
                </form>
            </body>
        </html>
        '''
        return html
    def html_error404(self):
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

#cabeceras: -curl -v -s
#para devolver el diccionario lo pasamos a str con ",".join(a)
