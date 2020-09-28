from google.cloud import storage
from datetime import datetime
import pytz

utc=pytz.UTC

bucket = storage.Client().get_bucket("nlp_keyword_bucket")
total_keyword_utternaces = []
total_counts_dict = dict()

new_keyword_utternaces = []
new_counts_dict = dict()

threshold_date = datetime(2020, 1, 1)
for blob in bucket.list_blobs(prefix="data_dir/"):
    total_keyword_utternaces.append(blob.name)
    keyword = blob.name.split("/")[1:][0].lower()
    
    try:
        total_counts_dict[keyword] += 1
    except KeyError:
        total_counts_dict[keyword] = 1
    
    if blob.updated.replace(tzinfo=utc) > threshold_date.replace(tzinfo=utc):
        new_keyword_utternaces.append(blob.name)
        try:
            new_counts_dict[keyword] += 1
        except KeyError:
            new_counts_dict[keyword] = 1

print("Total utterances: " + str(len( total_keyword_utternaces )) )
print("2020 utterances: " + str(len( new_keyword_utternaces )) )
print("Total and 2020 utterances per keyword are to be dumped in a file called total_dumps and new_dumps.txt")

with open("total_dumps.txt", "w") as tfd:

    for keyword, count in total_counts_dict.items():

        tfd.write(keyword + "    " + str(count) +  "\n")

with open("new_dumps.txt", "w") as nfd:

    for keyword, count in new_counts_dict.items():

        nfd.write(keyword + "    " + str(count) +  "\n")


