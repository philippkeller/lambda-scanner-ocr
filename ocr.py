import boto3
import tarfile
import os
import subprocess

s3 = boto3.client('s3')
s3.download_file('scanner-upload', 'scan_2018-01-20_155119.tar.gz', 'test.tar.gz')
tar = tarfile.open('test.tar.gz')
tar.extractall()
with open('filenames.txt', 'w') as f:
    f.write("\n".join(tar.getnames()))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(SCRIPT_DIR, 'lib')
env = os.environ.copy()
env.update(dict(LD_LIBRARY_PATH=LIB_DIR, TESSDATA_PREFIX=SCRIPT_DIR))
out = subprocess.check_output(['./tesseract', 'filenames.txt', 'out', 'pdf'], cwd=SCRIPT_DIR, env=env)
print(out)
