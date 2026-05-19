from fastapi import FastAPI

from identity.presentation.http.auth_router import router as auth_router
from petstore.infrastructure.persistence.database import initialise_schema
from petstore.presentation.http.pet_event_router import router as pet_event_router
from petstore.presentation.http.pet_router import router as pet_router

app = FastAPI(title="Pet Store API", version="2.0.0")

initialise_schema()
app.include_router(auth_router)
app.include_router(pet_router)
app.include_router(pet_event_router)
