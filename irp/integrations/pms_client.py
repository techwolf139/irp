import httpx
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from irp.core.retry import retry_async, RetryConfig


class PMSProject(BaseModel):
    project_id: str
    name: str
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class PMSPerson(BaseModel):
    person_id: str
    name: str
    skills: List[str] = []
    department: str
    availability: float = 1.0


class PMSClient:
    def __init__(self, base_url: str, retry_config: Optional[RetryConfig] = None):
        self.base_url = base_url
        self.retry_config = retry_config or RetryConfig()
        self.client = httpx.AsyncClient(timeout=self.retry_config.timeout)

    @retry_async(max_retries=3, delay=1.0, backoff=2.0, exceptions=(httpx.HTTPError,))
    async def get_projects(self) -> List[PMSProject]:
        response = await self.client.get(f"{self.base_url}/api/projects")
        response.raise_for_status()
        return [PMSProject(**p) for p in response.json()]

    @retry_async(max_retries=3, delay=1.0, backoff=2.0, exceptions=(httpx.HTTPError,))
    async def get_project(self, project_id: str) -> PMSProject:
        response = await self.client.get(f"{self.base_url}/api/projects/{project_id}")
        response.raise_for_status()
        return PMSProject(**response.json())

    @retry_async(max_retries=3, delay=1.0, backoff=2.0, exceptions=(httpx.HTTPError,))
    async def get_persons(self) -> List[PMSPerson]:
        response = await self.client.get(f"{self.base_url}/api/persons")
        response.raise_for_status()
        return [PMSPerson(**p) for p in response.json()]

    @retry_async(max_retries=3, delay=1.0, backoff=2.0, exceptions=(httpx.HTTPError,))
    async def get_person(self, person_id: str) -> PMSPerson:
        response = await self.client.get(f"{self.base_url}/api/persons/{person_id}")
        response.raise_for_status()
        return PMSPerson(**response.json())

    async def close(self):
        await self.client.aclose()
