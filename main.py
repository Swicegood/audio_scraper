import configparser
import datetime
import asyncio
import audio_scraper
from ftplib import FTP

def upload_files_to_server(files, remote_path):
    # Read configuration file for credentials
    config = configparser.ConfigParser()
    config.read('config.ini')
    hostname = config['FTP']['hostname']
    username = config['FTP']['username']
    password = config['FTP']['password']

    # Connect to the server using FTP
    ftp = FTP(hostname)
    ftp.login(user=username, passwd=password)

    # Write the file list to a file
    with open('all_files.txt', 'w') as f:
        f.write('#' + str(datetime.datetime.now()) + '\n') 
        for file in files:
            f.write(file + '\n')

    # Upload the file to the remote server
    with open('all_files.txt', 'rb') as f:
        ftp.storbinary('STOR ' + remote_path, f)

    # Close the FTP connection
    ftp.quit()

async def main():
    all_files = await audio_scraper.get_all_files()
    print("Total files found:", len(all_files))
    upload_files_to_server(all_files, "/wp/wp-content/uploads/all_files.txt")

if __name__ == "__main__":
    asyncio.run(main())
    
