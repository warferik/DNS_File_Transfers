# DNS_File_Transfers

dns_server.py (DNS Server that base64 encodes a file and then serves that file in TXT records that are availble through DNS)

Usage 
python3 dns_server.py (FILE_TO_SERVE)

-Will output command to use powershell with nslookup to transfer file, then use certutil to decode.

-File that is created on windows system is named "newFile"

-Run mv newFile to newFile.exe and run


