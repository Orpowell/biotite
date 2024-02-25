import requests
import gzip
import timeit

def gzip_download():
    r = requests.get("https://files.rcsb.org/download/4hhb.pdb.gz")

    content = gzip.decompress(r.content)

    with open("/Users/oliverpowell/4hhb_gz.pdb", "wb+") as file:
        file.write(content)

def download():
    r = requests.get("https://files.rcsb.org/download/4hhb.pdb")

    content = r.content

    with open("/Users/oliverpowell/4hhb_gz.pdb", "wb+") as file:
        file.write(content)

num_runs = 10
num_repetions = 100

download_times = timeit.Timer(download).repeat(repeat=num_repetions, number=num_runs)
download_mean = sum(download_times) / num_repetions

gzip_download_times = timeit.Timer(gzip_download).repeat(repeat=num_repetions, number=num_runs)
gzip_download_mean = sum(gzip_download_times) / num_repetions


print(f'{download_mean=}')
print(f'{gzip_download_mean=}')

