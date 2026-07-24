---
name: dm-quant-api-v26
description: Use only when explicitly asked to use DM Quant API V2.6, query DM data, search DM EDB levels, or export DM API results.
---

# DM Quant API V2.6

Default to the fastest path. Do not load large files into context.

## Fast Path

1. Use known DM PythonAPI style first: `DMQuantApiClient(app_key=..., sm4_key=..., pythonic=True)` and `client.post_data(data={...}, api_path="...")`.
2. Use `references/endpoint-index-v2.6.md` only when the endpoint is unknown.
3. Use `scripts/query_api.py` for direct calls and exports.
4. Use `scripts/search_edb_levels.py` for EDB hierarchy lookup.
5. Search large assets with `rg`; do not read them end-to-end.

## Rules

- Do not invent `api_path`, parameter names, field names, enum values, or history ranges.
- Prefer `pythonic=True` and snake_case request keys.
- Use `field_names` unless the manual says otherwise.
- Convert relative dates to exact dates before calling.
- Do not store or upload real credentials.
- For pagination, use `return_type="dict"` and handle `offset` / `max_offset`.
- In V2.6 bond date series, do not use removed CFETS source `2`; valid sources are `1,3,4,7`.

## Files

- Fast endpoint index: `references/endpoint-index-v2.6.md`
- Large manual extract: `assets/reference-data/manual-v2.6-20260721-extract.txt`
- EDB dictionary: `assets/reference-data/edb-levels.csv`
- Prompt reference: `assets/reference-data/dm-api-prompt-v2.6.md`
- Wheel: `assets/dm_quant_api_client-0.2.3-py3-none-any.whl`

## Commands

```bash
python scripts/query_api.py --api-path "/dm-quant-func-service/api/v1/..." --data-json '{"start_date":"2026-07-01","end_date":"2026-07-21"}'
python scripts/search_edb_levels.py --keyword CPI --limit 20
rg -n "债券-基础资料|basic-info/info|出参" assets/reference-data/manual-v2.6-20260721-extract.txt
```

If `app_secret` is rejected, use `sm4_key`; the value is the same secret.
