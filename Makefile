.PHONY: install lint test validate build deploy delete

install:
	python -m pip install -r requirements-dev.txt

lint:
	ruff check src tests

test:
	pytest -q

validate:
	python -m json.tool statemachine/delivery.asl.json > /dev/null
	sam validate

build:
	sam build

deploy:
	sam deploy --guided

delete:
	sam delete
