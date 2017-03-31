import bluetooth

server_sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)

server_sock.bind(("",1))
server_sock.listen(1)

client_sock,address = server_sock.accept()


print 'Accepted connection from ',address

data=client_sock.recv(1024)

print data