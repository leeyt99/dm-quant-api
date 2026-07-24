---
name: dm-quant-api-v26
description: Use only for DM Quant PythonAPI V2.6 endpoint lookup, authenticated API calls, EDB hierarchy search, or DM data exports. Includes a lightweight endpoint index, local EDB dictionary, V2.6 manual extract, bundled wheel, and reusable query scripts.
---

# DM Quant API V2.6

Use this skill only when the task explicitly needs DM Quant API calls, endpoint/field lookup, EDB dictionary lookup, or DM data export.

## Core Rules

- Never invent `api_path`, parameter names, field names, enum values, or history ranges.
- Prefer `pythonic=True`; write request parameters and read response fields in `snake_case`.
- Use `field_names` for field filtering unless the manual explicitly says the endpoint uses another parameter.
- Convert relative dates such as today, yesterday, latest, recent week, or past month into exact dates before calling the API.
- Do not store or upload real credentials. Use environment variables or a local ignored `credentials.local.json`.
- For paginated endpoints, call with `return_type="dict"` and handle `offset` / `max_offset` according to the manual.
- For bond date series in V2.6, do not use removed CFETS data source `2`; valid listed sources are `1=经纪商, 3=上交所, 4=上固收, 7=深交所`.

## Resource Routing

- Start with `references/endpoint-index-v2.6.md` for fast endpoint selection and key parameters.
- Search `references/manual-v2.6-20260721-extract.txt` with `rg` only when exact input fields, output fields, enum notes, or date range details are needed.
- Read `references/dm-api-prompt-v2.6.md` only when drafting reusable prompts or explaining V2.6 changes.
- For EDB level lookup, use `scripts/search_edb_levels.py` against `references/edb-levels.csv`.
- For direct API calls and exports, use `scripts/query_api.py`.
- The local dependency wheel is bundled at `assets/dm_quant_api_client-0.2.3-py3-none-any.whl`.

## Setup

Install dependencies from the skill directory:

```bash
python -m pip install -r requirements.txt
```

Credentials can be provided by either environment variables:

```bash
export DM_APP_KEY="..."
export DM_APP_SECRET="..."
```

or by copying `credentials.example.json` to `credentials.local.json` and filling it locally. `credentials.local.json` is ignored by git.

The official client may use `sm4_key` in older wheels and `app_secret` in newer manual examples. The bundled helper accepts `--app-secret` and passes it to the installed client as `sm4_key` when required.

## Workflows

1. Clarify the data need: subject, instruments, fields, frequency, date range, and output format.
2. Resolve exact dates in Asia/Shanghai time.
3. Locate the endpoint in `references/endpoint-index-v2.6.md`.
4. Confirm exact required parameters, optional filters, output fields, pagination, and history range with targeted `rg` searches only as needed.
5. Search EDB hierarchy first when the user gives an EDB theme or level rather than a final indicator.
6. Run `scripts/query_api.py` with exact `api_path` and JSON payload.
7. Return the endpoint, key request parameters, returned fields, row count, and a short sample. Export to CSV/XLSX/JSON when requested.

## Commands

Search EDB levels:

```bash
python scripts/search_edb_levels.py --keyword CPI --limit 20
python scripts/search_edb_levels.py --level-id M00161722100000 --limit 20
```

Call a DM endpoint:

```bash
python scripts/query_api.py \
  --api-path "/dm-quant-func-service/api/v1/bond/market-data/date" \
  --data-json '{"security_id_list":["2500002.IB"],"data_source_list":[1],"start_date":"2026-04-24","end_date":"2026-04-24"}' \
  --head 5
```

Export a result:

```bash
python scripts/query_api.py \
  --api-path "/dm-quant-func-service/api/v1/..." \
  --data-json '{"start_date":"2026-07-01","end_date":"2026-07-21"}' \
  --output output.xlsx
```

## Common Pitfalls

- If `DMQuantApiClient.__init__()` rejects `app_secret`, use `sm4_key` or the bundled helper.
- With `pythonic=True`, do not send camelCase payload keys such as `securityIdList`.
- EDB indicator calls use the exact parameter names from the manual; do not confuse level IDs with final indicator IDs.
- If the response structure contains paging metadata, switch to `return_type="dict"` before converting to a DataFrame.
- Always cite the function/manual source when answering endpoint or field questions.
