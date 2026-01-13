from sys import argv
import requests, re
from os import listdir
from pathlib import Path
import pandas as pd

try:
    coll_id = argv[1].strip()
except:
    print("run script as:\n$ python3 count_dls.py [collection ID]")
    exit(0)

solrbase = "https://solr-od2.library.oregonstate.edu/solr/prod/"
select = f"{solrbase}select?fl=id&q=member_of_collection_ids_ssim%3A{coll_id}&rows=100000"
jsonresponse = requests.get(select).json()
coll_works = [ id['id'] for id in jsonresponse['response']['docs'] ]
print(f"{len(coll_works)} works in collection {coll_id}")

getstart = re.compile(r'^# Start date: (\d{8})$')
getend = re.compile(r'^# End date: (\d{8})$')
exports = [ file for file in listdir("exports") if file.split('.')[-1] == "csv" ]

for csv in exports:
    start, end = None, None
    count = 0
    csvp = Path(f"exports/{csv}")
    lines = csvp.read_text(encoding="utf-8").splitlines(keepends=True)
    for line in lines[0:9]:
        s = re.match(getstart, line)
        if s != None:
            start = s.group(1)
        e = re.match(getend, line)
        if e != None:
            end = e.group(1)
    data = pd.read_csv(f"exports/{csv}", comment="#")
    for row in data.itertuples():
        if row._1.split('/')[-1] in coll_works:
            # pid extraction ^^^ needs to be more precise
            count += int(row.Views)
    print(f"from {start} to {end}, {count} views")
