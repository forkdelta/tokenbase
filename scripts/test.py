#!/usr/bin/env python3

from eth_utils import is_hex_address
import json
from unittest import SkipTest
import sys
from web3 import Web3, HTTPProvider
import yaml

web3 = Web3(HTTPProvider("https://api.myetherapi.com/eth"))
with open("scripts/erc20.abi.json") as erc20_abi_f:
    ERC20_ABI = json.load(erc20_abi_f)

KNOWN_LINK_TYPES = frozenset((
    'Bitcointalk', 'Blog', 'CoinMarketCap', 'Discord', 'Email', 'Facebook',
    'Github', 'Linkedin', 'Reddit', 'Slack', 'Telegram', 'Twitter', 'WeChat',
    'Website', 'Whitepaper', 'YouTube'))

class TestWarning(Exception):
    pass

def assert_key_in_dict(dictionary, key):
    assert key in dictionary, \
        "expected key `{}` to be present,".format(key) \
            + "but did not find it in {}".format(dictionary.keys())

def assert_string(dictionary, key):
    assert isinstance(dictionary[key], str), \
        "expected {} to be a string, but found {}".format(key, type(dictionary[key]))

def assert_nonempty_string(dictionary, key):
    assert_string(dictionary, key)
    assert len(dictionary[key]) > 0, \
        "expected {} to be a non-empty".format(key)

def test_file_extension_yaml(filename, content):
    "file extension must be .yaml"
    assert filename.endswith(".yaml"), "expected file extension to be .yaml"

def test_filename_match_contract(filename, content):
    "filename must be match the contract address in the file"
    from os.path import basename
    assert filename.startswith("tokens/"), "expected file to be in tokens folder"
    assert basename(filename).startswith(content["addr"]), "expected filename to match contract address"

def test_addr_key_exists(content):
    "addr must be present"
    assert_key_in_dict(content, "addr")

def test_addr_0x_string(content):
    "addr must be a quoted string"
    assert isinstance(content["addr"], str), \
        "expected `addr` to be a string, but found type {}".format(type(content["addr"]))

def test_addr_ethereum_address(content):
    "addr must be a valid Ethereum address starting with '0x'"
    assert is_hex_address(content["addr"]), \
        "`addr` is not a valid Ethereum address"
    assert content["addr"].startswith("0x"), \
        "expected `addr` to start with '0x', but got '{}'".format(content["addr"][:2])

def test_addr_lowercase(content):
    "addr must be lowercase"
    assert content["addr"] == content["addr"].lower(), \
        "expected `addr` to be lowercase"

def test_decimals_key_exists(content):
    "decimals must be present"
    assert_key_in_dict(content, "addr")

def test_decimals_int(content):
    "decimals must be an integer"
    assert isinstance(content["decimals"], int), \
        "expected `decimals` to be an integer, but got {}".format(type(content["decimals"]))

def test_decimals_range(content):
    "decimals must be between 0 and 18 inclusively"
    assert 0 <= content["decimals"] <= 18, \
        "expected `decimals` to be between 0 and 18 inclusively, but got" + \
            "{:d}".format(content["decimals"])

def test_decimals_equals_erc20_decimals(content):
    "decimals equals output of contract's 'decimals' function"
    contract_decimals = web3.eth.contract(content["addr"], abi=ERC20_ABI).call().decimals()
    assert content["decimals"] == contract_decimals, \
        "expected decimals to be {:d}, but got {:d}".format(contract_decimals, content["decimals"])

def test_name_key_exists(content):
    "name must be present"
    assert_key_in_dict(content, "name")

def test_name_key_nonempty_string(content):
    "name must be a non-empty string"
    assert_nonempty_string(content, "name")

def test_symbol_key_exists(content):
    "symbol must be present"
    assert_key_in_dict(content, "symbol")

def test_symbol_nonempty_string(content):
    "symbol must be a non-empty string"
    assert_nonempty_string(content, "symbol")

def test_contract_erc20_totalSupply(content):
    "token contract must support totalSupply"
    total_supply = web3.eth.contract(content["addr"], abi=ERC20_ABI).call().totalSupply()
    assert total_supply > 0, \
        "expected total supply to be greater than 0, " + \
            "but got {:d}".format(total_supply)

