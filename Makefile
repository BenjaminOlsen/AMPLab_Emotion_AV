.PHONY: build upload all

all: build push

build:
	docker build -t mtgupf/amplab-jamendo-notebook .

push:
	docker push mtgupf/amplab-jamendo-notebook

