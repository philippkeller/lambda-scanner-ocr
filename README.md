(will be) a lambda function to convert a tar-gzipped set of pnm files into one OCRed PDF

# Local testing

Using [emulambda](https://github.com/fugue/emulambda) you can try this:

```
export S3_BUCKET=scanner-upload
echo '{"file": "scan_2018-01-20_155119.tar.gz"}' | emulambda handler.handler - -v
```

# Setup of lambda

- add env variable: `S3_BUCKET=scanner-upload`
- put `Timeout` to 5 minutes

# Deploying

```
zip -r -q ocr-lambda.zip .
aws s3 cp ocr-lambda.zip s3://hansaplast-home/
```

On lambda: 

- Code entry type: `upload from S3`
- Runtime: `Python 3.6`
- Handler: `handler.handler`
- `S3 link URL`: `https://s3.eu-central-1.amazonaws.com/hansaplast-home/ocr-lambda.zip`

# Build tesseract binaries

Note to self: To build this, mainly follow [this post](https://stackoverflow.com/questions/33588262/tesseract-ocr-on-aws-lambda-via-virtualenv), tbd: try to use tesseract 4.0
