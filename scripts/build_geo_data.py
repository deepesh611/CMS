#!/usr/bin/env python3
"""Build geo_data.json for India + Oman from real postal / admin sources.

Sources (in tmp/geo_raw/):
  India:
    - GeoNames postal dump IN.txt (download.geonames.org/export/zip/IN.zip)
  Oman:
    - open-admin-data/oman-administrative-divisions
    - GeoNames OM place dump
    - Oman Post 3-digit codes (curated)

Run from repo root:
  python scripts/build_geo_data.py
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "tmp" / "geo_raw"
OUT = ROOT / "app" / "static" / "data" / "geo_data.json"

COUNTRIES = ["India", "Oman"]
OMAN = "Oman"
INDIA = "India"

# ---------------------------------------------------------------------------
# Oman Post published place → 3-digit codes (governorate, preferred wilayat)
# ---------------------------------------------------------------------------
OMAN_POSTAL: list[tuple[str, str, str, str]] = [
    # (governorate, wilayat, area, postcode)
    # Muscat
    ("Muscat", "Muscat", "Hai Al Mina", "100"),
    ("Muscat", "Muscat", "Muscat", "100"),
    ("Muscat", "Bausher", "Airport Heights", "111"),
    ("Muscat", "Muttrah", "Ruwi", "112"),
    ("Muscat", "Muttrah", "Hai Al Mina", "114"),
    ("Muscat", "Muscat", "Mina Al Fahal", "116"),
    ("Muscat", "Muttrah", "Wadi Kabir", "117"),
    ("Muscat", "Muttrah", "Al Wadi Al Kabir", "117"),
    ("Muscat", "Muscat", "Al Amarat", "119"),
    ("Muscat", "Muscat", "Al Amerat", "119"),
    ("Muscat", "Quriyat", "Qurayyat", "120"),
    ("Muscat", "A Seeb", "Seeb", "121"),
    ("Muscat", "A Seeb", "Al Seeb", "121"),
    ("Muscat", "A Seeb", "Maabilah", "122"),
    ("Muscat", "A Seeb", "Al Khoud", "123"),
    ("Muscat", "A Seeb", "Sultan Qaboos University", "123"),
    ("Muscat", "A Seeb", "Rusail", "124"),
    ("Muscat", "Bausher", "Al Athaiba", "130"),
    ("Muscat", "Bausher", "Azaiba", "130"),
    ("Muscat", "A Seeb", "Al Khoud", "132"),
    ("Muscat", "Bausher", "Al Khuwair", "133"),
    ("Muscat", "Bausher", "Shati Al Qurum", "134"),
    ("Muscat", "Bausher", "Qurum", "134"),
    ("Muscat", "Bausher", "Al Qurm", "134"),
    ("Muscat", "A Seeb", "Al Mouj", "138"),
    ("Muscat", "A Seeb", "The Wave", "138"),
    ("Muscat", "Bausher", "Al Ansab", "142"),
    ("Muscat", "A Seeb", "Al Hail", "143"),
    ("Muscat", "Muttrah", "Wadi Kabir", "144"),
    ("Muscat", "Muscat", "Al Amerat", "145"),
    ("Muscat", "Bausher", "Al Ghubra", "146"),
    ("Muscat", "Bausher", "Al Ghubrah", "146"),
    ("Muscat", "Bausher", "Ghubrah", "146"),
    ("Muscat", "Bausher", "Ghubra", "146"),
    ("Muscat", "A Seeb", "Al Khoud 7", "147"),
    ("Muscat", "A Seeb", "Al Khoud Souq", "148"),
    ("Muscat", "A Seeb", "Al Maabilah Nesto", "149"),
    ("Muscat", "A Seeb", "Al Maabilah Sinaiyah", "150"),
    ("Muscat", "Quriyat", "Qurayyat", "151"),
    ("Muscat", "Bausher", "Nawras Commercial Centre", "152"),
    ("Muscat", "A Seeb", "Mawaleh", "160"),
    ("Muscat", "A Seeb", "Al Mawalih", "160"),
    ("Muscat", "A Seeb", "Al Hail Square", "167"),
    ("Muscat", "Muttrah", "Ruwi", "168"),
    ("Muscat", "Muttrah", "Muttrah", "169"),
    ("Muscat", "Muttrah", "Mutrah", "169"),
    ("Muscat", "Muscat", "Al Amerat", "170"),
    ("Muscat", "A Seeb", "Maabilah", "171"),
    ("Muscat", "Bausher", "MBD Area", "172"),
    ("Muscat", "Bausher", "Liwan Al Ghubra", "157"),
    ("Muscat", "Bausher", "Ghala", "178"),
    ("Muscat", "Bausher", "Madinat Sultan Qaboos", "133"),
    ("Muscat", "Bausher", "Madinat Qaboos", "133"),
    ("Muscat", "Bausher", "Wattayah", "112"),
    ("Muscat", "Bausher", "Al Sarooj", "133"),
    ("Muscat", "Bausher", "Dolphin Village", "146"),
    # Dhofar
    ("Dhofar", "Salalah", "Salalah CPO", "211"),
    ("Dhofar", "Salalah", "Dahariz", "214"),
    ("Dhofar", "Salalah", "Al Awqadain", "217"),
    ("Dhofar", "Thumrait", "Thamrait", "222"),
    ("Dhofar", "Salalah", "Al Saada", "225"),
    ("Dhofar", "Salalah", "Salalah", "226"),
    ("Dhofar", "Salalah", "Awqad", "231"),
    ("Dhofar", "Mirbat", "Mirbat", "232"),
    ("Dhofar", "Taqah", "Taqa", "236"),
    ("Dhofar", "Rakhyut", "Rakhyut", "237"),
    ("Dhofar", "Thumrait", "Thumrait", "230"),
    # Al Batinah
    ("Al Batinah North", "Sohar", "Sohar", "311"),
    ("Al Batinah North", "Sohar", "Suhar", "311"),
    ("Al Batinah South", "Al Musannah", "Muladdah", "314"),
    ("Al Batinah North", "As Suwayq", "Al Suwaiq", "315"),
    ("Al Batinah North", "Saham", "Saham", "319"),
    ("Al Batinah South", "Barka", "Barka", "320"),
    ("Al Batinah North", "Liwa", "Liwa", "325"),
    ("Al Batinah North", "Al Khaburah", "Al Khaboura", "326"),
    ("Al Batinah South", "Nakhal", "Nakhal", "332"),
    ("Al Batinah South", "Al Awabi", "Al Awabi", "336"),
    ("Al Batinah South", "Ar Rustaq", "Rustaq", "338"),
    ("Al Batinah North", "Shinas", "Shinas", "324"),
    # Ad Dakhiliyah
    ("Ad Dakhiliyah", "Bidbid", "Bidbid", "600"),
    ("Ad Dakhiliyah", "Nizwa", "Nizwa", "611"),
    ("Ad Dakhiliyah", "Bahla", "Bahla", "612"),
    ("Ad Dakhiliyah", "Izki", "Izki", "614"),
    ("Ad Dakhiliyah", "Al Hamra", "Al Hamra", "617"),
    ("Ad Dakhiliyah", "Adam", "Adam", "618"),
    ("Ad Dakhiliyah", "Manah", "Manah", "619"),
    ("Ad Dakhiliyah", "Samail", "Samail", "620"),
    # Ad Dhahirah / Buraimi
    ("Ad Dhahirah", "Yanqul", "Yanqul", "500"),
    ("Ad Dhahirah", "Ibri", "Ibri", "511"),
    ("Al Buraimi", "Al Buraimi", "Al Buraimi", "512"),
    ("Al Buraimi", "Al Buraimi", "Buraimi", "524"),
    ("Al Buraimi", "Mahdah", "Mahda", "526"),
    # Sharqiyah
    ("Ash Sharqiyah North", "Ibra", "Ibra", "400"),
    ("Ash Sharqiyah South", "Sur", "Sur", "411"),
    ("Ash Sharqiyah South", "Al Kamil Wal Wafi", "Al Kamil Wal Wafi", "412"),
    ("Ash Sharqiyah South", "Masirah", "Masirah", "414"),
    ("Ash Sharqiyah South", "Jalan Bani Bu Hassan", "Jalan Bani Bu Hassan", "415"),
    ("Ash Sharqiyah South", "Jaalan Bani Bu Ali", "Jalan Bani Bu Ali", "416"),
    ("Ash Sharqiyah North", "Al Mudhaibi", "Al Mudhaibi", "420"),
    # Al Wusta
    ("Al Wusta", "Duqm", "Duqm", "700"),
    ("Al Wusta", "Haima", "Haima", "714"),
    # Musandam
    ("Musandam", "Diba", "Daba", "800"),
    ("Musandam", "Khasab", "Khasab", "811"),
    ("Musandam", "Madha", "Madha", "814"),
    ("Musandam", "Bukha", "Bukha", "816"),
]

# Extra well-known Muscat neighborhoods (attached even if missing from dumps)
MUSCAT_AREAS: dict[str, list[str]] = {
    "Bausher": [
        "Al Ghubra",
        "Al Ghubrah",
        "Ghubrah",
        "Ghubra",
        "Al Ghubrah South",
        "Al Ghubrah North",
        "Al Khuwair",
        "Al Khuwair South",
        "Al Khuwair North",
        "Qurum",
        "Al Qurm",
        "Shati Al Qurum",
        "Madinat Sultan Qaboos",
        "Madinat Qaboos",
        "Ghala",
        "Al Athaiba",
        "Azaiba",
        "Al Ansab",
        "Wattayah",
        "Al Sarooj",
        "Dolphin Village",
        "MBD Area",
        "Bausher",
        "Bousher",
    ],
    "A Seeb": [
        "Seeb",
        "Al Seeb",
        "Al Khoud",
        "Al Khoudh",
        "Maabilah",
        "Al Maabilah",
        "Al Hail",
        "Al Hail South",
        "Al Hail North",
        "Mawaleh",
        "Al Mawalih",
        "Al Mouj",
        "The Wave",
        "Rusail",
        "Sultan Qaboos University",
        "Mabella",
    ],
    "Muttrah": [
        "Muttrah",
        "Mutrah",
        "Ruwi",
        "Wadi Kabir",
        "Al Wadi Al Kabir",
        "Darsait",
        "Sidab",
        "Kalbooh",
        "Hai Al Mina",
    ],
    "Muscat": [
        "Muscat",
        "Old Muscat",
        "Al Amarat",
        "Al Amerat",
        "Mina Al Fahal",
        "Airport Heights",
        "Qurum Natural Park",
    ],
    "Quriyat": ["Qurayyat", "Quriyat", "Quryat"],
}


# Canonical English governorate names
GOV_CANON = {
    "ad dakhliyah": "Ad Dakhiliyah",
    "ad dakhiliyah": "Ad Dakhiliyah",
    "ad dhahirah": "Ad Dhahirah",
    "al dhahira": "Ad Dhahirah",
    "al dhahirah": "Ad Dhahirah",
    "al buraimi": "Al Buraimi",
    "al buraymi": "Al Buraimi",
    "al wusta": "Al Wusta",
    "al wusta governorate": "Al Wusta",
    "musandam": "Musandam",
    "musandam governorate": "Musandam",
    "southeastern governorate": "Ash Sharqiyah South",
    "northeastern governorate": "Ash Sharqiyah North",
    "ash sharqiyah south": "Ash Sharqiyah South",
    "ash sharqiyah north": "Ash Sharqiyah North",
    "al batinah north": "Al Batinah North",
    "al batinah south": "Al Batinah South",
    "dhofar": "Dhofar",
    "muscat": "Muscat",
}


def canon_gov(name: str) -> str:
    name = clean(name)
    return GOV_CANON.get(name.casefold(), name)


def fold(text: str) -> str:
    """Strip combining marks so 'Ghubrah' matches 'Ghubrah' with diacritics."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text


