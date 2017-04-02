import bluetooth

bd_addr = "B8:27:EB:46:FB:77"
port = 2

print 'Creating connection.'
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
print 'Trying to connect...'
sock.connect((bd_addr, port))
print 'Connected'
while True:
    data = raw_input('Enter data to send": ')
    sock.send(data)
    if data == 'q':
        sock.close()
        exit(0)
