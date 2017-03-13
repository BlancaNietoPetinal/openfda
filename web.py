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
        if self.path == '/':
            html=self.get_main_page()
            self.wfile.write(bytes(html, "utf8"))
        elif '/search' in self.path:
            print (self.path)
            if 'DRUG' in self.path:
                drug=self.search_path()[1].split("=")
                com_html=self.html_companies()
                self.get_drug_event()
                self.wfile.write(bytes(com_html, "utf8"))
            elif 'COMPANY' in self.path:
                com_html=self.html_search_companies()
                self.get_drugs_from_company()
                self.wfile.write(bytes(com_html, "utf8"))
            else:
                html=self.get_main_page()
                self.wfile.write(bytes(html, "utf8"))
        elif self.path == '/receive':
            ev_html=self.event_html()
            self.wfile.write(bytes(ev_html, "utf8"))
        else:
            self.wfile.write(bytes("No","utf8"))
        return
    def get_drug(self):
        drug=[]
        event=json.loads(self.get_events())
        result=event["results"]
        for event1 in result:
            drug+= [event1["patient"]["drug"][0]["medicinalproduct"]]
        return drug

    def search_path(self):
        print (self.path.split("?"))
        return self.path.split("?")
    def get_company_event(self):
        event=''
        connection = http.client.HTTPSConnection(self.OPENFDA_API_URL) #asi indicamos que es parte de tu clase
        connection.request("GET",self.OPENFDA_API_EVENT+'?search=companynumb:'+self.search_path()[1].split("=")[1]+'&limit=10')
        print("///////////////////")
        print (self.search_path()[1].split("=")[1])
        r1 = connection.getresponse()
        data1 = r1.read() #te devuelve la informacion en bytes
        data1 = data1.decode("utf8") #para pasar de bytes a string
        event=data1
        print (event)
        return event
    def get_drug_event(self):
        event=''
        connection = http.client.HTTPSConnection(self.OPENFDA_API_URL) #asi indicamos que es parte de tu clase
        connection.request("GET",self.OPENFDA_API_EVENT+'?limit=10&search=patient.drug.medicinalproduct:"'+self.search_path()[1]+'"')
        r1 = connection.getresponse()
        data1 = r1.read() #te devuelve la informacion en bytes
        data1 = data1.decode("utf8") #para pasar de bytes a string
        event=data1
        return event
    def get_drugs_from_company(self):
        drug=[]
        event=json.loads(self.get_company_event())
        result=event["results"]
        for event1 in result:
            drug += [event1["patient"]["drug"][0]["medicinalproduct"]]
        print (drug)
        return drug

    def get_companies(self):
        drug=[]
        event=json.loads(self.get_drug_event())
        result=event["results"]
        for event1 in result:
            drug+= [event1["companynumb"]]
        return drug

    def html_companies(self):
        items=self.get_companies()
        html='''
        <html>
        <head></head>
        <body>
            <ul>
        '''
        for commpany in items:
            html+="<li>"+commpany+"</li>"
        html+='''
            </ul>
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
                <form method="get" action="receive">
                    <input type="submit" value="Ask for drugs">
                    </input>
                </form>
                <form method="get" action="search">
                    <input type="text" name='DRUG'></input>
                    <input type="submit" value="Ask for companies"></input>
                </form>
                <form method="get" action="search">
                    <input type="text" name='COMPANY'></input>
                    <input type="submit" value="Ask for drugs"></input>
                </form>
            </body>
        </html>
        '''
        return html

    def event_html(self):
        items=self.get_drug()
        html='''
        <html>
        <head></head>
        <body>
            <ul>
        '''
        for drug in items:
            html+="<li>"+drug+"</li>"
        html+='''
            </ul>
        </body>
        </html>
        '''
        return html
    def html_search_companies(self):
        items=self.get_drugs_from_company()
        html='''
        <html>
        <head></head>
        <body>
            <ul>
        '''
        for commpany in items:
            html+="<li>"+commpany+"</li>"
        html+='''
            </ul>
        </body>
        </html>
        '''
        return html

    def get_events(self):
        event=''
        connection = http.client.HTTPSConnection(self.OPENFDA_API_URL) #asi indicamos que es parte de tu clase
        connection.request("GET",self.OPENFDA_API_EVENT+"?limit=10") #PARA CAMBIAR EL EVENTO CAMBIAMOS EL NUMERO DESPUES DEL =
        r1 = connection.getresponse()
        data1 = r1.read() #te devuelve la informacion en bytes
        data1 = data1.decode("utf8") #para pasar de bytes a string
        event=data1
        return event
    def do_GET(self):
        self.send_response(200)
        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.send_smg()
        return

#para devolver el diccionario lo pasamos a str con ",".join(a)
