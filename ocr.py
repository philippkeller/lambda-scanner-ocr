import boto3
import tarfile
import os
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
def ocr(src_bucketname, src_filename, dest_bucketname, dest_filename, empty_page_threshold, language='eng'):
    if src_bucketname == dest_bucketname:
        raise Exception('cannot store resulting pdf in same bucket as source files as it would result in an endless loop')
    s3.download_file(src_bucketname, src_filename, "{}/{}".format(TMP_DIR, DOWNLOAD_FILE))
    tar = tarfile.open("{}/{}".format(TMP_DIR, DOWNLOAD_FILE))
    tar.extractall(path=TMP_DIR)
    env = os.environ.copy()
    env.update(dict(LD_LIBRARY_PATH=LIB_DIR, TESSDATA_PREFIX=SCRIPT_DIR))

    output = PdfWriter()
    for filename in tar.getnames():
        cmd = ['./tesseract', '-l', language,
            '{}/{}'.format(TMP_DIR, filename),
            '{}/partial'.format(TMP_DIR),
            'pdf']
        out = subprocess.check_output(cmd, cwd=SCRIPT_DIR, env=env, stderr=subprocess.STDOUT)
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
    s3.upload_file("{}/output.pdf".format(TMP_DIR), dest_bucketname, dest_filename)
    for f in ['partial.pdf', 'output.pdf', DOWNLOAD_FILE] + tar.getnames():
        os.remove("{}/{}".format(TMP_DIR, f))
