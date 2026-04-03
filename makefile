.PHONY: benchmark rest graphql hybrid stop

PORT_REST=5000
PORT_GQL=5001
PORT_HYBRID=5002

rest:
	FLASK_APP=src/server_rest.py flask run --port $(PORT_REST)

graphql:
	FLASK_APP=src/server_graphql.py flask run --port $(PORT_GQL)

hybrid:
	FLASK_APP=src/server_hybrid.py flask run --port $(PORT_HYBRID)

benchmark:
	-FLASK_APP=src/server_rest.py flask run --port $(PORT_REST) & \
	FLASK_APP=src/server_graphql.py flask run --port $(PORT_GQL) & \
	FLASK_APP=src/server_hybrid.py flask run --port $(PORT_HYBRID) & \
	sleep 3 && \
	python3 src/client_benchmark.py
	pkill -f flask