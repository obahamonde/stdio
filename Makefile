.PHONY: setup test build-docs docker-build

setup:
	./scripts/setup.sh

test:
	./scripts/test.sh

build-docs:
	./scripts/build_docs.sh

docker-build:
	docker build -t your-application .

docker-run:
	docker run --rm -p 8000:8000 your-application
