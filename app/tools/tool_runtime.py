"""
工具运行时
"""

from pydantic import BaseModel

class ToolSchema(BaseModel):
    base_url: str
    api_key: str
