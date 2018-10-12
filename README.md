# Windows_File_Transfers
Repository for ways to transfer files to Windows using built in binaries

Techniques
dns_server.py
-DNS Servers that base64 encodes a file and then servers that file in TXT records through DNS

Usage 
./dnsserv.py (FILE_TO_Serve)
-Will output command to use powershell with nslookup to transfer file, then use certutil to decode.
-file that is created on windows system is named "newFile"
run mv newFile to newFile.exe and run

