#!/usr/bin/env python3
"""
Import script: Google Sheets -> DB + Drive photos -> /var/www/navernyborshchu/photos/
Usage: python import_data.py [--dry-run] [--skip-photos]
"""
import os
import sys
import json
import time
import urllib.request
import urllib.parse
import django
import re
from pathlib import Path
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'naverny_borschu_api.settings')
sys.path.insert(0, '/home/admin/projects/navernyborshchu-backend')
django.setup()

from core.models import Place, Borsch, Rating

DRY_RUN = '--dry-run' in sys.argv
SKIP_PHOTOS = '--skip-photos' in sys.argv

API_KEY = 'AIzaSyAbTZivJSKXKNl98GB9E8cpeFDvsb79uH0'
SHEET_ID = '11Bg5k3PLXYe5N5s1Nd-TKR8hHr531A00iqg_DUdgKpQ'
PHOTOS_DIR = Path('/var/www/navernyborshchu/photos')

def api_get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:50]

def get_sheet_data():
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/A1:Z300?key={API_KEY}'
    data = api_get(url)
    rows = data.get('values', [])
    # Find header row (row with 'name_place')
    header_idx = next((i for i, r in enumerate(rows) if 'name_place' in r), None)
    if header_idx is None:
        raise ValueError('Header row not found')
    headers = rows[header_idx]
    result = []
    for row in rows[header_idx + 1:]:
        if not row or not any(row):
            continue
        # Pad row to header length
        while len(row) < len(headers):
            row.append('')
        result.append(dict(zip(headers, row)))
    print(f'Sheet: {len(result)} data rows')
    return result

def get_drive_folder_files(folder_id):
    url = (f'https://www.googleapis.com/drive/v3/files'
           f'?q=%22{folder_id}%22+in+parents+and+trashed%3Dfalse'
           f'&fields=files(id,name,mimeType)'
           f'&key={API_KEY}')
    data = api_get(url)
    return [f for f in data.get('files', []) if f['mimeType'].startswith('image/')]

