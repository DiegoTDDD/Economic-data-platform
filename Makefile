up:
	cd infrastructure && docker-compose up -d --build

down:
	cd infrastructure && docker-compose down

build:
	cd infrastructure && docker-compose build

logs:
	cd infrastructure && docker-compose logs -f

pipeline-run:
	cd infrastructure && docker-compose start pipeline

test:
	python -m unittest discover -s tests
