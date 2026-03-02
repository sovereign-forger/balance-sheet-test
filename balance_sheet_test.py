#!/usr/bin/env python3
"""
Balance Sheet Test — Validate Synthetic HNWI Financial Data
============================================================
A quality assurance tool for synthetic wealth management data.
Run 5 integrity checks against any CSV dataset of synthetic
high-net-worth profiles.

Usage:
    python balance_sheet_test.py <path_to_csv>
    python balance_sheet_test.py data.csv --format json
    python balance_sheet_test.py data.csv --verbose

Checks:
    1. Net Worth Identity    — Assets − Liabilities = Net Worth
    2. Asset Decomposition   — Property + Equity + Cash = Total Assets
    3. Narrative Consistency  — Dollar amounts in text match fields
    4. Geographic Coherence   — Wealth tier matches location tier
    5. Distribution Realism   — Wealth follows Pareto, not Gaussian

Created by Sovereign Forger — https://sovereignforger.com
Born-synthetic UHNWI data with mathematical integrity.
"""

import csv
import sys
import re
import argparse
import json
from collections import Counter
from math import log, sqrt

__version__ = "1.0.0"

# ─── ANSI colors ─────────────────────────────────────────────
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


# ─── Column name mapping (flexible) ─────────────────────────
FIELD_ALIASES = {
    "net_worth": ["net_worth_usd", "net_worth", "networth", "net_worth_amount"],
    "total_assets": ["total_assets", "assets", "total_asset"],
    "total_liabilities": ["total_liabilities", "liabilities", "total_liability"],
    "property_value": ["property_value", "property", "real_estate_value"],
    "core_equity": ["core_equity", "equity", "equity_holdings"],
    "cash_liquidity": ["cash_liquidity", "cash", "liquid_assets", "liquidity"],
    "narrative_bio": ["narrative_bio", "bio", "biography", "narrative"],
    "assets_composition": ["assets_composition", "asset_composition", "asset_narrative"],
    "residence_city": ["residence_city", "city"],
    "residence_zone": ["residence_zone", "zone", "neighborhood"],
}


def resolve_column(headers, field_key):
    """Find the actual column name from aliases."""
    for alias in FIELD_ALIASES.get(field_key, []):
        if alias in headers:
            return alias
    return None


