from typing import List

from fastapi import FastAPI, HTTPException

from app.db import init_db, get_session
from app.models import Site, Building, Level

app = FastAPI(title="Pointr CMS APIs")


@app.get("/")
def root():
    return {"message": "Pointr CMS API is running", "docs": "/docs"}


@app.on_event("startup")
def on_startup():
    init_db()


# Site Endpoints
@app.post("/sites", response_model=Site, status_code=201)
def import_site(site: Site):
    with get_session() as session:
        session.add(site)
        session.commit()
        session.refresh(site)
        return site


@app.get("/sites/{site_id}", response_model=Site)
def get_site(site_id: int):
    with get_session() as session:
        site = session.get(Site, site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        return site


@app.delete("/sites/{site_id}", status_code=204)
def delete_site(site_id: int):
    with get_session() as session:
        site = session.get(Site, site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        session.delete(site)
        session.commit()
        return


# Building Endpoints
@app.post("/buildings", response_model=Building, status_code=201)
def import_building(building: Building):
    with get_session() as session:
        # ensure site exists
        if building.site_id and not session.get(Site, building.site_id):
            raise HTTPException(status_code=400, detail="Site does not exist")
        session.add(building)
        session.commit()
        session.refresh(building)
        return building


@app.get("/buildings/{building_id}", response_model=Building)
def get_building(building_id: int):
    with get_session() as session:
        building = session.get(Building, building_id)
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")
        return building


@app.delete("/buildings/{building_id}", status_code=204)
def delete_building(building_id: int):
    with get_session() as session:
        building = session.get(Building, building_id)
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")
        session.delete(building)
        session.commit()
        return


# Levels API - import single or multiple
from typing import Union

@app.post("/levels", response_model=List[Level], status_code=201)
def import_levels(levels: Union[Level, List[Level]]):
    with get_session() as session:
        levels_list = levels if isinstance(levels, list) else [levels]
        # validate building ids
        for lvl in levels_list:
            if lvl.building_id and not session.get(Building, lvl.building_id):
                raise HTTPException(status_code=400, detail=f"Building {lvl.building_id} does not exist")
        session.add_all(levels_list)
        session.commit()
        for lvl in levels_list:
            session.refresh(lvl)
        return levels_list
