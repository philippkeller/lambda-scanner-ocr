import os
def handler(event, context):
	dest_bucket = os.environ['S3_DEST_BUCKET']
	import ocr
	for record in event['Records']:
		src_bucket = record['s3']['bucket']['name']
		src_file = record['s3']['object']['key']
		dest_file = src_file.split('.')[0] + '.pdf'
		ocr.ocr(src_bucket, src_file, dest_bucket, dest_file)
