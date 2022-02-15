#!/usr/bin/env python3

import argparse

import sys
import os.path
import itertools
import socket
from socket import socket as Socket

# A simple web server

# Issues:
# Ignores CRLF requirement
# Header must be < 1024 bytes
# ...
# probabaly loads more


def main():

        # Command line arguments. Use a port > 1024 by default so that we can run
        # without sudo, for use as a real server you need to use port 80.
        parser = argparse.ArgumentParser()
        parser.add_argument('--port', '-p', default=2080, type=int, help='Port to use')
        args = parser.parse_args()
        
        # Create the server socket (to handle tcp requests using ipv4), make sure
        # it is always closed by using with statement.
        with Socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

	      # The socket stays connected even after this script ends. So in order
	      # to allow the immediate reuse of the socket (so that we can kill and
	      # re-run the server while debugging) we set the following option. This
	      # is potentially dangerous in real code: in rare cases you may get junk
	      # data arriving at the socket.
	
                # Set socket options
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# Bind socket to port
                server_socket.bind(('', args.port ))

		# Have socket listen
                server_socket.listen(0)

                print("server ready")

                while True:
		
		    # Use the server socket as the connection socket and accept incoming requests
		    # This is like file IO and you need to open the server socket as the connection socket
                    with server_socket.accept()[0] as connection_socket:
			
	   		        # Save the request received from the connection and decode as ascii
                                data_str=connection_socket.recv(1024).decode('ascii')
                                
                                # Bad Request error message
                                errorMessage400 = "Request had bad syntax or was inherently impossible to be satisfied" 
                                errorMessage404 = "The server has not found anything matching the URL given"
                                
                                request = data_str
                                
                                
                                # Split the request by line 
                                requestStrings = data_str.split( "/r/n" )
                                
                                # Isolate the request line
                                requestLineString = requestStrings[ 0 ]
                                requestLine = requestLineString.split()
                                
                                # Check if the request line has the correct number of fields
                                if len( requestLine ) != 3:
                                
                                	# If not, print a 400 error message
                                	print( errorMessage400 )
                                	server_socket.close()
                                	exit()
                                	
                               	# Check if the request line has an invalid method or version
                                if checkRequestLine( requestLine ) == False:
                                	
                                	# If so, print a 400 error message
                                	print( errorMessage400 )
                                	server_socket.close()
                                	exit()
                                	
                                # Extract the different request line fields
                                method = requestLine[ 0 ]
                                url = requestLine[ 1 ]
                                version = requestLine[ 2 ]
                                
                                # Split the URL into the domain and extension
                                splitURL = urlSplitter( url )
                                domain = splitURL[ 0 ].split("//")[ 1 ]
                                extension = splitURL[ 1 ]
                                
                                print( "domain: " + domain )
                                print( "extension: " + extension )
                                
                                # Check if the extension is an invalid path
                                # if checkPathInvalid( url ):
                                	
                                	# If so, print a 404 error message
                                #	print( errorMessage404 )
                                #	server_socket.close()
                                #	exit()

				
                                	
                                # Read the html file that we want to read
                                # htmlFile = open( extension, 'r', encoding = 'utf-8' )
                                # htmlText = htmlFile.read()
                                
                                # reply=htmlText
                                
                                # Generate a reply by sending the request received to http_handle()
                                
                                # Use the connection socket to send the reply encoded as bytestream
                                
                                replyString=connectToServer( url, requestLineString, domain )
                                replyEncoded = bytearray( replyString, 'utf-8' )
                                
                                print("Finished connecting to origin server")

                                print("\n\nReceived request")
                                print("======================")
                                print(request.rstrip())
                                print("======================")
                                print("\n\nReplied with")
                                print("======================")
                                print(replyString)#.rstrip())
                                print("======================")
                                
                                
                                connection_socket.sendall( replyEncoded )                                
                                server_socket.close()

# End of Main Method

# 
# Functions GET http://example.com HTTP/1.1
#

def checkRequestLine( requestLine ):

	errorMessage501 = "Not Implemented"

	# Separate request line fields 
	method = requestLine[ 0 ]
	url = requestLine[ 1 ]
	version = requestLine[ 2 ]
	
	# Initialize values
	validMethodTypes = [ "GET", "POST", "HEAD", "PUT", "PATCH", "DELETE" ]
	validMethodFlag = False
	validVersionFlag = False
	
	# Check if the request line has a valid method 
	for validMethod in validMethodTypes:
		if method == validMethod:
			validMethodFlag = True
			
	# Check if the method is a GET request
	if method != "GET":
		validMethodFlag = False
		print( errorMessage501 )
		exit()
	
	# Check if the version is 1.1 or 1.0
	if version == "HTTP/1.1" or version == "HTTP/1.0":
		validVersionFlag = True
		
	# Return true if the method is GET and the version is correct
	return validMethodFlag and validVersionFlag
	
def checkHeaders( requestHeaders ):
	
	return True

# Splits the URL into the domain and extension, then returns the list with both
def urlSplitter( url ):
	
	# Create a list of valid domain suffixes
	domainSuffixes = [ ".com", ".org", ".edu", ".gov" ]
	
	# Initialize our list that will hold our domain and extension
	splitURL = []
	
	# Loop through all of the suffixes to see which one is being used
	for suffix in domainSuffixes:
		if suffix in url:
		
			# Split the url, but keep the suffix in the domain
			splitURL = url.split( suffix )
			splitURL[ 0 ] = splitURL[ 0 ] + suffix
			
	# Return our domain and extension
	return splitURL
	
# Make a more readable function to check if path is valid
def checkPathInvalid( path ):
	return not os.path.exists( path )

# Connects to a server and gives it the request from our socket
def connectToServer( url, request, domain ):

	hostIP = socket.gethostbyname( domain )
	with Socket(socket.AF_INET, socket.SOCK_STREAM) as outside_socket:

		outside_socket.connect(( domain, 80 ))
		outside_socket.settimeout( 5 )
		outside_socket.sendall( bytearray( request, 'utf-8' ))
		
		stillReceiving = True
		response = ""
		
		print( "before receive" )
		while stillReceiving: 
			try: 
				response += outside_socket.recv( 1024 ).decode('utf-8')
			except: 
				stillReceiving = False
			
		print( "after receive" )
		outside_socket.close()
		return response

if __name__ == "__main__":
    sys.exit(main())
