Lambda function to convert a tar-gzipped set of pnm files into one OCRed PDF

# Install

## S3 buckets

You need to create:

- one source s3 bucket: this is where you'll upload `tar.gz` files which contains scanned images (only tested with pnm files so far)
- one destination bucket: this is where this lambda function will upload the resulting pdf to

Both buckets should be in the same region as your lambda function.

## IAM role

Now, create an IAM role which allows to read/write from source bucket (after reading the non-OCR source it will delete the file) and write to destination bucket:

1. navigate to IAM
2. create a **Policy**, switch to JSON tab
3. put the json below, replace the Resource with the ARNs from the buckets you just created:

	```json
	{
	  "Version": "2012-10-17",
	  "Statement": [
	    {
	      "Effect": "Allow",
	      "Action": [
	        "s3:GetObject",
	        "s3:DeleteObject"
	      ],
	      "Resource": ["arn:aws:s3:::<source-bucket>/*"]
	    },
	    {
	      "Effect": "Allow",
	      "Action": [
	        "s3:PutObject"
	      ],
	      "Resource": ["arn:aws:s3:::<dest-bucket>/*"]
	    }
	  ]
	}
	```
4. name the policy e.g. `ReadWriteOCR`
5. create a **Role** for Lambda
6. in the permissions step, choose the policy `ReadWriteOCR` you just created
7. name the role e.g. `ReadWriteOCR`


## Lambda function

Set up a lambda function with

- `Name`: e.g. `ocr`
- `Runtime`: `Python 3.6`
- `Role`: `Choose an existing role`
- `Existing role`: the role you just created, e.g. `ReadWriteOCR`

Then, in the lambda function set

- Handler: `handler.handler`
- env variable: `S3_DEST_BUCKET=<bucket-name>` Destination bucket name where lambda will upload the pdf
- `Timeout`: 5 minutes
- Memory: I chose 2048MB. The more memory you take, the faster the execution time (see also [the official doc](https://docs.aws.amazon.com/lambda/latest/dg/resource-model.html)). 128MB is not enough. It will lead to out of memory exceptions.

Then, upload the zip file to lambda:

- download the ocr-lambda.zip from the releases section of github
- upload the zip file onto a s3 bucket of yours which is in the same region as your lambda function
- then, choose Code entry type: `upload from S3`
- `S3 link URL`: the s3 link of the file you just uploaded, this has the form `https://s3.<region>.amazonaws.com/<bucket>/ocr-lambda.zip`

# Test

Upload tar.gz with 1 or more pnm files into `<bucket-name>`. then add new test handler with this:

```json
{
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "<source-bucket>"
        },
        "object": {
          "key": "<filename-you-just-uploaded>.tar.gz"
        }
      }
    }
  ]
}
```

## Add trigger

From the `Add triggers` menu on the left choose `S3`, then in `Configure trigger` dialogue:

- `Bucket`: the bucket where the lambda function should listen to
- `Event tpye`: `Object Created (All)`
- `Prefix` and `Suffix` you can leave empty

# Local testing

Using [emulambda](https://github.com/fugue/emulambda) you can try this:

```
export S3_BUCKET=scanner-upload
echo '{"Records":[{"s3":{"bucket":{"name":"scanner-upload"},"object":{"key":"scan_2018-01-20_155119.tar.gz"}}}]}' | emulambda handler.handler - -v
```

# Build tesseract binaries

This was mainly taken from  [this post](https://stackoverflow.com/questions/33588262/tesseract-ocr-on-aws-lambda-via-virtualenv) with minor modifications.

Tested, 2018-01-22 on an amazon linux ami 4.9.76-3.78.amzn1.x86_64:

```bash
sudo yum install gcc gcc-c++ make -y
sudo yum install autoconf aclocal automake -y
sudo yum install libtool -y
sudo yum install libjpeg-devel libpng-devel libpng-devel libtiff-devel zlib-devel -y
cd ~
mkdir leptonica
cd leptonica/
wget http://www.leptonica.com/source/leptonica-1.73.tar.gz
tar -xzvf leptonica-1.73.tar.gz
cd leptonica-1.73
./configure
make
sudo make install
cd ~
mkdir tesseract
cd tesseract/
wget https://github.com/tesseract-ocr/tesseract/archive/3.04.01.tar.gz
tar -xzvf 3.04.01.tar.gz
cd tesseract-3.04.01/
./autogen.sh
./configure
make
sudo make install
cd /usr/local/share/tessdata/
sudo wget https://github.com/tesseract-ocr/tessdata/raw/3.04.00/eng.traineddata
sudo wget https://github.com/tesseract-ocr/tessdata/raw/3.04.00/deu.traineddata
export TESSDATA_PREFIX=/usr/local/share/
cd ~
mkdir tesseract-lambda
cd tesseract-lambda/
cp /usr/local/bin/tesseract .
mkdir lib
cd lib/
cp /usr/local/lib/libtesseract.so.3 .
cp /usr/local/lib/liblept.so.5 .
cp /usr/lib64/libpng12.so.0 .
cp /usr/lib64/libz.so .
cd ..
cp -r /usr/local/share/tessdata .
cd tessdata
wget https://github.com/tesseract-ocr/tessdata/raw/master/osd.traineddata
cd ~
zip -r tesseract-lambda.zip tesseract-lambda
```

# Build lambda function

Unzip `tesseract-lambda.zip` you just built into the root of this repo

Then upload it to s3:

```
zip -r -q ocr-lambda.zip . -x deploy.sh -x ocr-lambda.zip -x README.md
aws s3 cp ocr-lambda.zip s3://<s3-bucket>/
```

# Refresh lambda function

```
aws lambda update-function-code --function-name <lamba-nam> --s3-bucket <s3-bucket> --s3-key ocr-lambda.zip
```