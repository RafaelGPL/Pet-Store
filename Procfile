release: python -c "from petstore.infrastructure.persistence.database import initialise_schema; initialise_schema()"
web: uvicorn main:app --host 0.0.0.0 --port $PORT
