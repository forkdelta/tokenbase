import json
from os import listdir, path
import yaml

def main():
    tokens_dir = "tokens"
    token_file_filter = lambda fname: fname.startswith("0x") and fname.endswith(".yaml")

    all_tokens = {}
    for defn_fname in sorted(map(lambda s: s.lower(), filter(token_file_filter, listdir(tokens_dir)))):
        with open(path.join(tokens_dir, defn_fname), encoding="utf8") as f:
            defn = yaml.safe_load(f)

        all_tokens[defn["addr"]] = defn

    with open("tokens/index.json", "w", encoding="utf8") as outfile:
        json.dump(all_tokens, outfile, separators=(',', ':'))

if __name__ == "__main__":
    main()