def clean(name: str) -> str:
    name = fold(name)
    name = re.sub(r"\s+", " ", (name or "").strip())
    name = re.sub(r"\s+Dist\.?$", "", name, flags=re.I).strip()
    name = re.sub(r"\s+Governorate$", "", name, flags=re.I).strip()
    return name


def sorted_unique(values) -> list[str]:
    # Prefer ASCII-looking labels; keep stable case-insensitive order
    seen = {}
    for v in values:
        if not v:
            continue
        key = v.casefold()
        # Prefer spellings without uncommon characters
        if key not in seen or sum(1 for c in v if ord(c) > 127) < sum(
            1 for c in seen[key] if ord(c) > 127
        ):
            seen[key] = v
    return sorted(seen.values(), key=lambda s: s.casefold())


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_india() -> dict:
    """India from GeoNames postal dump — state → district → city → locality → suburb + PIN."""
    path = RAW / "geo_IN" / "IN.txt"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Download https://download.geonames.org/export/zip/IN.zip"
        )

    bad = {"NA", "N/A", "NULL", "-"}
    states: set[str] = set()
    districts: dict[str, set[str]] = defaultdict(set)
    cities: dict[str, set[str]] = defaultdict(set)
    localities: dict[str, set[str]] = defaultdict(set)
    suburbs: dict[str, set[str]] = defaultdict(set)
    postal_index: dict[str, list] = {}

    with path.open(encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 8:
                continue
            pin = p[1].strip()
            place = clean(p[2])
            state = clean(p[3])
            district = clean(p[5])
            community = clean(p[7])

            if not (pin and place and state and district):
                continue
            if district.upper() in bad or place.upper() in bad:
                continue

            city = community if community and community.upper() not in bad else district
            locality = city
            suburb = place

            states.add(state)
            districts[state].add(district)
            cities[f"{INDIA}|{state}|{district}"].add(city)
            localities[f"{INDIA}|{state}|{district}|{city}"].add(locality)
            suburbs[f"{INDIA}|{state}|{district}|{city}|{locality}"].add(suburb)

            hit = [state, district, city, suburb]
            bucket = postal_index.setdefault(pin, [])
            if hit not in bucket:
                bucket.append(hit)

    return {
        "states": sorted_unique(states),
        "districts": {f"{INDIA}|{s}": sorted_unique(districts[s]) for s in states},
        "cities": {k: sorted_unique(v) for k, v in cities.items()},
        "localities": {k: sorted_unique(v) for k, v in localities.items()},
        "suburbs": {k: sorted_unique(v) for k, v in suburbs.items()},
        "postal_index": postal_index,
    }


def build_oman() -> dict:
    admin_dir = RAW / "oman_admin"
    govs = load_json(admin_dir / "all-governorate.json")
    wils = load_json(admin_dir / "all-wilayat.json")
    vils = load_json(admin_dir / "all-village.json")

    gov_by_id = {g["id"]: canon_gov(g["name"]["en"]) for g in govs}
    wil_by_id = {}
    for w in wils:
        wil_by_id[w["id"]] = {
            "name": clean(w["name"]["en"]),
            "gov_id": w["parent"]["id"],
            "gov": canon_gov(w["parent"]["name"]["en"]),
        }

    states: set[str] = set(gov_by_id.values())
    cities: dict[str, set[str]] = defaultdict(set)
    localities: dict[str, set[str]] = defaultdict(set)
    suburbs: dict[str, set[str]] = defaultdict(set)
    postal_index: dict[str, list] = {}

    def add_area(gov: str, wilayat: str, area: str):
        gov, wilayat, area = canon_gov(gov), clean(wilayat), clean(area)
        if not (gov and wilayat and area):
            return
        states.add(gov)
        cities[f"{OMAN}|{gov}"].add(wilayat)
        localities[f"{OMAN}|{gov}|{wilayat}"].add(area)
        suburbs[f"{OMAN}|{gov}|{wilayat}|{area}"].add(area)

    def add_postal(code: str, gov: str, wilayat: str, area: str):
        code = str(code).strip()
        if not code:
            return
        hit = [canon_gov(gov), "", clean(wilayat), clean(area)]
        bucket = postal_index.setdefault(code, [])
        if hit not in bucket:
            bucket.append(hit)

    for w in wils:
        info = wil_by_id[w["id"]]
        add_area(info["gov"], info["name"], info["name"])

    for v in vils:
        area = clean(v["name"]["en"])
        parent = v.get("parent") or {}
        wil_id = parent.get("id")
        if not wil_id or wil_id not in wil_by_id:
            continue
        info = wil_by_id[wil_id]
        add_area(info["gov"], info["name"], area)

    for wilayat, areas in MUSCAT_AREAS.items():
        for area in areas:
            add_area("Muscat", wilayat, area)

    admin1 = {}
    with (RAW / "admin1CodesASCII.txt").open(encoding="utf-8") as f:
        for line in f:
            p = line.split("\t")
            if p[0].startswith("OM."):
                admin1[p[0].split(".", 1)[1]] = canon_gov(p[1])

    wilayat_names_by_gov: dict[str, list[str]] = defaultdict(list)
    for info in wil_by_id.values():
        wilayat_names_by_gov[info["gov"]].append(info["name"])

    known_areas_by_gov_wil: dict[tuple[str, str], set[str]] = defaultdict(set)
    for key, areas in localities.items():
        parts = key.split("|")
        if len(parts) == 3:
            known_areas_by_gov_wil[(parts[1], parts[2])].update(areas)

    def match_wilayat(gov: str, place: str) -> str | None:
        place_l = place.casefold()
        for wname in wilayat_names_by_gov.get(gov, []):
            wl = wname.casefold()
            if wl == place_l or wl in place_l or place_l in wl:
                return wname
        for wname in wilayat_names_by_gov.get(gov, []):
            for area in known_areas_by_gov_wil.get((gov, wname), []):
                al = area.casefold()
                if al == place_l or al in place_l or place_l in al:
                    return wname
        if gov == "Muscat":
            for wname, areas in MUSCAT_AREAS.items():
                for a in areas:
                    al = a.casefold()
                    if al == place_l or al in place_l or place_l in al:
                        return wname
        return None

    dump = RAW / "dump_OM" / "OM.txt"
    keep = {"PPLC", "PPLA", "PPLA2", "PPLA3", "PPL", "PPLX", "PPLL"}
    with dump.open(encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 15 or p[6] != "P" or p[7] not in keep:
                continue
            name = clean(p[1]) or clean(p[2])
            if not name:
                continue
            a1 = p[10].strip()
            gov = canon_gov(admin1.get(a1, ""))
            if not gov:
                continue
            wilayat = match_wilayat(gov, name)
            if not wilayat:
                continue
            alts = [name]
            for alt in (p[3] or "").split(","):
                alt = clean(alt)
                if alt and re.search(r"[A-Za-z]", alt):
                    alts.append(alt)
            for area in alts:
                add_area(gov, wilayat, area)

    for gov, wilayat, area, code in OMAN_POSTAL:
        add_area(gov, wilayat, area)
        add_postal(code, gov, wilayat, area)

    return {
        "states": sorted_unique(states),
        "districts": {},
        "cities": {k: sorted_unique(v) for k, v in cities.items()},
        "localities": {k: sorted_unique(v) for k, v in localities.items()},
        "suburbs": {k: sorted_unique(v) for k, v in suburbs.items()},
        "postal_index": postal_index,
    }


def build() -> dict:
    print("Building India…")
    india = build_india()
    print("Building Oman…")
    oman = build_oman()

    out = {
        "has_districts": [INDIA],
        "countries": list(COUNTRIES),
        "states": {
            INDIA: india["states"],
            OMAN: oman["states"],
        },
        "districts": india["districts"],
        "cities": {},
        "localities": {},
        "suburbs": {},
        "postal_index": {
            INDIA: india["postal_index"],
            OMAN: oman["postal_index"],
        },
        "meta": {
            "countries": list(COUNTRIES),
            "sources": [
                "GeoNames postal dump IN (download.geonames.org/export/zip/IN.zip)",
                "open-admin-data/oman-administrative-divisions",
                "GeoNames OM place dump",
                "Oman Post published 3-digit postcodes",
            ],
        },
    }
    for part in (india, oman):
        out["cities"].update(part["cities"])
        out["localities"].update(part["localities"])
        out["suburbs"].update(part["suburbs"])
    return out


def main() -> None:
    out = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    size_mb = OUT.stat().st_size / 1e6
    print(f"Wrote {OUT} ({size_mb:.2f} MB)")
    for c in COUNTRIES:
        n_states = len(out["states"][c])
        n_pins = len(out["postal_index"][c])
        n_cities = sum(1 for k in out["cities"] if k.startswith(c + "|"))
        print(f"  {c}: states={n_states} cityKeys={n_cities} pins={n_pins}")
    print("India 400053 ->", out["postal_index"][INDIA].get("400053", [])[:2])
    print("Oman 146 ->", out["postal_index"][OMAN].get("146", [])[:2])
    bausher = out["localities"].get(f"{OMAN}|Muscat|Bausher", [])
    print("Al Ghubra present:", any("ghubra" in x.casefold() for x in bausher))


if __name__ == "__main__":
    main()
