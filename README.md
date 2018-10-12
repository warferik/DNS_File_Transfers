# DNS_File_Transfers

dns_server.py (DNS Server that base64 encodes a file and then serves that file in TXT records that are available through DNS)

Usage:

python3 dns_server.py (FILE_TO_SERVE)

-Will output command to use powershell or batch with nslookup to transfer file, then use certutil to decode.

-File that is created on windows system is named "newFile.exe"


