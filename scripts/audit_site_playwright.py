#!/usr/bin/env python3
"""Playwright audit for the Active-Edge customer site and Insights metadata."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"
PRODUCTION_ORIGIN = "https://active-esl.com"


def sitemap_paths():
    root = ET.parse(str(SITEMAP)).getroot()
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    paths = []
    for loc in root.findall("s:url/s:loc", namespace):
        parsed = urlparse(loc.text.strip())
        paths.append(parsed.path or "/")
    return paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://review.active-esl.com")
    parser.add_argument("--report", default="/tmp/aesl-playwright-audit.json")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    failures = []
    warnings = []
    results = []
    canonical_seen = {}

    def fail(path, message):
        failures.append({"path": path, "message": message})

    def warn(path, message):
        warnings.append({"path": path, "message": message})

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for viewport_name, viewport in (
            ("desktop", {"width": 1440, "height": 1000}),
            ("mobile", {"width": 390, "height": 844}),
        ):
            context = browser.new_context(
                viewport=viewport,
                user_agent=(
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "Chrome/140 Safari/537.36"
                ),
            )
            if viewport_name == "desktop":
                context.grant_permissions(["clipboard-read", "clipboard-write"], origin=base)

            for path in sitemap_paths():
                url = base + path
                page = context.new_page()
                console_errors = []
                bad_responses = []
                page_errors = []
                page.on(
                    "console",
                    lambda message, errors=console_errors: errors.append(
                        {"text": message.text, "location": message.location}
                    )
                    if message.type == "error"
                    else None,
                )
                page.on(
                    "response",
                    lambda response, errors=bad_responses: errors.append(
                        {"status": response.status, "url": response.url}
                    )
                    if response.status >= 400
                    else None,
                )
                page.on("pageerror", lambda error, errors=page_errors: errors.append(str(error)))
                response = page.goto(url, wait_until="networkidle", timeout=30000)
                status = response.status if response else 0
                if status != 200:
                    fail(path, "{} returned HTTP {}".format(viewport_name, status))
                    page.close()
                    continue

                title = page.title().strip()
                description_locator = page.locator('meta[name="description"]')
                canonical_locator = page.locator('link[rel="canonical"]')
                description = (
                    description_locator.get_attribute("content")
                    if description_locator.count()
                    else ""
                ) or ""
                canonical = (
                    canonical_locator.get_attribute("href")
                    if canonical_locator.count()
                    else ""
                ) or ""
                h1_count = page.locator("main h1").count()
                overflow = page.evaluate(
                    "() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"
                )
                missing_alt = page.locator("main img:not([alt])").count()
                empty_links = page.evaluate(
                    """() => [...document.querySelectorAll("a")].filter(
                      link => !link.textContent.trim() &&
                              !link.getAttribute("aria-label") &&
                              !link.querySelector("img[alt]")
                    ).length"""
                )

                if not title:
                    fail(path, "{} has no title".format(viewport_name))
                if not canonical:
                    fail(path, "{} has no canonical link".format(viewport_name))
                if not (50 <= len(description) <= 170):
                    warn(path, "meta description length is {} characters".format(len(description)))
                if h1_count != 1:
                    fail(path, "{} has {} main h1 elements".format(viewport_name, h1_count))
                if overflow:
                    fail(path, "{} has horizontal overflow".format(viewport_name))
                if missing_alt:
                    fail(path, "{} has {} main images without alt".format(viewport_name, missing_alt))
                if empty_links:
                    fail(path, "{} has {} unnamed links".format(viewport_name, empty_links))
                if console_errors:
                    fail(path, "{} console errors: {}".format(viewport_name, console_errors))
                if bad_responses:
                    fail(path, "{} failed responses: {}".format(viewport_name, bad_responses))
                if page_errors:
                    fail(path, "{} page errors: {}".format(viewport_name, page_errors))

                if viewport_name == "desktop":
                    expected_canonical = PRODUCTION_ORIGIN + path
                    if canonical != expected_canonical:
                        fail(path, "canonical is {!r}; expected {!r}".format(canonical, expected_canonical))
                    if canonical in canonical_seen:
                        fail(path, "canonical duplicates {}".format(canonical_seen[canonical]))
                    canonical_seen[canonical] = path

                    og = {}
                    for name in ("og:type", "og:url", "og:title", "og:description", "og:image"):
                        locator = page.locator('meta[property="{}"]'.format(name))
                        og[name] = locator.get_attribute("content") if locator.count() else ""
                        if not og[name]:
                            fail(path, "missing {}".format(name))
                    if og.get("og:url") != canonical:
                        fail(path, "og:url does not match canonical")

                    if path.startswith("/insights/") and path != "/insights/":
                        for name in (
                            "og:image:secure_url",
                            "og:image:type",
                            "og:image:width",
                            "og:image:height",
                            "og:image:alt",
                        ):
                            if not page.locator('meta[property="{}"]'.format(name)).count():
                                fail(path, "missing {}".format(name))
                        if page.locator('meta[property="og:image:width"]').get_attribute("content") != "1200":
                            fail(path, "Open Graph image width is not 1200")
                        if page.locator('meta[property="og:image:height"]').get_attribute("content") != "627":
                            fail(path, "Open Graph image height is not 627")

                        ld_blocks = page.locator('script[type="application/ld+json"]').all_text_contents()
                        parsed = []
                        for block in ld_blocks:
                            try:
                                parsed.append(json.loads(block))
                            except ValueError as error:
                                fail(path, "invalid JSON-LD: {}".format(error))
                        articles = [item for item in parsed if item.get("@type") == "BlogPosting"]
                        if len(articles) != 1:
                            fail(path, "expected one BlogPosting JSON-LD object")

                        share = page.locator(".insight-share")
                        if share.count() != 1:
                            fail(path, "missing article share panel")
                        else:
                            linked_in = share.locator('a[href*="linkedin.com/sharing/share-offsite/"]')
                            share_href = linked_in.get_attribute("href") if linked_in.count() == 1 else ""
                            share_url = parse_qs(urlparse(share_href).query).get("url", [""])[0]
                            if linked_in.count() != 1 or share_url != canonical:
                                fail(path, "LinkedIn share URL does not contain canonical URL")
                            copy = share.locator(".copy-link")
                            if copy.get_attribute("data-copy-url") != canonical:
                                fail(path, "Copy link does not use canonical URL")
                            copy.click()
                            page.wait_for_timeout(100)
                            if "Link copied" not in share.locator(".copy-link__status").inner_text():
                                fail(path, "Copy link did not report success")

                        og_path = urlparse(og["og:image"]).path
                        dimensions = page.evaluate(
                            """async (src) => {
                              const image = new Image();
                              image.src = src;
                              await image.decode();
                              return [image.naturalWidth, image.naturalHeight];
                            }""",
                            base + og_path,
                        )
                        if dimensions != [1200, 627]:
                            fail(path, "served Open Graph image is {}x{}".format(*dimensions))

                results.append(
                    {
                        "path": path,
                        "viewport": viewport_name,
                        "status": status,
                        "title": title,
                        "description_length": len(description),
                        "canonical": canonical,
                    }
                )
                page.close()
            context.close()
        browser.close()

    report = {
        "base_url": base,
        "pages_checked": len(results),
        "failures": failures,
        "warnings": warnings,
        "results": results,
    }
    Path(args.report).write_text(json.dumps(report, indent=2) + "\n")
    print("Playwright: {} page/viewport checks, {} failures, {} warnings".format(
        len(results), len(failures), len(warnings)
    ))
    for item in failures:
        print("FAIL {}: {}".format(item["path"], item["message"]))
    for item in warnings:
        print("WARN {}: {}".format(item["path"], item["message"]))
    print("Report: {}".format(args.report))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
