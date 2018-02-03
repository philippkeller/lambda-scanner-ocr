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
- env variable: `EMPTY_PAGE_THRESHOLD=200` if tesseract finds less than 200 characters on a page it's --- from experience --- likely to be empty and will be removed (assumes you're using a duplex scanner). If you want to disable empty page removal, just put this to 0
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


# Build lambda function

```
cd root/of/repo
pip3 install -r requirements.txt -t $(pwd)
zip -r ocr-lambda.zip . -x '/.git*' -x '/doc*' -x ocr-lambda.zip -x README.md -x requirements.txt -x LICENSE
aws s3 cp ocr-lambda.zip s3://<s3-bucket>/
aws lambda update-function-code --function-name <lamba-nam> --s3-bucket <s3-bucket> --s3-key ocr-lambda.zip
```

# Further docs

- [guild tesseract binaries](doc/compile_tesseract.md)
