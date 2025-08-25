from datetime import datetime
from typing import Annotated, TypeAlias

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator


def _dt_str_to_dt(v: str) -> datetime:
    DATE_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
    return datetime.strptime(v, DATE_FMT)


DateTime: TypeAlias = Annotated[
    datetime,
    BeforeValidator(_dt_str_to_dt),
]


class KoboProjectView(BaseModel):
    model_config = ConfigDict(extra="ignore")
    uid: str
    name: str | None = None
    permissions: list[str]
    assigned_users: list[str]


class KoboLabelValue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str
    value: str


class KoboAssetSettings(BaseModel):
    sector: KoboLabelValue | None = None
    country: list[KoboLabelValue]
    description: str | None
    collects_pii: KoboLabelValue | None = None
    organization: str | None
    country_codes: list[str]

    @field_validator("sector", "collects_pii", mode="before")
    def empty_dict_to_none(cls, v):
        if v == {}:
            return None
        return v

    @field_validator("organization", "description", mode="before")
    def empty_str_to_none(cls, v) -> str | None:
        if v == "":
            return None
        return v


class KoboAssetSummary(BaseModel):
    geo: bool
    labels: list[str]
    columns: list[str]
    languages: list[str]
    row_count: int
    default_translation: str


class KoboSurveyNode(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str | None = None
    type: str
    kuid: str | None = Field(None, alias="$kuid")
    xpath: str | None = Field(None, alias="$xpath")
    qpath: str | None = Field(None, alias="$qpath")
    autoname: str | None = Field(None, alias="$autoname")
    label: list[str | None] | None = None
    required: bool | str = Field(False)
    relevant: str | None = None


class KoboAssetContent(BaseModel):
    survey: list[KoboSurveyNode]


class KoboAsset(BaseModel):
    url: str
    uid: str
    kind: str | None = None
    settings: KoboAssetSettings
    asset_type: str
    summary: KoboAssetSummary | None = None
    date_created: DateTime
    date_modified: DateTime
    date_deployed: DateTime | None = None
    version_id: str | None = None
    version__content_hash: str | None = None
    has_deployment: bool
    deployed_version_id: str | None = None
    content: KoboAssetContent | None = None
