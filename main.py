import json

from aiohttp import web
from pydantic import ValidationError
from sqlalchemy import select

from models import Advertisement, Session, close_db, init_db
from schema import AdvertisementCreate, AdvertisementUpdate


def json_response(data, status: int = 200) -> web.Response:
    return web.json_response(data, status=status, dumps=lambda d: json.dumps(d, ensure_ascii=False))


async def get_ad_or_404(session, ad_id: int) -> Advertisement:
    ad = await session.get(Advertisement, ad_id)
    if ad is None:
        raise web.HTTPNotFound(
            text=json.dumps({"error": f"advertisement {ad_id} not found"}),
            content_type="application/json",
        )
    return ad


async def parse_json(request: web.Request) -> dict:
    try:
        return await request.json()
    except json.JSONDecodeError:
        raise web.HTTPBadRequest(
            text=json.dumps({"error": "invalid JSON body"}),
            content_type="application/json",
        )


async def list_ads(request: web.Request) -> web.Response:
    async with Session() as session:
        result = await session.execute(select(Advertisement).order_by(Advertisement.id))
        ads = result.scalars().all()
        return json_response([ad.to_dict() for ad in ads])


async def get_ad(request: web.Request) -> web.Response:
    ad_id = int(request.match_info["ad_id"])
    async with Session() as session:
        ad = await get_ad_or_404(session, ad_id)
        return json_response(ad.to_dict())


async def create_ad(request: web.Request) -> web.Response:
    payload = await parse_json(request)
    try:
        data = AdvertisementCreate.model_validate(payload)
    except ValidationError as exc:
        raise web.HTTPBadRequest(
            text=exc.json(), content_type="application/json"
        )

    async with Session() as session:
        ad = Advertisement(**data.model_dump())
        session.add(ad)
        await session.commit()
        await session.refresh(ad)
        return json_response(ad.to_dict(), status=201)


async def update_ad(request: web.Request) -> web.Response:
    ad_id = int(request.match_info["ad_id"])
    payload = await parse_json(request)
    try:
        data = AdvertisementUpdate.model_validate(payload)
    except ValidationError as exc:
        raise web.HTTPBadRequest(
            text=exc.json(), content_type="application/json"
        )

    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        raise web.HTTPBadRequest(
            text=json.dumps({"error": "no fields to update"}),
            content_type="application/json",
        )

    async with Session() as session:
        ad = await get_ad_or_404(session, ad_id)
        for key, value in updates.items():
            setattr(ad, key, value)
        await session.commit()
        await session.refresh(ad)
        return json_response(ad.to_dict())


async def delete_ad(request: web.Request) -> web.Response:
    ad_id = int(request.match_info["ad_id"])
    async with Session() as session:
        ad = await get_ad_or_404(session, ad_id)
        await session.delete(ad)
        await session.commit()
        return json_response({"status": "deleted", "id": ad_id})


async def on_startup(app: web.Application) -> None:
    await init_db()


async def on_cleanup(app: web.Application) -> None:
    await close_db()


def build_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/ads", list_ads)
    app.router.add_post("/ads", create_ad)
    app.router.add_get(r"/ads/{ad_id:\d+}", get_ad)
    app.router.add_patch(r"/ads/{ad_id:\d+}", update_ad)
    app.router.add_delete(r"/ads/{ad_id:\d+}", delete_ad)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app


if __name__ == "__main__":
    web.run_app(build_app(), host="0.0.0.0", port=8080)
