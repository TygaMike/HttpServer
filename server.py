#CS560 Programming Assignment 1
#server.py - an implementation of a web server using sockets
#Michael Price and Shan Lalani

import socket
import os
import sys


#generates http response for a directory
def create_dir_html(dir_name):
    cwd = os.getcwd()
    
	# Appends / to set as directory
	if(dir_name[-1] != '/'):
        dir_name += '/'
    
	# Remove the current working directory from
	# absolute path to get the relative path 
    curr_path = dir_name.replace(cwd, '')

	# Set HTML headers and link and set links for files 
	# and directories inside the directory
    f = "<html>\n<head>\n<title>Directory: "+curr_path+"</title>\n</head>\n<body>\n"
    f += "Directory of "+curr_path+"<br><br>\n"
    f += "<a href = \""+ "../" + "\">..</a><br>\n"
    for file in os.listdir(dir_name):
        filename = os.fsdecode(file)
        if (os.path.isdir(dir_name+'/'+filename)):
            filename += '/'
        f += "<a href = \"" + filename+"\">"+filename+"</a><br>\n"
    f += "</body>\n</html>"

	# return the response
    return f.encode('utf-8')

# Set Port
HOST, PORT = '',6969

# Start up socket and listen for connections
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind ((HOST, PORT))
    
    s.listen (10)
    print ('Serving piping hot HTTP on port %s' % PORT)
    
    while True:
		# Connect with client and receive data
        conn, addr = s.accept()
        data = conn.recv(1024)
        if not data:
            continue
        
		# Decode data 
        data = data.decode('utf-8')
        print(data)
        
		# Get requested file name
        data = data.split(' ')
        rqfile = data[1]
        
		# Seperate POST and GET requests
        if (data[0] == "POST"): 
            try:
                first = True
                while True:
                    conn.settimeout(1)
                    data = conn.recv(1024)
                    if not data:
                        break
                    
					# First set, receive header information
                    if (first):
						# Pull out fileName and boundry for data
						# Append fileData
                        data = data.strip().split(b'\r\n\r\n')
                        fileName = data[0].split(b'\r\n')[-2].decode('utf-8').split("\"")[-2]
                        boundry = data[0].decode('utf-8').split('\r\n')[0]
                        fileData = data[1]
                        first = False
                    else:
                        fileData += data

			# Once socket times out, set the file data
            except socket.timeout:
                boundry = ("\r\n" + boundry).encode('utf-8')
                fileData = fileData.split(boundry)[0]
				
				# Open and write the data to the file
                f = open("uploads/"+fileName, "wb")
                f.write(fileData)
                f.close()

				# Set the headers and return uploads folder
                header = 'HTTP/1.1 200 OK\n\n'
                http_response = create_dir_html(os.getcwd()+'/uploads')

        else:
			# Set index.html as base case
            if (rqfile == '/'):
                rqfile = '/index.html'

            try:
				# Check if directory or file is requested
                rqfile = sys.path[0] + rqfile
                if (os.path.isdir(rqfile)):
                    header = 'HTTP/1.1 200 OK\n\n'
                    http_response = create_dir_html(rqfile)
                
				else:
					# Read bytes from file and set response
                    f = open(rqfile,'rb')
                    http_response = f.read()
                    f.close()
                
					# Set header information based on the type of file
                    header = 'HTTP/1.1 200 OK\n'
                    if(rqfile.endswith('.jpg')):
                        mime  = "image/jpg"
                    elif(rqfile.endswith('.png')):
                        mime = 'image/png'
                    else:
                        mime = "text/html"
                    
                    header += 'Content-Type: '+str(mime)+'\n\n'
            
            except Exception:
                #default to 404 for invalid requests
                header = 'HTTP/1.1 404 Not Found\n\n'
                http_response = """<html><body><center><h3>Error 404: File not found</h3>
                <p>Go home user, you\'re drunk.</p></center></body></html>"""
                http_response = http_response.encode('utf-8')
    
		# Finishs up response and sends to the client
        response = header.encode('utf-8')
        response += http_response
        conn.send(response)
