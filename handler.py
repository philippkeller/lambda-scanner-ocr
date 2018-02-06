import os
def handler(event, context):
    """
    download tar.gz, do ocr and upload it to configured cloud service
    (currently AWS S3 or Google Drive)
    """
    import ocr
    
    if os.environ['UPLOAD_TYPE'] == 'gdrive':
        upload_type = 'gdrive'
        folder = os.environ.get('GDRIVE_FOLDER', None)
        client_id = os.environ['GDRIVE_CLIENT_ID']
        client_secret =  os.environ['GDRIVE_CLIENT_SECRET']
        refresh_token = os.environ['GDRIVE_REFRESH_TOKEN']
        upload_params = (client_id, client_secret, refresh_token, folder)
    elif os.environ['UPLOAD_TYPE'] == 's3':
        bucket = os.environ['S3_BUCKET']
        upload_params = (bucket)
    else:
        raise Exception('unknown upload type {}'.format(os.environ['UPLOAD_TYPE']))

    empty_page_threshold = int(os.environ.get('EMPTY_PAGE_THRESHOLD', 200))
    language = os.environ.get('TESSERACT_LANG', 'eng')

    import boto3
    s3 = boto3.client('s3')
    for record in event['Records']:
        src_bucket = record['s3']['bucket']['name']
        src_file = record['s3']['object']['key']

        s3.download_file(src_bucket, src_file, "/tmp/scan.tar.gz")
        pdf_file = ocr.ocr("/tmp/scan.tar.gz", empty_page_threshold, language)

        dest_filename = src_file.split('.')[0] + '.pdf'
        if upload_type == 's3':
            s3.upload_file(pdf_file, upload_params[0], dest_filename)
        elif upload_type == 'gdrive':
            upload_gdrive(pdf_file, dest_filename, *upload_params)

        
def upload_gdrive(file_src, file_dest, client_id, client_secret, refresh_token, folder=None):
    import httplib2
    import os
    from apiclient import discovery
    from oauth2client import client
    from apiclient.http import MediaFileUpload

    credentials = client.GoogleCredentials(None, 
        client_id, 
        client_secret,
        refresh_token,
        None,
        "https://accounts.google.com/o/oauth2/token",
        'scanner-ocr')

    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    file_metadata = {
        'name': file_dest,
    }
    if folder is not None:
        file_metadata['parents'] = [folder]

    media = MediaFileUpload(file_src,
                            mimetype='image/jpeg')
    file = service.files().create(body=file_metadata,
                                  media_body=media,
                                  fields='id').execute()