TEST_BALANCE_ADDR = "0x1111111111111111111111111111111111111111"
def test_contract_erc20_balanceOf(content):
    "token contract must support balanceOf"
    balance_of = web3.eth.contract(content["addr"], abi=ERC20_ABI).call().balanceOf(TEST_BALANCE_ADDR)
    assert True, "passes if no exception was raised"

def test_description_string(content):
    "description must be a string"
    if "description" not in content:
        raise SkipTest("consider adding a description")
    assert_string(content, "description")

def test_description_nonempty(content):
    "description should be non-empty"
    if "description" not in content:
        raise SkipTest("no description found")
    if len(content["description"]) == 0:
        raise TestWarning("expected description to be non-empty, but got length 0")

def test_description_max_length(content):
    "description must be under 1000 characters"
    if "description" not in content:
        raise SkipTest("no description found")
    assert len(content["description"]) <= 1000, \
        "expected description to be under 1000 characters, " \
            + "but got {}".format(len(content["description"]))

def test_description_safe_html_only(content):
    "TODO: description must not contain unsafe HTML"

def test_links_sequence(content):
    "links must be a sequence"
    if "links" not in content:
        raise TestWarning("consider adding links")
    assert isinstance(content["links"], list), \
        "expected links to be a list, but found {}".format(type(content["links"]))

def test_link_key_value_pair(content, link=None):
    "`links` entries must contain a single key-value pair (e.g, Website: https://example.com)"
    assert link is not None, "Test suite programming error"
    assert isinstance(link, dict), \
        "expected link '{}' to be a key-value pair, ".format(link) \
            + "but got {}".format(type(link))
    assert len(link.keys()) == 1, \
        "expected link '{}' to have one key-value pair, ".format(link) \
            + "but got {}".format(len(link.keys()))

def _verify_valid_link_entry(link):
    assert link is not None, "Test suite programming error"
    if not isinstance(link, dict) or len(link.keys()) > 1:
        # Reduce test verbosity somewhat
        raise SkipTest("invalid link entry '{}'".format(link))

def test_link_key_known(content, link=None):
    "a links entry should be one of a well-known type"
    _verify_valid_link_entry(link)
    key, value = list(link.items())[0]

    if key not in KNOWN_LINK_TYPES:
        raise TestWarning(
            "can '{}: {}' be better described by one of well-known types: {}?".format(
                key, value, KNOWN_LINK_TYPES))

def test_link_value_uri(content, link=None):
    "link URL must be valid"
    from rfc3986 import is_valid_uri
    _verify_valid_link_entry(link)
    key, value = list(link.items())[0]
    assert is_valid_uri(value, require_scheme=True), \
        "expected {} link '{}' to be a valid URL".format(key, value)

def test_link_value_https_preferred(content, link=None):
    "link URL should use HTTPS whenever possible"
    from rfc3986 import is_valid_uri, uri_reference
    _verify_valid_link_entry(link)
    key, value = list(link.items())[0]

    if is_valid_uri(value, require_scheme=True):
        parsed_value = uri_reference(value)
        if parsed_value.scheme == "http":
            raise TestWarning("URL scheme is HTTP, but HTTPS is strongly preferred: {}".format(value))

USER_AGENT = "ForkDelta Token Discovery Tests 0.1.0"
def test_http_link_active(content, link=None):
    "link URL must be active"
    import cfscrape
    from requests.exceptions import RequestException
    from rfc3986 import is_valid_uri, uri_reference
    _verify_valid_link_entry(link)
    key, value = list(link.items())[0]

    if not is_valid_uri(value, require_scheme=True):
        return

    parsed_value = uri_reference(value)
    if parsed_value.scheme not in ("http", "https"):
        return

    # Hooray.
    if parsed_value.host.endswith("linkedin.com"):
        raise SkipTest("linkedin.com won't let us see {} anyway".format(value))

    try:
        r = cfscrape.create_scraper().get(value, timeout=30.0, headers={"User-Agent": USER_AGENT})
    except RequestException as exc:
        assert False, "error while checking {}: {}".format(value, exc)
    else:
        assert 200 <= r.status_code < 300, \
            "expected {} link {} to be active, but got {}".format(key, value, r.status_code)

