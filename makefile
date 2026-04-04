.PHONY: inspect-running
inspect-running:
	ss -ltnp

.PHONY: seed-database
seed-database:
	rm -f app.db
	python3 src/database.py

.PHONY: rest
rest:
	FLASK_APP=src/server_rest.py flask run --port 5000

.PHONY: graphql
graphql:
	FLASK_APP=src/server_graphql.py flask run --port 5001

.PHONY: hybrid
hybrid:
	FLASK_APP=src/server_hybrid.py flask run --port 5002

.PHONY: client
client:
	python3 src/client_benchmark.py

.PHONY: run
run:
	$(MAKE) rest &
	$(MAKE) graphql &
	$(MAKE) hybrid &
	$(MAKE) client
