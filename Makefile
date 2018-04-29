VERSION=`cat version.txt`
OWNER=samstradling
REPO=cloudinary-jwt

setup:
	pip install -r requirements-dev.txt --quiet

test: setup
	flake8
	coverage run -m nose
	coverage-badge > coverage.svg
	coverage report

build:
	docker build . -t $(OWNER)/$(REPO):latest
	docker tag $(OWNER)/$(REPO):latest $(OWNER)/$(REPO):$(VERSION)

deploy: build
	docker push $(OWNER)/$(REPO):latest
	docker push $(OWNER)/$(REPO):$(VERSION)
	# Increment Version
	awk -F"." '{print $$1"."$$2"."$$3+1}' version.txt > tmpversionfile && mv tmpversionfile version.txt
