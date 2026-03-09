import re
from decimal import Decimal
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_price(text: str | None):
    if not text:
        return None

    cleaned = (
        text.replace("\xa0", " ")
        .replace("₴", "")
        .replace("грн", "")
        .replace(",", ".")
        .strip()
    )
    cleaned = re.sub(r"[^\d.]", "", cleaned)

    if not cleaned:
        return None

    try:
        value = Decimal(cleaned)
    except Exception:
        return None

    if value < 5000 or value > 500000:
        return None

    return value


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def extract_product_urls_from_soup(soup: BeautifulSoup) -> list[str]:
    product_urls = []
    seen = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin("https://brain.com.ua", href)

        if "/ukr/Mobilniy_telefon_Apple_iPhone" not in full_url:
            continue

        if full_url in seen:
            continue

        seen.add(full_url)
        product_urls.append(full_url)

    return product_urls


def extract_next_page_url(soup: BeautifulSoup, current_url: str) -> str | None:
    candidates = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin("https://brain.com.ua", href)

        # беремо тільки лінки тієї ж категорії
        if "/ukr/category/Telefony_mobilni-c1274/" not in full_url:
            continue

        # ігноруємо саму поточну сторінку
        if full_url == current_url:
            continue

        # шукаємо або page=, або типові пагінаційні класи/атрибути
        cls = " ".join(a.get("class", []))
        rel = " ".join(a.get("rel", []))
        text = a.get_text(" ", strip=True)

        if (
            "page=" in full_url
            or "next" in cls.lower()
            or "pagination" in cls.lower()
            or "next" in rel.lower()
            or text in {">", "›", "→", "Наступна"}
        ):
            candidates.append(full_url)

    if not candidates:
        return None

    candidates = sorted(set(candidates), key=len)
    return candidates[0]


def get_catalog_product_urls(catalog_url: str, max_pages: int = 20) -> list[str]:
    all_product_urls = []
    seen_products = set()
    seen_pages = set()

    next_page = catalog_url
    page_num = 0

    while next_page and next_page not in seen_pages and page_num < max_pages:
        seen_pages.add(next_page)
        page_num += 1

        soup = get_soup(next_page)

        page_products = extract_product_urls_from_soup(soup)

        added = 0
        for url in page_products:
            if url in seen_products:
                continue
            seen_products.add(url)
            all_product_urls.append(url)
            added += 1

        print(f"PAGE {page_num}: found {added} urls")

        next_page = extract_next_page_url(soup, next_page)

    return all_product_urls


def get_variant_urls(soup: BeautifulSoup, base_url: str) -> list[str]:
    variant_urls = []
    seen = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin("https://brain.com.ua", href)

        if "/ukr/Mobilniy_telefon_Apple_iPhone" not in full_url:
            continue

        if full_url == base_url:
            continue

        if full_url in seen:
            continue

        seen.add(full_url)
        variant_urls.append(full_url)

    return variant_urls


def parse_brain_product(url: str) -> dict:
    soup = get_soup(url)

    name_tag = soup.find("h1")
    name = name_tag.get_text(strip=True) if name_tag else None

    product_code = None
    code_label = soup.find("span", string=re.compile(r"Код товару"))
    if code_label:
        code_value = code_label.find_next("span")
        product_code = code_value.get_text(strip=True) if code_value else None

    reviews_count = 0
    reviews_tag = soup.select_one(".reviews-count")
    if reviews_tag:
        match = re.search(r"\d+", reviews_tag.get_text())
        if match:
            reviews_count = int(match.group())

    price_regular = None
    price_current = None

    old_price_tag = soup.select_one(".br-pr-op")
    if old_price_tag:
        price_regular = parse_price(old_price_tag.get_text())

    new_price_tag = soup.select_one(".br-pr-np")
    if new_price_tag:
        price_current = parse_price(new_price_tag.get_text())



    images = []
    seen_images = set()

    for img in soup.find_all("img"):
        img_url = img.get("src")

        if (
            not img_url
            or img_url.startswith("data:")
            or img_url.endswith(".svg")
            or "/static/images/prod_img/" not in img_url
            or img_url in seen_images
        ):
            continue

        seen_images.add(img_url)
        images.append(img_url)

    characteristics = {}
    items = soup.select(".br-pr-chr-item")

    for item in items:
        rows = item.select("div > div")

        for row in rows:
            spans = row.find_all("span", recursive=False)
            if len(spans) < 2:
                continue

            key = spans[0].get_text(strip=True)
            value = clean_text(spans[1].get_text(" ", strip=True))

            if key and value:
                characteristics[key] = value

    variant_urls = get_variant_urls(soup, url)

    return {
        "name": name,
        "url": url,
        "product_code": product_code,
        "manufacturer": characteristics.get("Виробник"),
        "color": characteristics.get("Колір"),
        "memory": characteristics.get("Вбудована пам'ять"),
        "screen_size": characteristics.get("Діагональ екрану"),
        "resolution": characteristics.get("Роздільна здатність екрану"),
        "price_regular": price_regular,
        "price_current": price_current,
        "reviews_count": reviews_count,
        "images": images,
        "characteristics": characteristics,
        "variant_urls": variant_urls,
    }