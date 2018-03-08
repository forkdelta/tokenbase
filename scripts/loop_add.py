from subprocess import call
import yaml
import sys

from token_info import main as token_info_main

with open(sys.argv[1]) as f:
    tokens_to_add = [l.strip().split(',') for l in f.readlines()]

for (token_addr, website_url, issue_number) in tokens_to_add:
    token_addr = token_addr.lower()
    outfile = "tokens/{}.yaml".format(token_addr)

    token_yaml = token_info_main(token_addr, website_url)
    with open(outfile, "w") as f:
        f.write(token_yaml)

    with open(outfile) as f:
        token_info = yaml.safe_load(f.read())

    commit_msg = "List {symbol} {name}\n\nhttps://etherscan.io/token/{addr}\nCloses #{issue_number}".format(**token_info, issue_number=issue_number)
    call(["git", "add", outfile])
    call(["git", "commit", "-m", commit_msg, "--", outfile])
