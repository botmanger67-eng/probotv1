"""
Pydantic schemas for project-related API requests and responses.

This module defines validation models for creating, updating,
and retrieving projects. It imports the ProjectStatus enum from
the project model and uses Pydantic's BaseModel for data validation.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    """
    Schema for creating a new project.

    Attributes:
        name: Project name (required, 3-100 characters).
        description: Optional description (max 1000 characters).
        status: Initial status; defaults to ProjectStatus.PLANNING.
    """

    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Project name (3-100 characters)",
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional project description",
    )
    status: ProjectStatus = Field(
        default=ProjectStatus.PLANNING,
        description="Initial project status",
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        """Ensure the project name is not just whitespace."""
        if not value.strip():
            raise ValueError("Project name cannot be blank")
        return value.strip()

    @field_validator("description")
    @classmethod
    def description_must_not_be_blank(cls, value: Optional[str]) -> Optional[str]:
        """Strip whitespace from description if present."""
        if value is not None and not value.strip():
            raise ValueError("Description cannot be blank if provided")
        return value.strip() if value else value


class ProjectUpdate(BaseModel):
    """
    Schema for updating an existing project (all fields optional).

    Attributes:
        name: Updated project name (3-100 characters).
        description: Updated description (max 1000 characters).
        status: Updated project status.
    """

    name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Updated project name (3-100 characters)",
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Updated project description",
    )
    status: Optional[ProjectStatus] = Field(
        None,
        description="Updated project status",
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: Optional[str]) -> Optional[str]:
        """Ensure the name is not blank if provided."""
        if value is not None and not value.strip():
            raise ValueError("Name cannot be blank")
        return value.strip() if value else value

    @field_validator("description")
    @classmethod
    def description_must_not_be_blank(cls, value: Optional[str]) -> Optional[str]:
        """Strip whitespace from description if present."""
        if value is not None and not value.strip():
            raise ValueError("Description cannot be blank if provided")
        return value.strip() if value else value