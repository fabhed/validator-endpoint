import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from btvep.config import Config, cast_str_to_bool

router = APIRouter()


class ConfigValue(BaseModel):
    key: str
    value: str


@router.get("/")
async def get_config():
    config = Config().to_json()
    return json.loads(config)


@router.get("/{key}")
async def get_config_value(key: str):
    config = Config().load()
    if key in config.__dict__:
        return {key: config.__dict__[key]}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown config key: {key}")


@router.post("/")
async def set_config_value(config_value: ConfigValue):
    key = config_value.key
    value = config_value.value
    config = Config().load()

    if key in config.__dict__:
        if isinstance(config.__dict__[key], bool):
            value = cast_str_to_bool(value)
        config.__dict__[key] = value
        config.save()
        return {key: config.load().__dict__[key]}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown config key: {key}")