def parse_number(value):
    """Parse a numeric string, stripping $ and commas."""
    if value is None or value == "":
        return None
    cleaned = str(value).replace("$", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_dollar_amounts(text):
    """Extract all dollar amounts from a narrative text."""
    if not text:
        return []
    pattern = r'\$[\d,]+(?:\.\d+)?'
    matches = re.findall(pattern, text)
    return [parse_number(m) for m in matches if parse_number(m) is not None]


# ═══════════════════════════════════════════════════════════════
# CHECK 1: Net Worth Identity
# ═══════════════════════════════════════════════════════════════
def check_net_worth_identity(row, cols, tolerance=0.01):
    """Assets − Liabilities must equal Net Worth."""
    net_worth = parse_number(row.get(cols["net_worth"]))
    assets = parse_number(row.get(cols["total_assets"]))
    liabilities = parse_number(row.get(cols["total_liabilities"]))

    if None in (net_worth, assets, liabilities):
        return None, "Missing fields"

    computed = assets - liabilities
    diff = abs(computed - net_worth)

    if diff <= tolerance:
        return True, None
    else:
        return False, f"Assets({assets:,.0f}) − Liabilities({liabilities:,.0f}) = {computed:,.0f}, but Net Worth = {net_worth:,.0f} [Δ {diff:,.0f}]"


# ═══════════════════════════════════════════════════════════════
# CHECK 2: Asset Decomposition
# ═══════════════════════════════════════════════════════════════
def check_asset_decomposition(row, cols, tolerance=0.01):
    """Property + Equity + Cash must equal Total Assets."""
    assets = parse_number(row.get(cols["total_assets"]))
    prop = parse_number(row.get(cols.get("property_value")))
    equity = parse_number(row.get(cols.get("core_equity")))
    cash = parse_number(row.get(cols.get("cash_liquidity")))

    if None in (assets, prop, equity, cash):
        return None, "Missing sub-fields"

    computed = prop + equity + cash
    diff = abs(computed - assets)

    if diff <= tolerance:
        return True, None
    else:
        return False, f"Property({prop:,.0f}) + Equity({equity:,.0f}) + Cash({cash:,.0f}) = {computed:,.0f}, but Total Assets = {assets:,.0f} [Δ {diff:,.0f}]"


# ═══════════════════════════════════════════════════════════════
# CHECK 3: Narrative Consistency
# ═══════════════════════════════════════════════════════════════
def check_narrative_consistency(row, cols):
    """Dollar amounts in narrative text must match structured fields."""
    assets_text = row.get(cols.get("assets_composition"), "")
    if not assets_text:
        return None, "No narrative field"

    narrative_amounts = set(extract_dollar_amounts(assets_text))
    if not narrative_amounts:
        return None, "No dollar amounts in narrative"

    field_amounts = set()
    for key in ["total_assets", "property_value", "core_equity", "cash_liquidity"]:
        col = cols.get(key)
        if col:
            val = parse_number(row.get(col))
            if val is not None:
                field_amounts.add(val)

    mismatches = narrative_amounts - field_amounts
    if not mismatches:
        return True, None
    else:
        return False, f"Narrative contains amounts not in fields: {', '.join(f'${m:,.0f}' for m in mismatches)}"


# ═══════════════════════════════════════════════════════════════
# CHECK 4: Geographic Coherence (heuristic)
# ═══════════════════════════════════════════════════════════════

# Known UHNWI enclaves with expected minimum wealth tiers
UHNWI_ZONES = {
    "bel air": 500_000_000,
    "pacific heights": 100_000_000,
    "atherton": 100_000_000,
    "old palo alto": 200_000_000,
    "hillsborough": 100_000_000,
    "montecito": 100_000_000,
    "malibu": 50_000_000,
    "ocean avenue": 50_000_000,
    "presidio heights": 80_000_000,
    "russian hill": 50_000_000,
    "nob hill": 50_000_000,
    "beverly hills": 100_000_000,
    "holmby hills": 200_000_000,
    "woodside": 100_000_000,
    "ross": 50_000_000,
    "tiburon": 50_000_000,
    "saratoga": 30_000_000,
    "los altos hills": 50_000_000,
    "silver creek valley": 30_000_000,
}


def check_geographic_coherence(row, cols):
    """Wealth tier should be consistent with residential zone."""
    zone = row.get(cols.get("residence_zone"), "")
    net_worth = parse_number(row.get(cols.get("net_worth")))

    if not zone or net_worth is None:
        return None, "Missing location or net worth"

    zone_lower = zone.strip().lower()
    min_wealth = UHNWI_ZONES.get(zone_lower)

    if min_wealth is None:
        return None, f"Zone '{zone}' not in reference database"

    if net_worth >= min_wealth * 0.5:  # Allow 50% margin
        return True, None
    else:
        return False, f"Net worth ${net_worth:,.0f} seems low for {zone} (expected ≥ ${min_wealth:,.0f})"


# ═══════════════════════════════════════════════════════════════
# CHECK 5: Distribution Realism (Pareto test)
# ═══════════════════════════════════════════════════════════════
def check_distribution_realism(net_worths):
    """
    Test whether the wealth distribution follows a Pareto distribution
    rather than a Gaussian (normal) distribution.

    Uses the ratio of max/median vs mean/median as a heuristic:
    - Pareto: max >> mean >> median (right-skewed)
    - Gaussian: max ≈ mean ≈ median (symmetric)

    Also checks skewness: Pareto should be heavily right-skewed.
    """
    if len(net_worths) < 10:
        return None, "Need ≥ 10 records for distribution test"

    sorted_nw = sorted(net_worths)
    n = len(sorted_nw)
    median = sorted_nw[n // 2]
    mean = sum(sorted_nw) / n
    maximum = sorted_nw[-1]

    if median == 0:
        return None, "Median is zero — cannot test distribution"

    # Skewness test: right-skew indicates Pareto-like
    mean_dev = [(x - mean) for x in sorted_nw]
    variance = sum(d**2 for d in mean_dev) / n
    std_dev = sqrt(variance) if variance > 0 else 1
    skewness = sum(d**3 for d in mean_dev) / (n * std_dev**3) if std_dev > 0 else 0

    # Concentration ratio: top 20% should hold > 60% of total wealth (Pareto)
    top_20_start = int(n * 0.8)
    total_wealth = sum(sorted_nw)
    top_20_wealth = sum(sorted_nw[top_20_start:])
    concentration = top_20_wealth / total_wealth if total_wealth > 0 else 0

    results = {
        "records": n,
        "min": sorted_nw[0],
        "median": median,
        "mean": mean,
        "max": maximum,
        "skewness": skewness,
        "top_20_concentration": concentration,
    }

    # Pareto-like: skewness > 1 and top 20% hold > 60%
    is_pareto = skewness > 1.0 and concentration > 0.60

    if is_pareto:
        return True, results
    else:
        issues = []
        if skewness <= 1.0:
            issues.append(f"skewness {skewness:.2f} (expected > 1.0)")
        if concentration <= 0.60:
            issues.append(f"top-20% concentration {concentration:.1%} (expected > 60%)")
        return False, {"issues": issues, **results}


# ═══════════════════════════════════════════════════════════════
# MAIN RUNNER
# ═══════════════════════════════════════════════════════════════
def load_csv(filepath):
    """Load CSV and return list of dicts."""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def run_tests(rows, verbose=False):
    """Run all 5 checks and return structured results."""
    if not rows:
        print(f"{RED}Error: No data rows found.{RESET}")
        sys.exit(1)

    headers = list(rows[0].keys())

    # Resolve columns
    cols = {}
    for field_key in FIELD_ALIASES:
        col = resolve_column(headers, field_key)
        if col:
            cols[field_key] = col

    # Required columns
    for req in ["net_worth", "total_assets", "total_liabilities"]:
        if req not in cols:
            print(f"{RED}Error: Cannot find column for '{req}'.{RESET}")
            print(f"Available columns: {', '.join(headers)}")
            sys.exit(1)

    total = len(rows)
    results = {
        "total_records": total,
        "checks": {}
    }

    # ── Check 1: Net Worth Identity ──
    c1_pass, c1_fail, c1_skip = 0, 0, 0
    c1_failures = []
    for i, row in enumerate(rows):
        ok, msg = check_net_worth_identity(row, cols)
        if ok is True:
            c1_pass += 1
        elif ok is False:
            c1_fail += 1
            c1_failures.append((i + 1, row.get(cols.get("net_worth", ""), "?"), msg))
        else:
            c1_skip += 1

    results["checks"]["net_worth_identity"] = {
        "pass": c1_pass, "fail": c1_fail, "skip": c1_skip,
        "rate": c1_pass / (c1_pass + c1_fail) if (c1_pass + c1_fail) > 0 else 0
    }

    # ── Check 2: Asset Decomposition ──
    c2_pass, c2_fail, c2_skip = 0, 0, 0
    c2_failures = []
    for i, row in enumerate(rows):
        ok, msg = check_asset_decomposition(row, cols)
        if ok is True:
            c2_pass += 1
        elif ok is False:
            c2_fail += 1
            c2_failures.append((i + 1, msg))
        else:
            c2_skip += 1

    results["checks"]["asset_decomposition"] = {
        "pass": c2_pass, "fail": c2_fail, "skip": c2_skip,
        "rate": c2_pass / (c2_pass + c2_fail) if (c2_pass + c2_fail) > 0 else 0
    }

    # ── Check 3: Narrative Consistency ──
    c3_pass, c3_fail, c3_skip = 0, 0, 0
    c3_failures = []
    for i, row in enumerate(rows):
        ok, msg = check_narrative_consistency(row, cols)
        if ok is True:
            c3_pass += 1
        elif ok is False:
            c3_fail += 1
            c3_failures.append((i + 1, msg))
        else:
            c3_skip += 1

    results["checks"]["narrative_consistency"] = {
        "pass": c3_pass, "fail": c3_fail, "skip": c3_skip,
        "rate": c3_pass / (c3_pass + c3_fail) if (c3_pass + c3_fail) > 0 else 0
    }

    # ── Check 4: Geographic Coherence ──
    c4_pass, c4_fail, c4_skip = 0, 0, 0
    c4_failures = []
    for i, row in enumerate(rows):
        ok, msg = check_geographic_coherence(row, cols)
        if ok is True:
            c4_pass += 1
        elif ok is False:
            c4_fail += 1
            c4_failures.append((i + 1, msg))
        else:
            c4_skip += 1

    results["checks"]["geographic_coherence"] = {
        "pass": c4_pass, "fail": c4_fail, "skip": c4_skip,
        "rate": c4_pass / (c4_pass + c4_fail) if (c4_pass + c4_fail) > 0 else 0
    }

    # ── Check 5: Distribution Realism ──
    net_worths = []
    for row in rows:
        nw = parse_number(row.get(cols["net_worth"]))
        if nw is not None and nw > 0:
            net_worths.append(nw)

    dist_ok, dist_info = check_distribution_realism(net_worths)
    results["checks"]["distribution_realism"] = {
        "pass": 1 if dist_ok else 0,
        "fail": 0 if dist_ok else 1,
        "skip": 0 if dist_ok is not None else 1,
        "details": dist_info
    }

    # ═══ PRINT REPORT ═══
    print()
    print(f"{BOLD}{'═' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  BALANCE SHEET TEST — Data Quality Report{RESET}")
    print(f"{BOLD}{'═' * 60}{RESET}")
    print(f"  Dataset: {total} records")
    print(f"{'─' * 60}")

    def print_check(name, passed, failed, skipped, idx):
        total_tested = passed + failed
        if total_tested == 0:
            status = f"{YELLOW}SKIP{RESET}"
            detail = f"({skipped} records without required fields)"
        elif failed == 0:
            status = f"{GREEN}PASS{RESET}"
            detail = f"{passed}/{total_tested} records"
        else:
            rate = passed / total_tested * 100
            status = f"{RED}FAIL{RESET}"
            detail = f"{passed}/{total_tested} records ({rate:.1f}%)"
        print(f"  {idx}. {name:30s} [{status}] {detail}")

    print_check("Net Worth Identity", c1_pass, c1_fail, c1_skip, 1)
    print_check("Asset Decomposition", c2_pass, c2_fail, c2_skip, 2)
    print_check("Narrative Consistency", c3_pass, c3_fail, c3_skip, 3)
    print_check("Geographic Coherence", c4_pass, c4_fail, c4_skip, 4)

    # Distribution check (single result)
    if dist_ok is True:
        print(f"  5. {'Distribution Realism':30s} [{GREEN}PASS{RESET}] Pareto-like (skew: {dist_info['skewness']:.2f}, top-20%: {dist_info['top_20_concentration']:.1%})")
    elif dist_ok is False:
        issues_str = "; ".join(dist_info.get("issues", []))
        print(f"  5. {'Distribution Realism':30s} [{RED}FAIL{RESET}] {issues_str}")
    else:
        print(f"  5. {'Distribution Realism':30s} [{YELLOW}SKIP{RESET}] {dist_info}")

    print(f"{'─' * 60}")

    # Overall score
    checks_run = 0
    checks_passed = 0
    for name, data in results["checks"].items():
        if name == "distribution_realism":
            if data["pass"] + data["fail"] > 0:
                checks_run += 1
                if data["pass"] > 0:
                    checks_passed += 1
        else:
            if data["pass"] + data["fail"] > 0:
                checks_run += 1
                if data["fail"] == 0:
                    checks_passed += 1

    if checks_run > 0:
        score = checks_passed / checks_run * 100
        if score == 100:
            grade = f"{GREEN}{BOLD}EXCELLENT{RESET}"
        elif score >= 80:
            grade = f"{YELLOW}{BOLD}GOOD{RESET}"
        elif score >= 60:
            grade = f"{YELLOW}FAIR{RESET}"
        else:
            grade = f"{RED}{BOLD}POOR{RESET}"

        print(f"  Overall: {checks_passed}/{checks_run} checks passed — {grade}")
    print(f"{'═' * 60}")

    # Verbose: show failures
    if verbose and (c1_failures or c2_failures or c3_failures or c4_failures):
        print(f"\n{BOLD}Failure Details:{RESET}")
        if c1_failures:
            print(f"\n  {RED}Net Worth Identity failures:{RESET}")
            for row_num, _, msg in c1_failures[:10]:
                print(f"    Row {row_num}: {msg}")
            if len(c1_failures) > 10:
                print(f"    ... and {len(c1_failures) - 10} more")

        if c2_failures:
            print(f"\n  {RED}Asset Decomposition failures:{RESET}")
            for row_num, msg in c2_failures[:10]:
                print(f"    Row {row_num}: {msg}")

        if c3_failures:
            print(f"\n  {RED}Narrative Consistency failures:{RESET}")
            for row_num, msg in c3_failures[:10]:
                print(f"    Row {row_num}: {msg}")

        if c4_failures:
            print(f"\n  {RED}Geographic Coherence failures:{RESET}")
            for row_num, msg in c4_failures[:10]:
                print(f"    Row {row_num}: {msg}")
        print()

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Balance Sheet Test — Validate synthetic HNWI financial data",
        epilog="Created by Sovereign Forger — https://sovereignforger.com"
    )
    parser.add_argument("file", help="Path to CSV file with synthetic profiles")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show failure details")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--version", action="version", version=f"balance-sheet-test {__version__}")

    args = parser.parse_args()

    rows = load_csv(args.file)
    results = run_tests(rows, verbose=args.verbose)

    if args.format == "json":
        # Convert for JSON serialization
        print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
