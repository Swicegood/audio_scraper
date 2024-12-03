import configparser
import datetime
import asyncio
import audio_scraper
import yaml
import subprocess
import os

BADFILESFILE = 'bad_files.txt'

def remove_bad_files(files):
    # Read the bad files from the file
    with open(BADFILESFILE, 'r') as f:
        bad_files = f.readlines()
    bad_files = [x.strip() for x in bad_files]

    # Remove the bad files from the list
    files = [file for file in files if file not in bad_files]
    return files

def rename_problem_files(files):
    # Read in dictionary of problem files from file renames.yaml
    with open('renames.yaml', 'r') as f:
        renames = yaml.safe_load(f)
    # Rename the files
    for i, file in enumerate(files):
        if file in renames:
            files[i] = renames[file]
            print(f"Renamed {file} to {renames[file]}")
    return files

def upload_files_to_server(files, remote_path):

    # Write the file list to a file
    with open('all_files.txt', 'w') as f:
        f.write('#' + str(datetime.datetime.now()) + '\n') 
        for file in files:
            f.write(file + '\n')
    # Step 2: Copy file from host to remote server
    subprocess.run(["scp", "-i", "id_rsa_atourcity",  "all_files.txt", "atourcity@newgoloka.com:public_html/bkgoswami.com/wp/wp-content/uploads/"])

async def main():
    all_files = await audio_scraper.get_all_files()
    total_files = len(all_files)
    print("Total files found:", total_files)
    all_files = remove_bad_files(all_files)
    print("Total files after removing bad files:", len(all_files))
    print("Bad files removed ", total_files - len(all_files))
    all_files = rename_problem_files(all_files)
    print("Renamed problem files")
    print("Uploading files to server...")
    upload_files_to_server(all_files, "/wp/wp-content/uploads/all_files.txt")

if __name__ == "__main__":
    asyncio.run(main())
    
