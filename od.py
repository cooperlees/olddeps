#!/usr/bin/env python3
# Copyright (c) 2014-present, Facebook, Inc.

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Awaitable, Dict, Generator, List, Union

import aiohttp
import click
import requirements


LOG = logging.getLogger(__name__)


def _handle_debug(
    ctx: click.core.Context,
    param: Union[click.core.Option, click.core.Parameter],
    debug: Union[bool, int, str],
) -> Union[bool, int, str]:
    """Turn on debugging if asked otherwise INFO default"""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s (%(filename)s:%(lineno)d)",
        level=log_level,
    )
    return debug


def get_requirements(req_file: Path) -> Generator:
    LOG.debug(f"Opening {req_file} to parse with requirements")
    with req_file.open("r") as rfp:
        return requirements.parse(rfp.read())


async def get_req_stats(
    pkg_req: requirements.requirement.Requirement,
    aiohttp_session: aiohttp.client.ClientSession,
    url: str = "https://pypi.org/pypi/{}/json",
) -> Dict:
    pkg_url = url.format(pkg_req.name)
    async with aiohttp_session.get(pkg_url) as response:
        try:
            pkg_json = await response.json()
        except aiohttp.client_exceptions.ContentTypeError:
            LOG.error(f"{pkg_req} does not return JSON ...")
            return {}

    version = str(pkg_req.specs[0][1])
    try:
        version_json = pkg_json["releases"][version].pop()
    except KeyError:
        LOG.error(f"{pkg_req} version does not exist in JSON ...")
        return {}

    upload_dt = datetime.strptime(version_json["upload_time"], "%Y-%m-%dT%H:%M:%S")
    dt_now = datetime.now()
    return {
        "name": pkg_req.name,
        "latest": version == pkg_json["info"]["version"],
        "released_days_ago": (dt_now - upload_dt).days,
        "upload_time": version_json["upload_time"],
        "version": version,
    }


async def check_file(req_file: Path) -> List:
    loop = asyncio.get_event_loop()
    LOG.info(f"Parsing {req_file}")
    reqs = await loop.run_in_executor(None, get_requirements, req_file)
    get_stats_coros: List[Awaitable] = []

    async with aiohttp.ClientSession() as session:
        for req in reqs:
            get_stats_coros.append(get_req_stats(req, session))

        return await asyncio.gather(*get_stats_coros)


async def async_main(debug: bool, requirements_files: List[str]) -> int:
    file_coros: Dict[Path, Awaitable] = {}
    for requirements_file in requirements_files:
        rfp = Path(requirements_file)
        if not rfp.exists():
            LOG.error(f"{rfp} does not exit. Skipping")

        file_coros[rfp] = check_file(rfp)

    if not file_coros:
        return -1

    all_pkg_status = await asyncio.gather(*list(file_coros.values()))
    file_paths = list(file_coros.keys())
    for idx, pkg_status in enumerate(all_pkg_status):
        print(f"Packages from {file_paths[idx]}")
        clean_pkg_stats = [ps for ps in pkg_status if ps]
        for pkg in sorted(
            clean_pkg_stats, key=lambda x: x["released_days_ago"], reverse=True
        ):
            if not pkg:
                continue

            if pkg["latest"]:
                print(f" - {pkg['name']} {pkg['version']}: LATEST")
            else:
                print(f" - {pkg['name']} {pkg['version']}: {pkg['released_days_ago']} days old")

    return 0


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--debug",
    is_flag=True,
    callback=_handle_debug,
    show_default=True,
    help="Turn on debug logging",
)
@click.argument("requirements_files", nargs=-1)
@click.pass_context
def main(ctx, **kwargs) -> None:
    ctx.exit(asyncio.run(async_main(**kwargs)))


if __name__ == "__main__":
    main()
