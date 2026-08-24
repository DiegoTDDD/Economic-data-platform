up:
	cd infrastructure && docker-compose up -d

down:
	cd infrastructure && docker-compose down

logs:
	cd infrastructure && docker-compose logs -f

init:
	python database_init.py

pipeline:
	python orchestrator.py

dashboard:
	streamlit run dashboards/main_dashboard.py

test:
	python -m unittest discover -s tests
