# using http.server library
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# load and parse json file of usernames/passwords
f = open("users.json")
users = json.load(f)

routes = {
    "/": open("index.html").read(),
    "/welcome": "Hello World!",
    "/about": "copyright reserved by Blade",
    "/index": open("index.html").read(),
    "/login": open("login.html").read(),
    "/accept": open("user_home.html").read(),
    "/register": open("register.html").read(),
    "/app": open("app.html").read(),
}

# global variables for error handling
error = False
error_message = ""

# handles GET and POST HTTP requests to server
class TestServer(BaseHTTPRequestHandler):

    # server is waiting to receive HTTP requests
    # when method GET is received in HTTP request line, this response will be sent
    def do_GET(self):
        global error
        global error_message
        # error checking for path routes
        #print(self.request)
        #print(self.path.split('?')[0])
        #print(self.parse_request)

        # making sure error message is cleared
        if error:
            error = False
        else:
            error_message = ""

        # if route is normal path, redirect to that route
        for route in routes:
            if route == self.path or (self.path.startswith(route) and route != '/'):
                self.send_response(200) # OK
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes(routes[route].replace("###ERROR###", error_message), "UTF-8"))
                break
        # if route is api, load dynamic json content
        if self.path.startswith("/api/"):
            # load login form to page if login button clicked
            if self.path.endswith("/login"):
                self.send_response(200)
                self.send_header("content-type", "application/json")
                self.end_headers()
                result = {
                    "status": 200,
                    "html": open("login-form.html").read()
                }
                self.wfile.write(bytes(json.dumps(result), "UTF-8"))

            # load register form to page if signup button clicked 
            if self.path.endswith("/register"):
                self.send_response(200)
                self.send_header("content-type", "application/json")
                self.end_headers()
                result = {
                    "status": 200,
                    "html": open("register-form.html").read()
                }
                self.wfile.write(bytes(json.dumps(result), "UTF-8"))


        #if self.path in routes:
            #self.send_response(200) # message = OK
            #self.send_header("Content-type", "text/html")
            #self.end_headers()
            #self.wfile.write(bytes(routes[self.path.split('?')[0]].replace("###ERROR###", error_message), "UTF-8"))
        #else: 
            #self.send_response(404) # message = Page Not Found
            #self.send_header("Content-type", "text/html")
            #self.end_headers()
            #self.wfile.write(bytes("Page Not Found", "UTF-8"))

    # when method POST is received in HTTP request line, this response will be sent
    # POST used for login form (for confidentiality and security)
    def do_POST(self):
        global error
        global error_message
        
        # reading form data and splitting into key/value pairs for username and password 
        # first converting to string object to perform string manipulation
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("UTF-8")
        #print(post_data)
        pairs = post_data.split('&')
        form = {}
        for pair in pairs:
            kvp = pair.split('=')
            form[kvp[0]] = kvp[1]
        #print(form)

        # compare form data with json data to validate (or reject) user login
        match = False
        found_user = False
        for key in users:
            user = users[key]
            if form["username"] == user["username"]:
                found_user = True
            if form["username"] == user["username"] and form["password"] == user["password"]:
                match = True
                break

        if self.path == "/accept":
            if match:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes(routes[self.path].replace("###USER###", user["username"]), "UTF-8"))
            else: # error message and redirect back to login
                error = True
                error_message = "Invalid user login."
                self.send_response(301) # message = Move Permanently (redirect)
                self.send_header('Location', '/login')
                self.end_headers()
                #self.wfile.write(bytes(routes[self.path.split('?')[0]].replace("###", "Incorrect user login."), "UTF-8"))
                #self.wfile.write(bytes("Invalid user login.", "UTF-8"))

            #self.wfile.write(bytes(routes[self.path.split('?')[0]], "UTF-8"))
                
        elif self.path == "/register":
            # 3 cases...
            # reject submission if username is already used
            if found_user:
                error = True
                error_message = "Username is already in the system."
                self.send_response(301)
                self.send_header('Location', '/register')
                self.end_headers()
            # reject submission if passwords don't match
            elif form["password"] != form["password2"]:
                error = True
                error_message = "Passwords do not match."
                self.send_response(301)
                self.send_header('Location', '/register')
                self.end_headers()
            # otherwise create new user and redirect to home page 
            else:
                error = False
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                # create new json object for new user
                users[str(len(users))] = {
                    "username": form["username"],
                    "password": form["password"]
                }
                # write new user to json file
                with open("users.json", "w") as outfile:
                    json.dump(users, outfile)
                self.wfile.write(bytes(routes["/accept"].replace("###USER###", form["username"]), "UTF-8"))

        elif self.path == "/api/login":
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            if found_user:
                result = {
                    "answer": 200,
                    "username": form["username"]
                }
                self.wfile.write(bytes(json.dumps(result), "UTF-8"))
            else:
                result = {
                    "answer": 400,
                    "error-message": "Incorrect username and password."
                }
                self.wfile.write(bytes(json.dumps(result), "UTF-8"))

        elif self.path == "/api/register":
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            if found_user:
                result = {
                    "answer": 400,
                    "error-message": "Username is already in the system."
                }
                self.wfile.write(bytes(json.dumps(result), "UTF-8"))
            elif form["password"] != form["password2"]:
                result = {
                    "answer": 400,
                    "error-message": "Passwords do not match."
                }
                self.wfile.write(bytes(json.dumps(result), "UTF-8"))
            else:
                users[str(len(users))] = {
                    "username": form["username"],
                    "password": form["password"]
                }
                with open("users.json", "w") as outfile:
                    json.dump(users, outfile)
                result = {
                    "answer": 200,
                    "username": form["username"]
                }
                self.wfile.write(bytes(json.dumps(result), "UTF-8"))

        #if self.path in routes:
        #else: 
            #self.send_response(404)
            #self.send_header("Content-type", "text/html")
            #self.end_headers()
            #self.wfile.write(bytes("Page Not Found", "UTF-8"))
        

# functions as Python "run method"
if __name__ == "__main__":
    webServer = HTTPServer(("localhost", 9090), TestServer)
    print("Server started http://%s:%s" % ("localhost", "9090"))
    
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    
    webServer.server_close()
    print("Server stopped.")