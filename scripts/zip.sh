rm -f ocr-lambda.zip
git archive -o ocr-lambda.zip HEAD
cd lib/python3.?/site-packages
zip -r ../../../ocr-lambda.zip .
cd -
zip ocr-lambda.zip tessdata/*.traineddata # if you use additional languages
