from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class LevelBase(SQLModel):
    name: str
    number: int
    building_id: Optional[int] = Field(default=None, foreign_key="building.id")


class Level(LevelBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class BuildingBase(SQLModel):
    name: str
    site_id: Optional[int] = Field(default=None, foreign_key="site.id")


class Building(BuildingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    levels: List[Level] = Relationship(back_populates=None, sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class SiteBase(SQLModel):
    name: str
    description: Optional[str] = None


class Site(SiteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
