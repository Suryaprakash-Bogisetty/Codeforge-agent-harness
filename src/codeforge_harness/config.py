"""Harness configuration: config/harness.toml plus environment overrides."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from pydantic import BaseModel, Field

DEFAULT_CONFIG_PATH = Path("config/harness.toml")


class BenchmarkConfig(BaseModel):
    path: Path = Path("../codeforge-benchmark")


class SandboxConfig(BaseModel):
    kind: str = "local"
    exec_timeout_seconds: int = 120
    max_output_bytes: int = 20_000


class RunConfig(BaseModel):
    runs_dir: Path = Path("runs")


class LLMConfig(BaseModel):
    base_url: str = "https://api.groq.com/openai/v1"
    model: str = "moonshotai/kimi-k2-instruct"
    temperature: float = 0.0
    max_iterations: int = 12
    api_key: str | None = None  # populated from GROQ_API_KEY, never from the toml file


class AgentConfig(BaseModel):
    kind: str = "mock"
    llm: LLMConfig = Field(default_factory=LLMConfig)


class HarnessConfig(BaseModel):
    benchmark: BenchmarkConfig = Field(default_factory=BenchmarkConfig)
    sandbox: SandboxConfig = Field(default_factory=SandboxConfig)
    run: RunConfig = Field(default_factory=RunConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)

    @classmethod
    def load(cls, path: Path | None = None) -> HarnessConfig:
        cfg_path = path or DEFAULT_CONFIG_PATH
        data: dict = {}
        if cfg_path.is_file():
            data = tomllib.loads(cfg_path.read_text())
        cfg = cls.model_validate(data)

        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            cfg.agent.llm.api_key = api_key
        return cfg
