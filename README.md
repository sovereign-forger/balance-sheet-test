# The Balance Sheet Test

**Does your synthetic data add up? Literally?**

A single command to audit any synthetic HNWI dataset for mathematical integrity. Open a file, pick a record, check whether Assets − Liabilities = Net Worth. If it fails on even one record, you have a data quality problem that will propagate through every model you train on it.

Most synthetic financial datasets fail this test.

```
pip install -r requirements.txt  # no dependencies — pure Python
python balance_sheet_test.py your_data.csv
```

```
════════════════════════════════════════════════════════════
  BALANCE SHEET TEST — Data Quality Report
════════════════════════════════════════════════════════════
  Dataset: 100 records
────────────────────────────────────────────────────────────
  1. Net Worth Identity              [PASS] 100/100 records
  2. Asset Decomposition             [PASS] 100/100 records
  3. Narrative Consistency           [PASS] 100/100 records
  4. Geographic Coherence            [PASS] 17/17 records
  5. Distribution Realism            [PASS] Pareto-like (skew: 3.68, top-20%: 63.3%)
────────────────────────────────────────────────────────────
  Overall: 5/5 checks passed — EXCELLENT
════════════════════════════════════════════════════════════
```

That's [Sovereign Forger](https://sovereignforger.com) data. Run it on yours.

---

## The Five Checks

### 1. Net Worth Identity
```
Total Assets − Total Liabilities = Net Worth
```
The fundamental accounting identity. If a single record fails, the dataset's financial fields were generated independently rather than constrained by algebraic relationships. Your model learns that inconsistency is normal.

### 2. Asset Decomposition
```
Property Value + Core Equity + Cash Liquidity = Total Assets
```
Many datasets include detailed sub-fields that look granular but don't sum to the stated total. The appearance of detail without the substance.

### 3. Narrative Consistency
Dollar amounts mentioned in biographical or asset narrative text are cross-checked against the structured numerical fields. If the narrative says "$130M in assets" but the field says $127M, the text was generated without awareness of the numbers.

### 4. Geographic Coherence
A $2M net worth in Atherton or a $500K profile in Bel Air signals that the location and wealth tier were generated independently. This check flags profiles where the residential zone doesn't match the wealth tier.

### 5. Distribution Realism
UHNWI wealth follows a Pareto distribution — a small number of profiles at very high net worth, with a long tail. If your dataset shows a bell curve, it was not modeled on real-world wealth patterns. The test checks skewness and top-20% wealth concentration.

---

## Usage

```bash
# Basic test
python balance_sheet_test.py data.csv

# See which records fail and why
python balance_sheet_test.py data.csv --verbose

# Machine-readable output for CI pipelines
python balance_sheet_test.py data.csv --format json
```

### CSV Column Mapping

The tool auto-detects common column naming conventions:

| Field | Accepted column names |
|-------|----------------------|
| Net Worth | `net_worth_usd`, `net_worth`, `networth` |
| Total Assets | `total_assets`, `assets` |
| Total Liabilities | `total_liabilities`, `liabilities` |
| Property Value | `property_value`, `property`, `real_estate_value` |
| Core Equity | `core_equity`, `equity`, `equity_holdings` |
| Cash Liquidity | `cash_liquidity`, `cash`, `liquid_assets` |
| Narrative | `narrative_bio`, `bio`, `assets_composition` |
| Location | `residence_city`, `residence_zone` |

---

## Why This Exists

Most synthetic data pipelines — GANs, VAEs, LLMs — generate fields probabilistically. Each value is sampled from a distribution with some correlation modeling to keep things "loosely coherent."

Loosely coherent is not algebraically exact. At scale, small error rates compound: a 2% failure rate on 10,000 records means 200 broken balance sheets polluting your training data.

The alternative is **born-synthetic** data: built from mathematical constraints first, enriched by AI second. Net worth is computed from a Pareto distribution. Assets and liabilities are derived from constrained splits. Sub-components are allocated proportionally. The numbers are locked before any language model touches the profile.

The AI adds biography, profession, philanthropy. It never touches the numbers.

This is how [Sovereign Forger](https://sovereignforger.com) builds UHNWI data. The Balance Sheet Test is how we prove it works — and how you can verify any dataset, including ours.

---

## Try It On Real Data

We publish a free sample of 100 born-synthetic Silicon Valley UHNWI profiles. Every record passes all five checks — 100 out of 100.

**[Download the free sample →](https://sovereignforger.com/sample/?ref=github)**

Run the test. If the math works, consider what 10,000 records with the same integrity could do for your product.

---

## License

MIT — use it, fork it, test your vendors with it.

---

*Built by [Sovereign Forger](https://sovereignforger.com) — born-synthetic UHNWI data with mathematical integrity.*
