import zipfile
import copy
from random import shuffle, choice
import os
import json
import sys

# Check arguments
if len(sys.argv) < 2:
    datapack_path = "scrambler.zip"
    print("Using default datapack name: ./scrambler.zip")
else:
    datapack_path = sys.argv[1]

try:
    blacklist = list(map(lambda s: s.strip(), open(
    "blacklist.txt", "r").readlines()))
except FileNotFoundError:
    print("No blacklist detected, ignoring...")
    blacklist = []
all_data = {}  # key is the filename, value is the object data.
for file_handler in os.scandir('crafting_files/'):
    (basename, ext) = os.path.splitext(file_handler.name)
    if ext == ".json":
        file_data = json.load(open(file_handler.path, "r"))
        # Some special recipes don't have a result...
        # And we don't files in the blacklist too!
        if file_data.get("result") is None or basename in blacklist:
            continue
        all_data[file_handler.name] = file_data

random_data = copy.deepcopy(all_data)

# Create the zip file and write the pack.mcmeta
try:
    zip_file = zipfile.ZipFile(datapack_path, "x", zipfile.ZIP_DEFLATED, False)
except FileExistsError:
    print(f'{datapack_path} already exists.')
    exit()

data_folder = os.path.join("data", "minecraft", "recipes")
zip_file.writestr("pack.mcmeta", json.dumps({
    "pack": {
        "pack_format": 4,
        "description": "Scramble all the recipes!"
    }
}))

# Iterate over all the files and pop a random item from 'random_data',
# assigning its result value to the current file.
for i, (filename, obj) in enumerate(all_data.items()):
    # I need to find a better way...
    random_item = random_data.pop(choice(list(random_data.keys())))
    random_result = random_item.get("result")
    obj_result = obj.get("result")
    # Crafting recipes need an object for the result and everything else needs a string.
    # We have to convert them if the types between the current file and the random item are different.
    if type(random_result) == type(obj_result):
        obj["result"] = random_item["result"]
    # Case where we need a str but the random item is an object
    elif type(random_result) == dict and type(obj_result) == str:
        obj["result"] = random_item["result"]["item"]
    else:  # Case where we need an object but the random item is a str
        obj["result"] = {
            "item": random_item["result"]
        }

    zip_file.writestr(os.path.join(data_folder, filename), json.dumps(obj))
    # Progress bar :D
    # Thanks : https://gist.github.com/sibosutd/c1d9ef01d38630750a1d1fe05c367eb8
    percent = 100.0*(i+1)/len(all_data.items())
    sys.stdout.write('\r')
    sys.stdout.write("Completed: [{:{}}] {:>3}%"
                     .format('='*int(percent/(100.0/20)),
                             20, int(percent)))
    sys.stdout.flush()
zip_file.close()
print()
print("Done!")
