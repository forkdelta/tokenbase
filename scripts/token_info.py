from requests.exceptions import ConnectionError, TooManyRedirects
import sys
from utils import *
import yaml
from yaml_utils import *

LISTINGS = get_forkdelta_listings()

DEFAULT_LINK_FIELDS = frozenset((
    "Website", "Bitcointalk", "Blog", "Whitepaper",
    "Twitter", "Telegram", "Reddit"))

def main(addr, website=None, parse_website=True, guide_mode=True):
    addr = addr.lower()
    # Gather info
    try:
        info = get_token_info(addr)
    except:
        print("# ERROR fetching information from Ethplorer")
        info = {}


    etherscan_doc = get_etherscan_token_page(addr)

    links = [entry.split(": ") for entry in get_etherscan_contact_info(addr, html_doc=etherscan_doc)]
    if website and not dict(links).get("Website"):
        links += [("Website", website)]

    notice = get_etherscan_notice(addr, html_doc=etherscan_doc)

    addr_filter = lambda listing: listing["addr"].lower() == addr.lower()
    existing_listing = next(filter(addr_filter, LISTINGS), None)
    if existing_listing:
        token_guide = get_forkdelta_guide(existing_listing["name"])
        guide_website = get_fd_token_website(token_guide)
        if guide_website and dict(links).get("Website") != guide_website:
            links.append(("Website", guide_website))
        guide_description = get_fd_token_description(token_guide)
    else:
        guide_description = None

    metas = []
    website = dict(links).get("Website", website)
    if website and parse_website:
        try:
            website_doc = get_website(website)
            metas = get_website_metas(website, website_doc)
            links += get_website_links(website, website_doc)
        except (ConnectionError, TooManyRedirects):
            print("Failed to fetch {} listed on {}".format(website, addr))


    # Build a listing
    listing = dict(addr=addr, decimals=int(info.get("decimals", -1)))
    listing.update({ k: info.get(k, "") for k in ("name", "symbol") })

    if existing_listing:
        if not listing["symbol"]:
            listing["symbol"] = existing_listing["name"]
        elif listing["symbol"] and listing["symbol"] != existing_listing["name"]:
            listing["__FORKDELTA_CUSTOM_SYMBOL"] = existing_listing["name"]

    if notice is not None:
        listing["notice"] = LiteralString(notice)


    # Get a set of unique links
    links = [(k, v) for (v, k) in dict(((v, k) for (k, v) in links)).items()]
    links = sorted(links, key=lambda p: p[0])

    if guide_mode:
        link_fields = set((entry[0] for entry in links))
        missing_link_fields = DEFAULT_LINK_FIELDS - link_fields
        placeholder_links = [(field, "ADD OR DELETE LINE") for field in missing_link_fields]
    else:
        placeholder_links = []

    listing.update({ "links": [{entry[0]: entry[1]} for entry in links + placeholder_links] })

    description = ""
    description_meta_filter = lambda e: e[0] in ("description", "og:description")
    if any(filter(description_meta_filter, metas)):
        # Use ljust below to keep YAML from getting double new-lines
        if guide_mode:
            description += comment_line("The following options were found")
            description += comment_line("You may need to edit them and you MUST delete commented lines")
        for (meta_name, meta_content) in filter(description_meta_filter, metas):
            if meta_content:
                description += comment_line("From the website: {} meta tag".format(meta_name))
                description += meta_content.strip()
                description += "\n"

    if guide_description:
        if guide_mode:
            if not description:
                description += comment_line("The following options were found")
                description += comment_line("You may need to edit them and you MUST delete commented lines")
            description += comment_line("From the existing ForkDelta token guide")
        description += guide_description + "\n"

    if guide_mode and not description:
        description = "FILL ME IN"

    listing.update({ "description": LiteralString(description.strip()) })

    return yaml.dump(listing, default_flow_style=False, explicit_start=True, width=YAML_WIDTH, indent=YAML_INDENT, allow_unicode=True)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        print(main(sys.argv[1], sys.argv[2]))
    elif len(sys.argv) == 2:
        print(main(sys.argv[1]))
    else:
        print("Usage: script.py <token address> [website url]")
        exit(1)
