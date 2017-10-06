import glob
import json
import os
import re
import zipfile
from urllib.parse import urljoin

import requests
import wget
from bs4 import BeautifulSoup

url = 'http://cvlab.hanyang.ac.kr/tracker_benchmark/datasets.html'
vtb_dir = 'datasets/vtb/'
tmp_dir = os.path.join(vtb_dir, 'tmp')

json_filename = os.path.join(vtb_dir, 'vtb.json')


def parse_html():
    with requests.Session() as sess:
        res = sess.get(url)

    soup = BeautifulSoup(res.text, "html.parser")

    datasets = {}

    for table in soup.findAll('table', {'class': 'seqtable', 'id': 'motion'}):
        for td in table.findAll('td'):
            link = urljoin(url, td.find('a').get('href'))
            name = link.split('/')[-1].split('.')[0]
            tags = list(filter(None, re.split(',| ', td.find('small').text)))
            datasets[name] = {'name': name, 'link': link, 'tags': tags}
    return datasets


def fix_data():
    files = glob.glob('datasets/vtb/*/groundtruth_rect*')

    for file in files:
        if os.stat(file).st_size == 0:
            print('Remove empty file: {}'.format(file))
            os.remove(file)

    files = glob.glob('datasets/vtb/*/groundtruth_rect*')

    for file in files:
        with open(file, 'r') as f:
            s = f.read()

        s = s.strip().replace(',', ' ').replace('\t', ' ').strip('0 0 0 0')

        with open(file, 'w') as f:
            f.write(s)

if __name__ == '__main__':
    os.makedirs(vtb_dir, exist_ok=True)

    if not os.path.exists(json_filename):
        datasets = parse_html()
        json.dump(datasets, open(json_filename, 'w'), indent=4)

    datasets = json.load(open(json_filename, 'r'))

    for name in datasets:
        link = datasets[name]['link']

        os.makedirs(tmp_dir, exist_ok=True)

        filename = os.path.join(tmp_dir, link.split('/')[-1])

        if not os.path.exists(filename):
            print("Downloading {}".format(filename))
            wget.download(link, out=filename)
        else:
            print("{} exists".format(filename))

        if zipfile.is_zipfile(filename):
            with zipfile.ZipFile(filename, 'r') as zf:
                print("Extracting {}".format(filename))
                zf.extractall(vtb_dir)

    fix_data()
