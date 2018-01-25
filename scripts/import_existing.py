from token_info import main as token_info_main
from utils import *
import sys
import yaml
from yaml_utils import *

LISTINGS = get_forkdelta_listings()

if __name__ == "__main__":
    for (idx, token) in enumerate(LISTINGS):
        print("Token", idx, "of", len(LISTINGS))
        addr = token["addr"].lower()

        if addr == "0x0000000000000000000000000000000000000000":
            continue

        try:
            yaml_content = token_info_main(addr, parse_website=False, guide_mode=False)
        except:
            print("ERROR IMPORTING {}".format(addr))
        else:
            with open("tokens/{}.yaml".format(addr), "w") as f:
                f.write(yaml_content)
