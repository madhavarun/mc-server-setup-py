import os
import requests
import shutil

def get_confirmation(prompt: str, default: str):
    fallback = f"Enter y, n, or leave blank for default({default})" 
    confirmation = input(prompt).strip().lower()

    while confirmation not in ["y", "n", "yes", "no", ""]:
        print(fallback)
        confirmation = input(prompt).strip().lower()

    if confirmation == "":
        confirmation = default
    elif confirmation == "yes":
        confirmation = "y"
    elif confirmation == "no":
        confirmation = "n"

    return confirmation == "y"

print("Running from " + os.getcwd())
### Get list of versions and download links

jarlist = requests.get("https://gist.githubusercontent.com/cliffano/77a982a7503669c3e1acb0a0cf6127e9/raw/1c9097ac7a88e33a9011d88a6619e92587e369b2/minecraft-server-jar-downloads.md")

with open("jarlist.md", "w") as jlfile:
    jlfile.writelines(jarlist.text)

with open("jarlist.md", "r") as infile:
    data = infile.readline()
    data = infile.readline()
    data = infile.readlines()

os.remove("jarlist.md")

versionmap = dict()

for version in data:
    version_data = list(map(str.strip, version.split("|")))
    versionmap[version_data[1]] = version_data[2]


### Get version input, create folder and download server jar
version_name = str()
while version_name not in versionmap:
    if version_name == "list":
        print(list(versionmap.keys()))
    print("Enter a valid minecraft version, or list to see the list of versions")
    version_name = input()

if not get_confirmation(f"Download server to {os.getcwd()}/output/{version_name}? <Y/n>: ", "y"):
    print("Script complete, exiting normally.")
    exit()

# Check if output path exists
if not os.path.exists("output"):
    os.mkdir("output")
os.chdir("output")

# Check if folder exists for selected version
if os.path.exists(version_name):
    if not get_confirmation(f"Folder for '{version_name}' exists. Replace? <y/N>: ", "n"):
        print("Script complete, exiting normally.")
        exit()

    # Remove the old directory
    else:
        print("Deleting old server directory...")
        shutil.rmtree(version_name)

os.mkdir(version_name)
os.chdir(version_name)
print("Downloading server jar...")
r = requests.get(versionmap[version_name])

with open("server.jar", "wb") as serverjar:
    serverjar.write(r.content)


if not get_confirmation("Create launch script? <y/N>: ", "n"):
    print("Script complete, exiting normally.")
    print(exit())

ram = input("Enter server RAM amount in GB: (2-6, default 2): ")
while True:
    if ram == "":
        ram = "2"
    try:
        ram = int(ram)
        break
    except ValueError:
        print("Enter an integer or leave blank for default")
    ram = input("Enter server RAM amount in GB: (2-6, default 2): ")

if os.name == "nt":
    ext = "bat"
elif os.name == "posix":
    ext = "sh"

with open(f"start.{ext}", "w") as startfile:
    startfile.write(f"java -jar -Xmx{ram}G -Xms{ram}G server.jar -nogui")

print("Script completed, exiting normally.")
