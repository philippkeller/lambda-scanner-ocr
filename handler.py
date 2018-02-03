import os
def handler(event, context):
    import ocr
    dest_bucket = os.environ['S3_DEST_BUCKET']
    empty_page_threshold = int(os.environ['EMPTY_PAGE_THRESHOLD'])
    if 'TESSERACT_LANG' in os.environ:
    	language = os.environ['TESSERACT_LANG']
    else:
    	language = 'eng'
    for record in event['Records']:
        src_bucket = record['s3']['bucket']['name']
        src_file = record['s3']['object']['key']
        dest_file = src_file.split('.')[0] + '.pdf'
        ocr.ocr(src_bucket, src_file, dest_bucket, dest_file, empty_page_threshold, language)
