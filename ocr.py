import boto3
import tarfile
import os, sys
import subprocess
from pdfrw import PdfReader, PdfWriter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(SCRIPT_DIR, 'lib')
DOWNLOAD_FILE = 'scan.tar.gz'
TMP_DIR = '/tmp'

s3 = boto3.client('s3')

# todo: 
# - remove empty pages using http://www.binpress.com/tutorial/pdfrw-the-other-python-PDF-library/171
# - try tessxeract 4.0..?
# - use tesseract_fast to lower the size (4MB vs 40MB!)
# - try if w/o deu package it makes any difference..
def ocr(tar_gz_filename, empty_page_threshold, language='eng'):
    tar = tarfile.open(tar_gz_filename)
    tar.extractall(path=TMP_DIR)
    env = os.environ.copy()
    env.update(dict(LD_LIBRARY_PATH=LIB_DIR, TESSDATA_PREFIX="{}/tessdata".format(SCRIPT_DIR)))

    output = PdfWriter()
    for filename in tar.getnames():
        cmd = ['./tesseract', '-l', language,
            '-c', 'min_orientation_margin=0', # don't leave out characters close to border
            '{}/{}'.format(TMP_DIR, filename),
            '{}/partial'.format(TMP_DIR),
            'pdf']
        try:
            out = subprocess.check_output(cmd, cwd=SCRIPT_DIR, env=env, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print('tesseract call failed, here\'s the output so far:')
            print(e.output)
            sys.exit(1)
        print(out)
        for p in PdfReader("{}/{}".format(TMP_DIR, "partial.pdf")).pages:
            try:
                if int(p.Contents['/Length']) < empty_page_threshold:
                    continue
            except:
                # if in doubt add the page
                pass
            output.addpage(p)
    output.write('{}/output.pdf'.format(TMP_DIR))

    for f in ['partial.pdf', DOWNLOAD_FILE] + tar.getnames():
        os.remove("{}/{}".format(TMP_DIR, f))
    return '{}/output.pdf'.format(TMP_DIR)
