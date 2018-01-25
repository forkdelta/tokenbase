from utils import *
import sys
import yaml
from yaml_utils import *

LISTINGS = get_forkdelta_listings()

DEFAULT_LINK_FIELDS = frozenset((
    "Website", "Blog", "Whitepaper",
    "Twitter", "Telegram", "Reddit"))

def main():
    if len(sys.argv) >= 2:
        addr = sys.argv[1].lower()
        if len(sys.argv) == 3:
            website = sys.argv[2]
        else:
            website = None
    else:
        print("Usage: script.py <token address> [website url]")
        exit(1)

    addr = addr.lower()
    # Gather info
    info = get_token_info(addr)

    etherscan_doc = get_etherscan_token_page(addr)

    links = [entry.split(": ") for entry in get_etherscan_contact_info(addr, html_doc=etherscan_doc)]
    if website and not dict(links).get("Website"):
        links += [("Website", website)]

    notice = get_etherscan_notice(addr, html_doc=etherscan_doc)

    addr_filter = lambda listing: listing["addr"] == addr
    existing_listing = next(filter(addr_filter, LISTINGS), None)
    if existing_listing:
        print("already on forkdelta", existing_listing)
        token_guide = get_forkdelta_guide(existing_listing["name"])
        guide_website = get_fd_token_website(token_guide)
        if guide_website and dict(links).get("Website") != guide_website:
            links.append(("Website", guide_website))
        guide_description = get_fd_token_description(token_guide)
    else:
        guide_description = None

    metas = []
    website = dict(links).get("Website", website)
    if website:
        website_doc = get_website(website)
        metas = get_website_metas(website, website_doc)
        links += get_website_links(website, website_doc)

    # Build a listing
    listing = dict(addr=addr, decimals=int(info["decimals"]))
    listing.update({ k: info.get(k, "") for k in ("name", "symbol") })

    if existing_listing:
        if not listing["symbol"]:
            listing["symbol"] = existing_listing["name"]
        elif listing["symbol"] != existing_listing["name"]:
            listing["WARNING_MISMATCHING_FORKDELTA_SYMBOL"] = existing_listing["name"]

    if notice is not None:
        listing["notice"] = LiteralString(notice)


    # Get a set of unique links
    links = [(k, v) for (v, k) in dict(((v, k) for (k, v) in links)).items()]
    links = sorted(links, key=lambda p: p[0])

    link_fields = set((entry[0] for entry in links))
    missing_link_fields = DEFAULT_LINK_FIELDS - link_fields
    placeholder_links = [(field, "ADD OR DELETE LINE") for field in missing_link_fields]

    listing.update({ "links": [{entry[0]: entry[1]} for entry in links + placeholder_links] })

    description = ""
    description_meta_filter = lambda e: e[0] in ("description", "og:description")
    if any(filter(description_meta_filter, metas)):
        # Use ljust below to keep YAML from getting double new-lines
        description = comment_line("The following options were found")
        description += comment_line("You may need to edit them and you MUST delete commented lines")
        for (meta_name, meta_content) in filter(description_meta_filter, metas):
            if meta_content:
                description += comment_line("From the website: {} meta tag".format(meta_name))
                description += meta_content.strip()
                description += "\n"

    if guide_description:
        if not description:
            description = comment_line("The following options were found")
            description += comment_line("You may need to edit them and you MUST delete commented lines")
        description += comment_line("From the existing ForkDelta token guide")
        description += guide_description + "\n"

    if not description:
        description = "FILL ME IN"

    listing.update({ "description": LiteralString(description.strip()) })

    print(yaml.dump(listing, default_flow_style=False, explicit_start=True, width=YAML_WIDTH, indent=YAML_INDENT, allow_unicode=True))

main()
