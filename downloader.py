import ftplib
import os
import shutil
import socket
import tarfile
import tempfile

MAIN_DOMAINS_DIR = "domains"
COMPRESSED_EXT = ".tar.gz"
AGGREGATE = True


def main():
    working_dir = os.getcwd()
    fetch = True
    decompress = True

    try:
        os.mkdir(MAIN_DOMAINS_DIR, 0o777)
    except OSError:
        tmp_dir_files = os.listdir(MAIN_DOMAINS_DIR)
        ext_filter = [COMPRESSED_EXT]
        uncompressed_files = [x for x in tmp_dir_files if all(y not in x for y in ext_filter)]
        if len(tmp_dir_files) != 0:
            fetch = False
        if len(uncompressed_files) != 0:
            decompress = False

    path = os.path.join(working_dir, MAIN_DOMAINS_DIR)
    os.chdir(path)

    list_files = []
    if fetch:
        list_files = download()
    else:
        list_files = os.listdir(".")

    decompress_files(decompress, list_files)


def decompress_files(decompress, list_files):
    if decompress:
        print("Decompressing list files:")
        print(list_files)
        for listFile in list_files:
            tar = tarfile.open(listFile, "r:gz")
            for member in tar.getmembers():
                # Process both domains and urls files, append them to the same domains.txt file
                if member.name.endswith("domains") or member.name.endswith("urls"):
                    extract = True
                    member_dir = member.name.split(os.path.sep)[0]
                    try:
                        os.mkdir(member_dir, 0o777)
                    except OSError as e:
                        if not str(e).__contains__("File exists"):
                            print('Could not create dir {}, exception {}. Omitting'.format(member_dir, e))
                            extract = False

                    if extract:
                        # Extract and re-write files filtering ipv4/v6 domains
                        f = tar.extractfile(member)
                        with tempfile.NamedTemporaryFile() as tp:
                            for domain in f.readlines():
                                if not is_ip(str(domain).strip()):
                                    tp.write(domain)
                            tp.seek(0)
                            with open(member_dir + os.path.sep + "domains.txt", 'ba') as f_out:
                                shutil.copyfileobj(tp, f_out)
                            tp.seek(0)
                            # Aggregate into the single, giant exclusion list
                            if AGGREGATE:
                                with open("the_whole_thing.txt", 'ba') as f_out:
                                    shutil.copyfileobj(tp, f_out)
    else:
        print("Local /domains directory with non compressed files exists. Check its contents and delete to try again")


def is_ip(s) -> bool:
    return is_valid_ipv4_address(s) or is_valid_ipv6_address(s)


# See https://stackoverflow.com/a/4017219/4887442
def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True


# See https://stackoverflow.com/a/4017219/4887442
def is_valid_ipv6_address(address):
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:  # not a valid address
        return False
    return True


def download():
    ftp = ftplib.FTP("ftp.ut-capitole.fr")
    ftp.connect()
    ftp.login()
    ftp.set_pasv(True)
    ftp.cwd("/pub/unix/reseau/cache/squidguard_contrib")

    # Obtain file list and filter only the expected domain lists
    files = ftp.nlst()
    exclusions = [
        ".",
        "..",
        "README.orig.tar.gz",
        "LICENSE.pdf.tar.gz",
        "cc-by-sa-4-0.pdf.tar.gz",
        "catalogue-biu-toulouse.tar.gz",
        "blacklists.tar.gz",
        "blacklists_for_dansguardian.tar.gz",
        "blacklists_for_pfsense.tar.gz",
        "blacklists_for_pfsense_reducted.tar.gz",
        # Size-oriented exclusions. See README
        "adult.tar.gz",
        "porn.tar.gz",
    ]
    list_files = list(set(files) - set(exclusions))
    for value in list_files:
        if not value.endswith(COMPRESSED_EXT):
            list_files.remove(value)

    print("Retrieving the following compressed lists from ftp server:")
    print(list_files)
    for listFile in list_files:
        with open(listFile, 'wb') as f:
            ftp.retrbinary(str('RETR ' + listFile), lambda data: f.write(data))
    ftp.close()

    return list_files


if __name__ == '__main__':
    main()