def download_photo(file_id, dest_path):
    url = f'https://drive.google.com/uc?export=download&id={file_id}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'image/*'
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            content = r.read()
            if len(content) < 1000:  # probably an HTML error page
                return False
            dest_path.write_bytes(content)
            return True
    except Exception as e:
        print(f'  Download error: {e}')
        return False

def extract_folder_id(url):
    # https://drive.google.com/drive/folders/FOLDER_ID
    m = re.search(r'/folders/([a-zA-Z0-9_-]+)', url or '')
    return m.group(1) if m else None

def parse_coords(coords_str):
    """Parse '50.45143, 30.509558' -> (lat, lng)"""
    try:
        parts = coords_str.replace(' ', '').split(',')
        return float(parts[0]), float(parts[1])
    except:
        return None, None

def parse_rating(val):
    try:
        return float(val)
    except:
        return 0.0

def parse_date(val):
    for fmt in ['%d,%m,%Y', '%d.%m.%Y', '%Y-%m-%d']:
        try:
            return datetime.strptime(val.strip(), fmt)
        except:
            continue
    return None

def main():
    print(f'=== Import start (dry_run={DRY_RUN}, skip_photos={SKIP_PHOTOS}) ===')
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

    rows = get_sheet_data()

    places_created = 0
    borsches_created = 0
    photos_downloaded = 0
    errors = []

    # Group by place name to avoid duplicates
    place_cache = {}

    for i, row in enumerate(rows):
        place_name = row.get('name_place', '').strip()
        borsch_name = row.get('name_borsch', '').strip()

        if not place_name or not borsch_name:
            continue

        # --- Place ---
        if place_name not in place_cache:
            lat, lng = parse_coords(row.get('location(lat,lng)', ''))
            place_data = dict(
                name=place_name,
                address=row.get('adress', '').strip(),
                latitude=lat,
                longitude=lng,
                country=row.get('country', '').strip(),
                city=row.get('city', '').strip(),
                type=row.get('type', '').strip(),
            )
            if not DRY_RUN:
                place, created = Place.objects.get_or_create(
                    name=place_name,
                    defaults=place_data
                )
                if created:
                    places_created += 1
                    print(f'[+] Place: {place_name}')
                place_cache[place_name] = place
            else:
                print(f'[DRY] Place: {place_name} lat={lat} lng={lng}')
                place_cache[place_name] = None

        place = place_cache[place_name]

        # --- Photos ---
        photo_urls_field = []
        if not SKIP_PHOTOS:
            folder_id = extract_folder_id(row.get('photo_urls', ''))
            if folder_id:
                try:
                    files = get_drive_folder_files(folder_id)
                    if files:
                        slug = slugify(place_name + '-' + borsch_name)
                        photo_dir = PHOTOS_DIR / slug
                        if not DRY_RUN:
                            photo_dir.mkdir(parents=True, exist_ok=True)
                        for img in files[:5]:  # max 5 photos per borsch
                            ext = img['name'].rsplit('.', 1)[-1].lower() if '.' in img['name'] else 'jpg'
                            dest = photo_dir / f"{img['id']}.{ext}"
                            if DRY_RUN:
                                photo_urls_field.append(f'/photos/{slug}/{img["id"]}.{ext}')
                                print(f'  [DRY] Photo: {img["name"]}')
                            elif dest.exists():
                                photo_urls_field.append(f'/photos/{slug}/{dest.name}')
                            else:
                                ok = download_photo(img['id'], dest)
                                if ok:
                                    photo_urls_field.append(f'/photos/{slug}/{dest.name}')
                                    photos_downloaded += 1
                                    print(f'  [photo] {dest.name}')
                                else:
                                    errors.append(f'Photo download failed: {img["name"]} for {borsch_name}')
                        time.sleep(0.3)  # rate limit
                except Exception as e:
                    errors.append(f'Drive error for {borsch_name}: {e}')

        # --- Borsch ---
        type_meat_raw = row.get('type_meat', '').strip()
        type_meat_map = {
            'яловичина': 'beef', 'яловичини': 'beef',
            'свинина': 'pork', 'свинини': 'pork',
            'курка': 'chicken', 'куриця': 'chicken', 'курятина': 'chicken',
            'без м\'яса': 'no_meat', '-': 'no_meat', '': 'no_meat',
        }
        type_meat = type_meat_map.get(type_meat_raw.lower(), 'other')

        def parse_price(val):
            try:
                return float(str(val).replace(',', '.')) or None
            except:
                return None

        borsch_data = dict(
            name=borsch_name,
            type_meat=type_meat,
            price=parse_price(row.get('price', '')),
            grams=(lambda v: int(float(v.replace(',','.'))) if v and v not in ['-','—',''] else None)(str(row.get('weight','') or '')),
            extras=row.get('додатково', '').strip(),
            dish_features=row.get('особливості', '').strip(),
            date=parse_date(row.get('дата', '')),
            photo_urls=photo_urls_field,
        )

        rating_data = dict(
            rating_salt=parse_rating(row.get('rating_salt', 0)),
            rating_meat=parse_rating(row.get('rating_meat', 0)),
            rating_beet=parse_rating(row.get('rating_beet', 0)),
            rating_density=parse_rating(row.get('rating_density', 0)),
            rating_aftertaste=parse_rating(row.get('rating_aftertaste', 0)),
            rating_serving=parse_rating(row.get('rating_serving', 0)),
            overall_rating=parse_rating(row.get('overall_rating', 0)),
        )

        if DRY_RUN:
            print(f'[DRY] Borsch: {borsch_name} | meat={type_meat} | photos={len(photo_urls_field)}')
        else:
            borsch, created = Borsch.objects.get_or_create(
                name=borsch_name,
                place=place,
                defaults=borsch_data
            )
            if created:
                borsches_created += 1
                print(f'  [+] Borsch: {borsch_name}')
                # Create rating
                Rating.objects.create(borschi=borsch, **rating_data)
            elif photo_urls_field:
                # Update photos if we got them
                borsch.photo_urls = photo_urls_field
                borsch.save(update_fields=['photo_urls'])

    print(f'\n=== Done ===')
    print(f'Places created: {places_created}')
    print(f'Borsches created: {borsches_created}')
    print(f'Photos downloaded: {photos_downloaded}')
    if errors:
        print(f'Errors ({len(errors)}):')
        for e in errors[:10]:
            print(f'  - {e}')

if __name__ == '__main__':
    main()
