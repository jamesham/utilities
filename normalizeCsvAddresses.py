#!/usr/bin/env python3

import urllib.parse
import urllib.request
import json
import os
import sys
import qrz
import csv

if (len(sys.argv) != 2):
    sys.exit("Need CSV file argument")

uspsURL = 'https://tools.usps.com/tools/app/ziplookup/zipByAddress'

csvInName = sys.argv[1]

with open(csvInName) as csvIn:
    csvreader = csv.DictReader(csvIn)
    for row in csvreader:
        sys.stderr.write(f"{row['Name']}|{row['Street']}|{row['City']}|{row['State']}|{row['zip']}\n")

        csvAddr = {
            'companyName': '',
            'address1': row['Street'],
            'address2': '',
            'city': row['City'],
           'state': row['State'],
            'urbanCode': '',
           'zip': row['zip']
        }
        
        addrEnc = urllib.parse.urlencode(csvAddr).encode('ascii')

        req = urllib.request.Request(uspsURL)
        req.add_header('User-Agent','Mozilla/5.0')

        resp = urllib.request.urlopen(req,addrEnc)
        respJson = resp.read().decode('utf-8')

        respObj = json.loads(respJson)

        if ('resultStatus' not in respObj or respObj['resultStatus'] != 'SUCCESS'):
            sys.stderr.write(f"USPS Non-Success parsing previous line:\n{json.dumps(respObj, indent=4)}\n")
            continue

        csvwriter = csv.writer(sys.stdout,lineterminator=os.linesep)

        try:
            addr = respObj['addressList'][0]
            sys.stderr.write(f"USPS Normalized: {addr['addressLine1']} {addr['city']}, {addr['state']} {addr['zip5']}-{addr['zip4']}\n\n")
            output = [
                row['Name'],
                addr['addressLine1'],
                addr['city'],
                addr['state'],
                f"{addr['zip5']}-{addr['zip4']}"
            ]
            csvwriter.writerow(output)

        except KeyError:
            sys.stderr.write(f"USPS Data:\n{json.dumps(respObj, indent=4)}\n")
