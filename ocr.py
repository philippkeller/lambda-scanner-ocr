import boto3
import tarfile
import os
import subprocess
import pdfrw


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
def ocr(src_bucketname, src_filename, dest_bucketname, dest_filename):
	print("pdfrw version: {}".format(pdfrw.__version__))
	if src_bucketname == dest_bucketname:
		raise Exception('cannot store resulting pdf in same bucket as source files as it would result in an endless loop')
	s3.download_file(src_bucketname, src_filename, "{}/{}".format(TMP_DIR, DOWNLOAD_FILE))
	tar = tarfile.open("{}/{}".format(TMP_DIR, DOWNLOAD_FILE))
	tar.extractall(path=TMP_DIR)
	with open('{}/filenames.txt'.format(TMP_DIR), 'w') as f:
	    f.write("\n".join(["{}/{}".format(TMP_DIR, n) for n in tar.getnames()]))
	env = os.environ.copy()
	env.update(dict(LD_LIBRARY_PATH=LIB_DIR, TESSDATA_PREFIX=SCRIPT_DIR))
	out = subprocess.check_output(['./tesseract', 
		'{}/filenames.txt'.format(TMP_DIR),
		'{}/out'.format(TMP_DIR),
		'pdf'], cwd=SCRIPT_DIR, env=env)
	s3.upload_file("{}/out.pdf".format(TMP_DIR), dest_bucketname, dest_filename)
	for f in ['out.pdf', 'filenames.txt', DOWNLOAD_FILE] + tar.getnames():
		os.remove("{}/{}".format(TMP_DIR, f))
