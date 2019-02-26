#CS560 Programming Assignment 1
#server.py - an implementation of a web server using sockets
#Michael Price and Shan Lalani

import socket
import os
import sys

def create_dir_html(dir_name):
    #generates http response for a directory
    cwd = os.getcwd()
    if(dir_name[-1] != '/'):
        dir_name += '/'
    
    curr_path = dir_name.replace(cwd, '')
    f = "<html>\n<head>\n<title>Directory: "+curr_path+"</title>\n</head>\n<body>\n"
    f += "Directory of "+curr_path+"<br><br>\n"
    f += "<a href = \""+ "../" + "\">..</a><br>\n"
    for file in os.listdir(dir_name):
        filename = os.fsdecode(file)
        if (os.path.isdir(dir_name+'/'+filename)):
            print ("here")
            filename += '/'
        f += "<a href = \"" + filename+"\">"+filename+"</a><br>\n"
    f += "</body>\n</html>"
    return f.encode('utf-8')

HOST, PORT = '',6969

#prepare the socket and have it begin to listen
listen_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
listen_socket.bind((HOST,PORT))
listen_socket.listen(10)
print ('Serving piping hot HTTP on port %s' % PORT)

while True:
    #Take in each request, print it to show http request
    client_connection, client_address = listen_socket.accept()
    request = client_connection.recv(1024).decode('utf-8')
    print (request)
    print(request.split(' '))
    if (request):
        rqfile = request.split(' ')[1]
    
    if(rqfile == '/'): 
        #default to index.html if there is no path
        rqfile = '/index.html'
    #rqfile = sys.path[0]+rqfile
    try:
        #open file, then tell what kind of file you're reading
        if(rqfile == '/fileupload?'):
            #this happens when a file is uploaded, write file to server side uploads folder
            print('Time to write a file!')
        else:
            rqfile = sys.path[0]+rqfile
            print (rqfile)
            f = open(rqfile,'rb')
            http_response = f.read()
            f.close()
            header = 'HTTP/1.1 200 OK\n'
            #prepare mime type based on file, default to html
            if(rqfile.endswith('.jpg')):
                mime  = "image/jpg"
            elif(rqfile.endswith('.png')):
                mime = 'image/png'
            else:
                mime = "text/html"
            header += 'Content-Type: '+str(mime)+'\n\n'
    except IsADirectoryError:
        #create custom response for directory
        header = 'HTTP/1.1 200 OK\n\n'
        http_response = create_dir_html(rqfile)
    except Exception:
        #default to 404 for invalid requests
        header = 'HTTP/1.1 404 Not Found\n\n'
        http_response = '<html><body><center><h3>Error 404: File not found</h3><p>Go home user, you\'re drunk.</p></center></body></html>'.encode('utf-8')
 
    #combine header and http_response to send to the client
    response = header.encode('utf-8')
    response += http_response
    client_connection.send(response)
    client_connection.close()