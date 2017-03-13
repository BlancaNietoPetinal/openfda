#Este archivo utiliza las bibliotecas de Cliente-Servidor
import socketserver
import web
PORT = 903
#Handler = http.server.SimpleHTTPRequestHandler es una clase que me permite crear un server directamente

Handler = web.testHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()

#handler: clase que gestiona las peticiones
