import os
def handler(event, context):
	import ocr
	bucket = os.environ['S3_BUCKET']
	file = event['file']
	# S3_BUCKET = 'scanner-upload'
	# S3_FILE = 'scan_2018-01-20_155119.tar.gz'
	ocr.ocr(bucket, file, "")