FILE_TESTS = (
    test_file_extension_yaml,
    test_filename_match_contract
)
CONTENT_TESTS = (
    test_addr_key_exists,
    test_addr_0x_string,
    test_addr_ethereum_address,
    test_addr_lowercase,
    test_decimals_key_exists,
    test_decimals_int,
    test_decimals_range,
    test_decimals_equals_erc20_decimals,
    test_name_key_exists,
    test_name_key_nonempty_string,
    test_symbol_key_exists,
    test_symbol_nonempty_string,
    test_contract_erc20_totalSupply,
    test_contract_erc20_balanceOf,
    test_description_string,
    test_description_nonempty,
    test_description_max_length,
    test_description_safe_html_only,
    test_links_sequence
)
PER_LINK_TESTS = (
    test_link_key_value_pair,
    test_link_key_known,
    test_link_value_uri,
    test_link_value_https_preferred,
    test_http_link_active
)

from functools import partial, update_wrapper
def generate_tests(target, content):
    for test in FILE_TESTS:
        partial_test = partial(test, target)
        update_wrapper(partial_test, test)
        yield partial_test

    for test in CONTENT_TESTS:
        yield test

    if "links" in content and isinstance(content["links"], list):
        for link_kv in content["links"]:
            for test in PER_LINK_TESTS:
                partial_test = partial(test, link=link_kv)
                update_wrapper(partial_test, test)
                yield partial_test


CRITICAL_FAILURES = (AssertionError, Exception)
def main(targets, quiet=False):
    test_results = []
    skip_count = 0
    warnings_count = 0
    failures_count = 0

    for target in targets:
        try:
            with open(target) as f:
                content = yaml.safe_load(f.read())
        except FileNotFoundError:
            print("File not found: {}".format(target))
            continue

        print("Checking", target)
        for test in generate_tests(target, content):
            try:
                retval = test(content)
            except (KeyboardInterrupt, SystemExit):
                raise
            except TestWarning as exc:
                test_results.append((target, test, exc))
                warnings_count += 1
                print("  {} (WARN: {})".format(test.__doc__, exc))
            except SkipTest as exc:
                test_results.append((target, test, exc))
                skip_count += 1
                print("  {} (SKIPPED: {})".format(test.__doc__, exc))
            except AssertionError as exc:
                test_results.append((target, test, exc))
                failures_count += 1
                print("  {} (FAILED - {})".format(test.__doc__, failures_count))
            except Exception as exc:
                test_results.append((target, test, exc))
                failures_count += 1
                print("  {} (ERROR - {})".format(test.__doc__, failures_count))
            else:
                test_results.append((target, test, None))
                # print("  {}".format(test.__doc__))
        print("  Complete.")


    print(len(targets), "targets x", len(CONTENT_TESTS), "tests =",
            len(test_results), "runs, of which:",
            failures_count, "failures,", warnings_count, "warnings,",
            skip_count, "skipped.")

    import traceback
    printable_results = [result for result in test_results if result[-1] is not None]
    print("-" * 88)
    prev_target = None
    for (idx, (target, test, outcome)) in enumerate(printable_results):
        if prev_target != target:
            print("{}:".format(target))
        if isinstance(outcome, TestWarning):
            print("  {}) Non-critical issue:".format(idx + 1), outcome)
            print("        in {}: {}".format(test.__name__, test.__doc__))
        elif isinstance(outcome, SkipTest):
            print("  {}) Skipped {}:".format(idx + 1, test.__name__), outcome)
        else:
            print("  {}) Failure/Error: {}: {}".format(idx + 1, outcome.__class__.__name__, outcome))
            print("        in {}: {}".format(test.__name__, test.__doc__))
            if not isinstance(outcome, AssertionError):
                traceback.print_tb(outcome.__traceback__)
        print()
        prev_target = target
    print("-" * 88)

    return int(failures_count > 0)


if __name__ == "__main__":
    exit(main(sys.argv[1:]))
