from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

### Import CRUD operations ###

from database_setup import Base, Category, Item
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

### Connect to database ###

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/categories/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>Create new category</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/categories/new'>"
                output += "<input name='newCategory' type='text' placeholder='New category.'>"
                output += "<input type='submit' value='Create'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
            if self.path.endswith("/edit"):
                categoryId = self.path.split("/")[2]
                myCategoryData = session.query(Category).filter_by(id = categoryId).one()
                if myCategoryData !=[] :
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    output = ""
                    output += "<html><body>"
                    output += "<h1>"
                    output += myCategoryData.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/categories/%s/edit'>" % categoryId
                    output += "<input name='newCategoryName' type='text' placeholder = '%s'>" % myCategoryData.name
                    output += "<input type='submit' value='Rename'></form>"
                    output += "</body></html>"
                    self.wfile.write(output)
                    print output
                return
            if self.path.endswith("/delete"):
                categoryId = self.path.split("/")[2]
                myCategoryData = session.query(Category).filter_by(id = categoryId).one()
                if myCategoryData != [] :
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>"
                    output += myCategoryData.name
                    output += "</h1>"
                    output += "Are you sure you want to delete?"
                    output += "<form method='POST' enctype='multipart/form-data' action='/categories/%s/delete'>" % categoryId
                    output += "<input type='submit' value='Delete'></form>"
                    output += "</body></html>"
                    self.wfile.write(output)
                    print output
            
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "Hello!"
      
                output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message' type='text'><input type='submit' value='Submit'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "&#161Hola <a href='/hello'>Back to Hello page</a>"
                output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message' type='text'><input type='submit' value='Submit'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
            if self.path.endswith("/categories"):
                categories = session.query(Category).all()
                output = ""
                output += "<a href='/categories/new'>Add new category here</a></br></br>"
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output += "<html><body>"

                for category in categories:
                    output += category.name
                    output += "</br>"
                    output += "<a href='/categories/%s/edit'>Edit</a>" % category.id
                    output += "</br>"
                    output += "<a href='/categories/%s/delete'>Delete</a>" % category.id
                    output += "</br></br>"
              
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newCategoryName')
                categoryId = self.path.split("/")[2]
                myCategoryData = session.query(Category).filter_by(id = categoryId).one()

                if myCategoryData != []:
                    myCategoryData.name = messagecontent[0]
                    session.add(myCategoryData)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/categories')
                    self.end_headers()

                return
            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                categoryId = self.path.split("/")[2]
                myCategoryData = session.query(Category).filter_by(id = categoryId).one()
                if myCategoryData != []:
 
                    session.delete(myCategoryData)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/categories')
                    self.end_headers()
                
            if self.path.endswith("/categories/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newCategory')

                ### Create new category ###

                newCategory = Category(name = messagecontent[0])
                session.add(newCategory)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/categories')
                self.end_headers()

                return
                    
                
                
##            self.send_response(301)
##            self.end_headers()
##
##            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
##            if ctype == 'multipart/form-data':
##                fields=cgi.parse_multipart(self.rfile, pdict)
##                messagecontent = fields.get('message')
##
##            output = ""
##            output += "<html><body>"
##            output += "<h2> Okay, how about this: </h2>"
##            output += "<h1> %s </h1>" % messagecontent[0]
##
##            output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message' type='text'><input type='submit' value='Submit'></form>"
##            output += "</body></html>"
##            self.wfile.write(output)
##            print output
        except:
            pass
            

    
        
def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()
        

if __name__ == '__main__':
    main()
