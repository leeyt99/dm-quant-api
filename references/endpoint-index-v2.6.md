# DM Quant API V2.6 Endpoint Index

Fast lookup index. Use this first, then search `manual-v2.6-20260721-extract.txt` only for exact field lists, enum definitions, output columns, or longer examples.

| Category | Function | api_path | Key Params | Range |
|---|---|---|---|---|
| 债券-行情 | 债券-高频序列 | `/dm-quant-func-service/api/v1/bond/market-data/bars` | `security_id_list`, `data_source_list`, `kline_type` | 按 K 线频率，1天至3年 |
| 债券-行情 | 债券-日期序列 | `/dm-quant-func-service/api/v1/bond/market-data/date` | `security_id_list`, `data_source_list`, `start_date`, `end_date` | <=3个月 |
| 债券-行情 | 债券-实时最新行情 | `/dm-quant-func-service/api/v1/bond/market-data/realtime-quote` | `security_id_list` | 仅当天 |
| 债券-行情 | 债券-收益率曲线 | `/dm-quant-func-service/api/v1/bond/yield-curve/data` | `data_source`, `curve_name`, `curve_term_list` | <=1个月 |
| 债券-行情 | 债券-机构行为 | `/dm-quant-func-service/api/v1/bond/analysis/insti-sentiment` | `data_source`; 国利需 `freq_list` | <=1周 |
| 债券-分析 | 债券-基础资料 | `/dm-quant-func-service/api/v1/bond/basic-info/info` | `security_id_list` 或 `sec_short_name` | 无 |
| 债券-分析 | 债券-发行人维度债券调取 | `/dm-quant-func-service/api/v1/bond/basic-info/outstanding-bonds` | `issuer_full_name` 或 `society_code`, `bond_status_list`, `offset` | 需翻页 |
| 债券-分析 | 债券-活跃券/次活跃券 | `/dm-quant-func-service/api/v1/bond/market-data/rolling-bonds` | `sequence_type`, `bond_filter_type`, `key_tenor` | <=1年 |
| 债券-分析 | 债券-DM流动性评分 | `/dm-quant-func-service/api/v1/bond/analysis/liquidity-score` | `security_id_list` 或 `sec_short_name_list`, `stat_period` | <=1个月 |
| 债券-分析 | 主体-DM流动性评分 | `/dm-quant-func-service/api/v1/company/analysis/liquidity-score` | `com_full_name_list`, `stat_period_list` | <=1个月 |
| 债券-分析 | 评级-主体评级 | `/dm-quant-func-service/api/v1/company/rating/data` | `com_full_name_list` 等 | 按手册 |
| 债券-分析 | 评级-债券评级 | `/dm-quant-func-service/api/v1/bond/rating/data` | `security_id_list` 等 | 按手册 |
| 债券-分析 | 评级-债券隐含评级 | `/dm-quant-func-service/api/v1/bond/analysis/implied-rating` | `security_id_list`, `start_date`, `end_date` | 按手册 |
| 债券-分析 | 评级-债券隐含违约率 | `/dm-quant-func-service/api/v1/bond/default-rate/data` | `security_id_list`, `start_date`, `end_date` | 按手册 |
| 债券-发行 | 债券-一级发行 | `/dm-quant-func-service/api/v1/bond/primary/data` | `start_date`, `end_date`, `bond_category`, `offset` | <=30天 |
| 债券-发行 | 债券-余额包销 | `/dm-quant-func-service/api/v1/bond/basic-info/underwriter-balance` | `security_id_list` 或 `sec_short_name_list` | 无 |
| 债券-发行 | 利率债招标-标书 | `/dm-quant-func-service/api/v1/bond/primary/rate-bond-tender-detail` | `security_id_list` 或 `sec_short_name_list` | 无 |
| 离岸债 | 离岸债-基础信息 | `/dm-quant-func-service/api/v1/bond/basic-info/offshore-bond-profile` | `security_id_list` 或中英文简称 | 无 |
| 离岸债 | 全球离岸债-发行人维度离岸债调取 | `/dm-quant-func-service/api/v1/bond/basic-info/offshore-bonds-by-issuer` | 主体/发行人相关入参 | 需翻页 |
| 离岸债 | 全球国债-高频序列 | `/dm-quant-func-service/api/v1/bond/market-data/global-bond-bars` | `security_id_list`, `kline_type` | 按 K 线频率 |
| 离岸债 | 离岸债 RP 估值-单债日期序列 | `/dm-quant-func-service/api/v1/bond/market-data/offshore-bond-valuation` | `security_id_list` 或中英文简称, `start_date`, `end_date` | <=1年 |
| 离岸债 | 离岸债 RP 估值-主题日期序列 | `/dm-quant-func-service/api/v1/bond/market-data/offshore-bond-theme-valuation` | `subject_name_list`, `start_date`, `end_date` | <=1年 |
| 离岸债 | 外资发行人-基础信息 | `/dm-quant-func-service/api/v1/bond/basic-info/intl-issuer-basic` | `issuer_eng_full_name_list` 或 `issuer_chi_full_name_list` | 无 |
| 离岸债 | 海外评级-离岸债评级 | `/dm-quant-func-service/api/v1/bond/rating/offshore-bond-intl-rating` | `security_id_list` 或中英文简称, `start_date`, `end_date` | <=1年 |
| 离岸债 | 海外评级-主体评级 | `/dm-quant-func-service/api/v1/company/rating/com-intl-rating` | `issuer_eng_full_name_list` 或 `issuer_chi_full_name_list` | 按手册 |
| 票据 | 票据-直贴行情-当日实时行情 | `/dm-quant-func-service/api/v1/bill/discount/quote/realtime` | `bill_bank_short_name_list` | 仅当天 |
| 票据 | 票据-大行指导 | `/dm-quant-func-service/api/v1/bill/bank-guided-price/data` | `bank_short_name_list`, `start_date`, `end_date` | <=1周 |
| 资金 | 货币市场-日期序列 | `/dm-quant-func-service/api/v1/money-market/data/date` | `instrument_type_list` 或 `instrument_code_list` | <=1周 |
| 资金 | 货币市场-资金情绪指数 | `/dm-quant-func-service/api/v1/money-market/analysis/sentiment-index` | `start_date`, `end_date` | <=2个月 |
| 资金 | 货币市场-国际基准利率-日期序列 | `/dm-quant-func-service/api/v1/money-market/data/intl-benchmark-rate` | `instrument_code_list` 或 `instrument_region_list` | 按手册 |
| 资金 | 资金日历 | `/dm-quant-func-service/api/v1/fund/calendar/data` | `start_date`, `end_date`, `data_category` | <=1年 |
| 资金 | 公开市场操作 | `/dm-quant-func-service/api/v1/money-market/data/omo-info` | `start_date`, `end_date` | <=1年 |
| 资金 | 央行动态-超储率 | `/dm-quant-func-service/api/v1/edb/pboc/excess-reserves` | `start_date`, `end_date` | 按手册 |
| 资金 | CME交易员美联储利率预测 | `/dm-quant-func-service/api/v1/global-macro/data/cme-fomc-probabilities` | `meeting_date_list` 或预测日期区间 | 按手册 |
| 期货 | 期货-高频序列 | `/dm-quant-func-service/api/v1/futures/market-data/bars` | `security_id_list`, `kline_type` | 按 K 线频率 |
| 期货 | 期货-日期序列衍生 | `/dm-quant-func-service/api/v1/futures/analysis/basis` | `security_id_list`, `start_date`, `end_date` | <=3个月 |
| 期货 | 期货-成交持仓排名 | `/dm-quant-func-service/api/v1/futures/analysis/vol-oi-rank` | `security_id_list`, `start_date`, `end_date` | <=1周 |
| 基金 | 基金-基础信息 | `/dm-quant-func-service/api/v1/fund/basic-info/profile` | `security_id_list` 或 `sec_short_name_list` | 无 |
| 基金 | 基金-日期序列 | `/dm-quant-func-service/api/v1/fund/market-data/date` | `security_id_list` 或 `sec_short_name_list`, `start_date`, `end_date` | <=1年 |
| 基金 | 基金-阶段回报 | `/dm-quant-func-service/api/v1/fund/market-data/performance` | `security_id_list` 或 `sec_short_name_list`, `window_period_list` | <=1个月 |
| 外汇 | 外汇-高频序列 | `/dm-quant-func-service/api/v1/fx/market-data/bars` | `security_id_list`, `kline_type` | 按 K 线频率 |
| 企业库 | 工商企业基础信息 | `/dm-quant-func-service/api/v1/company/basic-info/info` | `com_full_name_list` 或 `society_code_list` 或工商注册号 | 无 |
| 宏观经济 | EDB-指标ID获取 | `/dm-quant-func-service/api/v1/edb/data-info/code` | `edb_level_id_list`, `offset` | 需翻页 |
| 宏观经济 | EDB-指标数值调取 | `/dm-quant-func-service/api/v1/edb/data-info/data` | `indicator_id`, `start_date`, `end_date` | 按频率 |
| 宏观经济 | 区域经济 | `/dm-quant-func-service/api/v1/ctz/area/economy-data` | `area_name`, `data_year_list` | 最多5年 |
| 权益 | 权益-高频序列 | `/dm-quant-func-service/api/v1/equity/market-data/bars` | `security_category`, `security_id_list`, `kline_type` | 按 K 线频率 |
| 工具类 | 交易日历 | `/dm-quant-func-service/api/v1/market/trade-dates` | `market_type`, `start_date`, `end_date` | <=2年 |

Important V2.6 notes:

- Bond date series data sources: `1=经纪商, 3=上交所, 4=上固收, 7=深交所`; do not use removed CFETS source `2`.
- Money-market sentiment path is `/dm-quant-func-service/api/v1/money-market/analysis/sentiment-index`.
- Most field filtering uses `field_names`; confirm in the manual when an endpoint is unusual.
