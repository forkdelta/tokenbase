from glob import glob
import json
import yaml


def read_entry(fn):
    with open(fn) as infile:
        return yaml.safe_load(infile)


INDEX_KEYS = ["addr", "decimals", "name", "symbol"]


def abridged_entry(entry):
    return {k: entry[k] for k in INDEX_KEYS}


def main():
    files = sorted(glob("tokens/0x*.yaml"))

    entries = list(read_entry(fn) for fn in files)
    for entry in entries:
        json_fn = "tokens/{}.json".format(entry["addr"])
        with open(json_fn, "w") as outfile:
            json.dump(entry, outfile, separators=(',', ':'))

    with open("tokens/bundle.json", "w") as outfile:
        json.dump(entries, outfile, separators=(',', ':'))

    with open("tokens/index.json", "w") as outfile:
        json.dump(
            list(abridged_entry(entry) for entry in entries),
            outfile,
            separators=(',', ':'))


if __name__ == "__main__":
    main()
