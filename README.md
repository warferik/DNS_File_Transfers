# Windows_File_Transfers
Repository for ways to transfer files to Windows using built in binaries

Techniques

dns_server.py (DNS Server that base64 encodes a file and then serves that file in TXT records that are availble through DNS)

Usage 
./dns_server.py (FILE_TO_Serve)

-Will output command to use powershell with nslookup to transfer file, then use certutil to decode.\n
-file that is created on windows system is named "newFile"\n
-run mv newFile to newFile.exe and run


