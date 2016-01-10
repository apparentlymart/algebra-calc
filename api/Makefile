
lambda_dist.zip: lambda_dist
	cd lambda_dist && zip -r ../lambda_dist.zip *

lambda_dist:
	mkdir -p lambda_dist
	cp *.py lambda_dist/
	pip install -r requirements.txt -t lambda_dist/

#	cp -r env/lib/python2.7/site-packages/* lambda_dist/

clean:
	rm -rf lambda_dist/ lambda_dist.zip

.PHONY: clean
