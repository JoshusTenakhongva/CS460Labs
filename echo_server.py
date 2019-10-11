# Server program that echos any message that is sent
import socket

HOST = '127.0.0.1'
PORT = 65432

# Setup
# API: socket()
with socket.socket( socket.AF_INET, socket.SOCK_STREAM ) as s: 
	# API: bind()
	s.bind(( HOST, PORT ))
	# API: listen()
	s.listen() # If you dont give an integer, itll autofill

	# Connection
	# API: accept()
	conn, addr = s.accept()
	with conn: 
		print( 'Connected by ', addr )
		while True: 
			# Handle service requests
			data = conn.recv( 1024 )
			if not data: 
				break
			conn.sendall( data )
# Close
# API: close()
	s.close()
