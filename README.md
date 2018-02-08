Lambda function to convert a tar-gzipped set of pnm files into one OCRed PDF

# Install

## Prerequisits

Before you start, you'll need..

- a **source s3 bucket**: this is where you'll upload `tar.gz` files which contains scanned images (only tested with pnm files so far). Needs to be in the same region as your lambda function
- an **IAM role** which allows to read + delete from source bucket. And store the log output. Attach this policy to the role:
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
  	      "logs:CreateLogGroup",
  	      "logs:CreateLogStream",
  	      "logs:PutLogEvents"
  	    ],
  	    "Resource": "arn:aws:logs:*:*:*"
  	  }
    ]
  }
  ```

## Lambda function

Set up a lambda function with

- `Runtime`: `Python 3.6`
- `Role`: the role you just created
- `Handler`: `handler.handler`
- env variable: `EMPTY_PAGE_THRESHOLD=200` if tesseract finds less than 200 characters on a page it's --- from experience --- likely to be empty and will be removed (assumes you're using a duplex scanner). If you want to disable empty page removal, just put this to 0
- optional: env variable: `TESSERACT_LANG`. Currently supported are `eng` english and `deu` deutsch. Default is english. If you want to add another language, see below
- `Timeout`: 5 minutes
- Memory: I chose 2048MB. The more memory you take, the faster the execution time (see also [the official doc](https://docs.aws.amazon.com/lambda/latest/dg/resource-model.html)). 128MB is not enough. It will lead to out of memory exceptions.

You have two options for storing your OCRed PDFs:

1. **Google drive**:
   - You need to first create a google api in the developers console, and turn on the google drive api [as described here](https://developers.google.com/drive/v3/web/quickstart/python#step_1_turn_on_the_api_name).
   - Copy the resulting `client_secret.json` into this projects root, then `pip install oauth2client` and then run `python scripts/get_drive_credentials`. Now, copy-paste the resulting values into the environment variables. This grants your lambda function to create files in your google drive and to access the files it created (which it won't need). See [here](https://developers.google.com/drive/v2/web/about-auth) for more details about the right you're granting.  
   - Optional: If you wish your PDFs to be stored in a specific folder, go to that folder in your google drive, copy the part in the url after `/folders/` and put that into an additional environment variabled named `GDRIVE_FOLDER`
2. **S3**: This is a lot easier as you'll only need to create an s3 bucket (in the same region as your lambda function) and add these lines to your policy (replace `<dest-bucket>`):
   ```
   {
     "Effect": "Allow",
     "Action": [
       "s3:PutObject"
     ],
     "Resource": ["arn:aws:s3:::<dest-bucket>/*"]
   }
   ```
   Then set the environment variables `UPLOAD_TYPE=s3` and `S3_BUCKET` to the name of the just created bucket.


Now, upload the zip file to lambda:

- download the ocr-lambda.zip from the releases section of github
- upload the zip file onto a s3 bucket of yours which is in the same region as your lambda function
- then, choose Code entry type: `upload from S3`
- `S3 link URL`: the s3 link of the file you just uploaded, this has the form `https://s3.<region>.amazonaws.com/<bucket>/ocr-lambda.zip`

## Test

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
scripts/zip.sh
aws s3 cp ocr-lambda.zip s3://<s3-bucket>/
aws lambda update-function-code --function-name <lambda-name> --s3-bucket <s3-bucket> --s3-key ocr-lambda.zip
```

# Further docs

- [guild tesseract binaries](doc/compile_tesseract.md)
- adding another language: git clone this repo, then cd into tessdata and load one of the files from within https://github.com/tesseract-ocr/tessdata_fast/raw/master/ into that dir. Then follow the instructions at "Build lambda function". Don't forget to set the `TESSERACT_LANG` env variable.