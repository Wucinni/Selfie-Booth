netsh advfirewall firewall add rule name=""Selfie-Booth" TCP Port 5000" dir=in action=allow protocol=TCP localport=5000
netsh advfirewall firewall add rule name=""Selfie-Booth" TCP Port 5000" dir=out action=allow protocol=TCP localport=5000
netsh advfirewall firewall add rule name=""Selfie-Booth" UDP Port 5000" dir=in action=allow protocol=UDP localport=5000
netsh advfirewall firewall add rule name=""Selfie-Booth" UDP Port 5000" dir=out action=allow protocol=UDP localport=5000
pause