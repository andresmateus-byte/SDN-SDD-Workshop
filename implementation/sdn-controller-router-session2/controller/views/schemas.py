from pydantic import BaseModel, ConfigDict, Field, field_validator

class LinkChangeRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    node_a: str = Field(min_length=1)
    node_b: str = Field(min_length=1)

    @field_validator("node_a", "node_b")
    @classmethod
    def non_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value
