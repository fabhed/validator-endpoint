import logging
import rich
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from btvep.chat_helpers import ChatResponseException

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

from btvep.api import all_endpoints
from btvep.api.dependencies import (
    InitializeRateLimiting,
)
from btvep.config import Config
from btvep.db.tables import create_all as create_all_tables
from btvep.db.utils import DB_PATH
from btvep.validator_prompter import ValidatorPrompter

create_all_tables()
config = Config().load().validate()

# Give info around configuration at server start
print("Config:")
rich.print_json(config.to_json(hide_mnemonic=True))
print("Using SQLite database at", DB_PATH)

# Initialize the validator prompter for bittensor
ValidatorPrompter(config.hotkey_mnemonic)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Allows all origins. You can change this to allow specific domains.
    allow_credentials=True,
    allow_methods=[
        "*"
    ],  # Allows all methods. You can change this to allow specific HTTP methods.
    allow_headers=[
        "*"
    ],  # Allows all headers. You can change this to allow specific headers.
)

app.include_router(all_endpoints)


@app.exception_handler(ChatResponseException)
async def unicorn_exception_handler(request: Request, exc: ChatResponseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "failed_responses": exc.failed_responses},
    )


@app.on_event("startup")
async def startup():
    if config.rate_limiting_enabled:
        await InitializeRateLimiting()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
