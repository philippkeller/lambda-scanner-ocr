import os
def handler(event, context):
	import ocr
	src_bucket = os.environ['S3_SRC_BUCKET']
	dest_bucket = os.environ['S3_DEST_BUCKET']
	src_file = event['file']
	dest_file = src_file.split()[0] + '.pdf'

	# S3_BUCKET = 'scanner-upload'
	# S3_FILE = 'scan_2018-01-20_155119.tar.gz'

	ocr.ocr(src_bucket, src_file, dest_bucket, dest_file)