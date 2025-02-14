"""Adam Peace 2020
Retrieves all Snapchat memories from AWS
"""

import urllib
import json
import requests
import datetime
import os
import shutil

# Helper Functions

def get_datetime(memory_date):
    return datetime.datetime.strptime(
            memory_date,
            "%Y-%m-%d %H:%M:%S %Z"
        )

def get_ext(memory_media_type):
    ext = "mp4"
    if memory["Media Type"] == "Image" or memory["Media Type"] == "PHOTO":
        ext = "jpg"
    return ext

def download_file_from_url(url, filename):
    with requests.get(url, stream=True) as r:
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    return filename

overwrite = False # Overwrites existing useful memory metadata file
st = datetime.datetime.now()

# Import Memories Data

memories = []
with open("memories_history.json") as memories_file:
    data = json.load(memories_file)
    all_memories = data["Saved Media"]
    print(len(all_memories), "memories to download")
    memories = all_memories

print(
    "First memory is a {}, taken on {} (available at {}...)".format(
            memories[-1]["Media Type"],
            memories[-1]["Date"],
            memories[-1]["Download Link"][:10]
    )
)

# Download all memories and record the time taken

if os.path.exists("useful_memories_history.json") and not overwrite:
    with open("useful_memories_history.json") as fp:
        data = json.load(fp)
        memories = data
else:
    print("Fetching all actual URLs")
    # Get Download Links

    st = datetime.datetime.now()
    for i, memory in enumerate(memories):
        print("{}: Time Elapsed: {}. Getting URL for date {}:".format(i + 1, datetime.datetime.now() - st, memory["Date"]), end=" ")
        try:
            link = requests.post(memory["Download Link"]).text
            print("Success")
            memory["url"] = link
        except:
            print("Failed")
    # Save memories JSON _with_ AWS URLs

    with open('useful_memories_history.json', 'w') as fp:
        json.dump(memories, fp)


print("Downloading all memories")

for memory in memories:
    memory_datetime = get_datetime(memory["Date"])
    filename = "memories/{:%Y-%m-%d-%H%M%S}.{}".format(
        memory_datetime,
        get_ext(memory["Media Type"])
    )

    print("Downloading File {}:".format(filename), end=" ")
    try:
        download_file_from_url(memory["url"], filename)
        modtime = datetime.datetime.timestamp(memory_datetime)
        os.utime(filename, (modtime, modtime))
        print("Success")
    except:
        print("Error")

print("Finished in {}. Bye!".format(datetime.datetime.now() - st))
