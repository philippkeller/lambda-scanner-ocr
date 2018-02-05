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
	    },
		{
		  "Effect": "Allow",
		  "Action": [
		    "logs:CreateLogGroup",
		    "logs:CreateLogStream",
		    "logs:PutLogEvents"
		  ],
		  "Resource": "arn:aws:logs:*:*:*"
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
- optional: env variable: `TESSERACT_LANG`. Currently supported are `eng` english and `deu` deutsch. Default is english. If you want to add another language, see below
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

- do a reload of the page (otherwise, you'll be in "test mode" and cannot save the trigger.. yeah, that's a aws bug..)
- `Bucket`: the bucket where the lambda function should listen to
- `Event tpye`: `Object Created (All)`
- `Prefix` and `Suffix` you can leave empty


# Build lambda function

```
cd root/of/repo
virtualenv --python=python3.6 .
pip install -r requirements.txt
git archive -o ocr-lambda.zip HEAD
cd lib/python3.6/site-packages
zip -r ../../../ocr-lambda.zip .
cd -
aws s3 cp ocr-lambda.zip s3://<s3-bucket>/
aws lambda update-function-code --function-name <lamba-name> --s3-bucket <s3-bucket> --s3-key ocr-lambda.zip
```

# Further docs

- [guild tesseract binaries](doc/compile_tesseract.md)
- adding another language: git clone this repo, then cd into tessdata and load one of the files from within https://github.com/tesseract-ocr/tessdata_fast/raw/master/ into that dir. Then follow the instructions at "Build lambda function". Don't forget to set the `TESSERACT_LANG` env variable.