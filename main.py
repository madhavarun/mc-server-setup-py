import hashlib
import os
import requests
import shutil
import textwrap

from mc_parser import get_mojang

def get_sha1sum(filepath):
    sha1 = hashlib.sha1()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha1.update(chunk)
        return sha1.hexdigest()
    except Exception as e:
        print(f"Error: {e}")
        return ""

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
    elif confirmation in exitwords:
        print("Script cancelled, exiting.")
        exit()

    return confirmation == "y"


def fetch_server(vname, url, server_sha1sum = None, cache = False):
    if cache:
        file_sha1sum = get_sha1sum(url)
        if file_sha1sum == server_sha1sum:
            print("Found server jar in cache, using it instead.")
            try:
                shutil.copy2(url, os.path.curdir)
                return
            except Exception as e:
                print(f"Error copying server jar from cache: {e}")
        else:
            os.remove(url)

        server_meta = get_mojang(vname)
        if server_meta:
            url = server_meta["url"]
        else:
            print(f"Error in retrieving server metadata, exiting.")
            exit()

    # Use the official URL if no local copy exists/error in copying
    print("Downloading server jar...")
    r = requests.get(url)

    with open(f"{vname}.jar", "wb") as serverjar:
        serverjar.write(r.content)
    
    file_sha1sum = get_sha1sum(f"{vname}.jar")
    if file_sha1sum != server_sha1sum:
        print("Error in server jar: sha1sum mismatch, removing file and exiting.")
        os.remove(f"{vname}.jar")
        exit()

    if IN_ROOTDIR:
        print("Saving server jar to cache to avoid redownloading later.")
        try:
            shutil.copy2(os.path.abspath(f"{vname}.jar"), os.path.abspath(CACHE_DIR))
        except Exception as e:
            print(f"Error in saving server jar to cache: {e}")


def main(IN_ROOTDIR, CACHE_DIR):
    print("Running from " + os.getcwd())
    IN_ROOTDIR = os.path.exists(".rootdir")
    if not IN_ROOTDIR:
        if get_confirmation("WARNING: This script is intended to be run from the root directory. Exit? <Y/n>: ", "y"):
            print("Script cancelled, exiting.")
            exit()

    if IN_ROOTDIR and not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)

    ### Get version input, create folder and download server jar
    version_name = str()
    cache_exists = False
    print(textwrap.dedent("""\
          Version name (standard format, 1.x.y) or
          'latest'/'latest-snap' for newest versions or
          'list' to list all versions\
          """))
    while True:
        print("Enter the server version:")
        version_name = input("> ").strip().lower()
        if version_name in exitwords:
            print("Script cancelled, exiting.")
            exit()
            
        server_meta = get_mojang(version_name)
        if server_meta:
            url = server_meta["url"]
            sha1sum = server_meta["sha1"]
            cache_path = f"{CACHE_DIR}/{version_name}.jar"
            if os.path.exists(cache_path):
                url = os.path.abspath(cache_path)
                cache_exists = True
            break

    if not get_confirmation(f"Download server to {os.getcwd()}/server/{version_name}? <Y/n>: ", "y"):
        print("Script cancelled, exiting.")
        exit()

    # Check if output path exists
    if not os.path.exists("servers"):
        os.mkdir("servers")
    os.chdir("servers")

    # Check if folder exists for selected version
    if os.path.exists(version_name):
        os.chdir(version_name)
        if get_confirmation(f"Server for '{version_name}' exists. Replace server jar? <y/N>: ", "n"):
            # Remove the old server jar
            print("Deleting old server...")
            os.remove(f"{version_name}.jar")

        else:
            # Abort script, server jar exists
            print("Script cancelled, exiting.")
            exit()
    else:
        os.mkdir(version_name)
        os.chdir(version_name)

    fetch_server(version_name, url, cache=cache_exists, server_sha1sum=sha1sum)

    if not get_confirmation("Create launch script? <y/N>: ", "n"):
        print("Script complete, exiting normally.")
        print(exit())

    ram = input("Enter server RAM amount in GB (2-6, default 2): ")
    while True:
        if ram in exitwords:
            print("Skipped creating launch script, exiting.")
            exit()
        if ram == "":
            ram = "2"
        try:
            ram = int(ram)
            break
        except ValueError:
            print("Enter an integer or leave blank for default")
        ram = input("Enter server RAM amount in GB (2-6, default 2): ")

    if os.name == "nt":
        ext = "bat"
    elif os.name == "posix":
        ext = "sh"

    with open(f"start.{ext}", "w") as startfile:
        startfile.write(f"java -jar -Xmx{ram}G -Xms{ram}G {version_name}.jar --nogui\n")

    print("Script completed, exiting normally.")
    return

if __name__ == "__main__":
    IN_ROOTDIR = os.path.exists(".rootdir")
    CACHE_DIR = os.path.abspath("cache") if IN_ROOTDIR else "."
    exitwords = ["exit", "quit", "cancel", "e", "c", "q", "-1"]
    print("At any prompt, enter 'exit' to cancel the script.")
    # TODO: User set cache path
    main(IN_ROOTDIR, CACHE_DIR)
