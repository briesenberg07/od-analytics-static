from sys import argv
import requests, re, json
from os import listdir
from pathlib import Path
import pandas as pd

message = "run script as:\n$ python[3 if home] count_dls.py [collection ID] [home|office]"

try:
    coll_id = argv[1].strip()
    work_loc = argv[2].strip()
except:
    print(message)
    exit(0)
if work_loc not in ["home", "office"]:
    print(message)
    exit(0)
elif work_loc == "home":
    dir = "/home/nebgreb/Dropbox/work_dropbox/ga4"
elif work_loc == "office":
    dir = "C:/Users/briesenb/University of Oregon Dropbox/Benjamin Riesenberg/ga4"

solrbase = "https://solr-od2.library.oregonstate.edu/solr/prod/"
select = f"{solrbase}select?fl=id&q=member_of_collection_ids_ssim%3A{coll_id}&rows=100000"
jsonresponse = requests.get(select).json()
coll_works = [ id['id'] for id in jsonresponse['response']['docs'] ]
# print(f"{len(coll_works)} works in collection {coll_id}") # do something else with this?

getstart = re.compile(r'^# Start date: (\d{8})$')
getend = re.compile(r'^# End date: (\d{8})$')
exports = sorted([ file for file in listdir(dir) if file.split('.')[-1] == "csv" ])

data = {}
for csv in exports:
    count = 0
    date = csv.split('.')[0]
    start, end = None, None
    csvp = Path(f"{dir}/{csv}")
    lines = csvp.read_text(encoding="utf-8").splitlines(keepends=True)
    for line in lines[0:9]:
        s = re.match(getstart, line)
        if s != None:
            start = s.group(1)
        e = re.match(getend, line)
        if e != None:
            end = e.group(1)
    dl = pd.read_csv(f"{dir}/{csv}", comment="#")
    for row in dl.itertuples():
        if str(row._1).split('/')[-1] in coll_works:
            # pid extraction ^^^ needs to be more precise,
            # skip rows which don't include 9-char PID
            count += int(row.Views)
    if len(date) == 4:
        data.update({date: {
            "total": count,
            "details": f"from {start} to {end}"
            }})
    elif len(date) == 6:
        if date[0:4] in data:
            data[date[0:4]].update({date: {
                "total": count,
                "details": f"from {start} to {end}"
            }})
        else:
            data.update({date[0:4]: {
                date: {
                    "total": count,
                    "details": f"from {start} to {end}"
                }}})
    with open(f"data/{coll_id}.json", "w") as jf:
        json.dump(data, jf, indent=4)
