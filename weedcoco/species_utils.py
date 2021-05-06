import zipfile
from collections import defaultdict
import datetime
import requests
import io
import os
from xml.etree import ElementTree

# This uses data from https://data.eppo.int/ in accordance with
# the EPPO Codes Open Data Licence (https://data.eppo.int/media/Open_Licence.pdf)

# TODO: get non-taxonomic group membership for a list of all crop species (3CRGK), for instance


SOURCE_URL = "https://data.eppo.int/files/xmlfull.zip"
DEFAULT_LANGUAGES = ("en",)
DEFAULT_TYPES = ("PFL", "SPT")


class EppoTaxonomy:
    SUFFIX_TO_LEVEL = {
        "C": "Class",
        "D": "Category",
        "F": "Family",
        "G": "Genus",
        "K": "Kingdom",
        "O": "Order",
        "P": "Phylum",
    }

    def __init__(
        self,
        path=None,
        cache=False,
        languages=DEFAULT_LANGUAGES,
        types=DEFAULT_TYPES,
    ):
        taxonomy = self._parse_xml(path, cache)
        self.version_date = datetime.datetime.strptime(
            taxonomy.getroot().attrib["dateexport"], "%Y-%m-%dT%H:%M:%S%z"
        )
        self.entries = self._extract_entries(taxonomy, languages=languages, types=types)
        children = self._extract_children(self.entries)
        self.root_codes = []
        for parent, child_codes in children.items():
            try:
                self.entries[parent]["children"] = child_codes
            except KeyError:
                # TODO: log a warning? Can happen if parent is inactive, i.e. data glitch
                pass

        for root_code in children[None]:
            self._set_ancestors(root_code, [])

        self._by_preferred_name = {
            entry["preferred_name"].lower(): entry for entry in self.entries.values()
        }
        self._by_lang_name = defaultdict(list)
        for entry in self.entries.values():
            for lang in languages:
                for name in entry.get(lang + "_names", ()):
                    self._by_lang_name[lang, name.lower()].append(entry)
        self._by_lang_name.default_factory = None

    @staticmethod
    def _parse_xml(path, cache=False):
        # TODO: invalidate cache if URL is updated, or after specified period
        if cache:
            if path is None:
                raise ValueError("Path must be given if cache is enabled")
            if not os.path.isfile(path):
                cache_path = path
                path = None

        if path is None:
            resp = requests.get(SOURCE_URL)
            resp.raise_for_status()
            if cache:
                path = cache_path
                with open(path, "wb") as cache_file:
                    cache_file.write(resp.content)
            else:
                path = io.BytesIO(resp.content)
        if hasattr(path, "endswith") and path.endswith(".xml"):
            file = open(path)
        else:
            file = zipfile.ZipFile(path).open("fullcodes.xml")

        with file:
            root = ElementTree.parse(file)
        return root

    @staticmethod
    def _extract_entries(taxonomy, languages, types):
        entries = {}

        elems = []
        for typ in types:
            elems.extend(taxonomy.findall(f"./code[@isactive='true'][@type='{typ}']"))

        for code_elem in elems:
            code = code_elem.find("./eppocode").text
            parent_code = getattr(
                code_elem.find(".//parent[@linktype='taxo']"), "text", None
            )
            preferred_name_elem = code_elem.find(
                ".//name[@ispreferred='true'][@isactive='true']//fullname"
            )

            name_elems = code_elem.findall(
                ".//name[@isactive='true']"
            )  # XXX: can't get xpath filter on [//lang/*[text() = "en"]] working
            if preferred_name_elem is None:
                preferred_name = f"EPPO:{code} [no preferred name]"
            else:
                preferred_name = preferred_name_elem.text

            entry = {
                "code": code,
                "parent_code": parent_code,
                "level": "species" if code_elem.attrib["type"] == "PFL" else "group",
                "preferred_name": preferred_name,
            }
            for lang in languages:
                entry[lang + "_names"] = [
                    elem.find("./fullname").text
                    for elem in name_elems
                    if elem.find("./lang").text == lang and elem.find("./fullname").text
                ]
            entries[code] = entry

        return entries

    @staticmethod
    def _extract_children(entries):
        children = defaultdict(set)
        for entry in entries.values():
            children[entry["parent_code"]].add(entry["code"])
        children.default_factory = None
        return children

    def _set_ancestors(self, code, ancestors):
        entry = self.entries[code]
        entry["ancestors"] = ancestors
        path = [code] + ancestors
        entry = self.entries[code]
        if "children" not in entry:
            return
        for child_code in entry["children"]:
            self._set_ancestors(child_code, path)

    def lookup_preferred_name(self, name, species_only=False):
        out = self._by_preferred_name[name.lower()]
        if species_only and out["level"] != "species":
            raise KeyError(f"{repr(name)} is not a species")
        return out

    def lookup_unique_name(self, lang, name, species_only=False):
        out = self._by_lang_name[lang, name.lower()]
        if len(out) != 1:
            raise KeyError(f"{repr(name)} is not unique")
        out = out[0]
        if species_only and out["level"] != "species":
            raise KeyError(f"{repr(name)} is not a species")
        return out

    def lookup_name(self, lang, name, species_only=False):
        out = self._by_lang_name[lang, name.lower()]
        if species_only:
            out = [entry for entry in out if entry["level"] == "species"]
        return out


# Add FAMILY_SUFFIX etc
for suf, name in EppoTaxonomy.SUFFIX_TO_LEVEL.items():
    setattr(EppoTaxonomy, name.upper() + "_SUFFIX", suf)


_EPPO_SINGLETON = {}


def get_eppo_singleton(
    path=None, cache=True, languages=DEFAULT_LANGUAGES, types=DEFAULT_TYPES
):
    # Note: languages and types should be sorted tuples
    if (languages, types) not in _EPPO_SINGLETON:
        _EPPO_SINGLETON[languages, types] = EppoTaxonomy(
            path=path, cache=cache, languages=languages, types=types
        )
    return _EPPO_SINGLETON[languages, types]
