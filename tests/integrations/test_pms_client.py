import pytest
from irp.integrations.pms_client import PMSProject, PMSPerson


def test_pms_project_model():
    project = PMSProject(
        project_id="PRJ001",
        name="Test Project",
        status="active"
    )
    assert project.project_id == "PRJ001"
    assert project.status == "active"


def test_pms_person_model():
    person = PMSPerson(
        person_id="P001",
        name="Jane Smith",
        skills=["Design", "Frontend"],
        department="Design",
        availability=1.0
    )
    assert person.name == "Jane Smith"
    assert person.availability == 1.0
    assert "Design" in person.skills
