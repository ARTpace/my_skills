# Web 爬虫分析报告

- **目标 URL**: https://item.upload.taobao.com/sell/v2/publish.htm?catId=202123606&gpfRenderTrace=215042cd17776879700956247e0dc9&fromAICategory=true&keyProps=%7B%7D&fromAIPublish=true&newRouter=1&paramCacheId=merge_router_cache_2484415358_1777689225297_363&x-gpf-submit-trace-id=213e04e017776892252673290e0d3f
- **分析时间**: 2026-05-02T14:06:59.283918
- **页面标题**: 淘宝网 - 商品发布

## 概览

| 指标 | 数值 |
|------|------|
| 总请求数 | 308 |
| API 端点 | 44 |
| 表单 | 0 |
| WebSocket | 7 |
| 技术栈 | Moment.js, React, Underscore/Lodash |

## 预检分析

- **Server**: Tengine/Aserver
- **robots.txt**: ⛔ 禁止爬取
- **Disallow 路径**: /

## 反爬检测

- **WAF**: f5_bigip
- **CAPTCHA**: ✓ 无
- **需 JS**: 否

## 渲染分析

- **渲染模式**: SSR
- **数据位置**: html
- **推荐工具**: requests + BeautifulSoup

## 分页分析

- **分页类型**: none

## 增量更新

- **ETag**: ✓
- **Last-Modified**: ✓

## API 端点

| # | 方法 | 状态 | 类型 | URL |
|---|------|------|------|-----|
| 1 | GET | 302 | REST | `https://item.upload.taobao.com/sell/v2/publish.htm?catId=202123606&gpfRenderTrace=215042cd17776879700956247e0dc9&fromAIC` |
| 2 | GET | 302 | REST | `https://login.taobao.com/member/login.jhtml?redirectURL=http%3A%2F%2Fitem.upload.taobao.com%2Fsell%2Fv2%2Fpublish.htm%3F` |
| 3 | GET | 200 | REST | `https://login.taobao.com/havanaone/login/login.htm?bizName=taobao&redirectURL=http%3A%2F%2Fitem.upload.taobao.com%2Fsell` |
| 4 | GET | 200 | REST | `https://login.taobao.com/havanaone/loginLegacy/qrCode/generate.do?bizEntrance=taobao_pc&bizName=taobao&hitRSA2048Gray=tr` |
| 5 | POST | 200 | REST | `https://umdcv4.taobao.com/repTw.json?e=2075&sv=181&pv=234&pn=login.taobao.com&biz=0` |
| 6 | GET | 200 | REST | `https://ynuf.aliapp.org/w/wu.json` |
| 7 | POST | 200 | REST | `https://login.taobao.com/havanaone/loginLegacy/qrCode/query.do?bizEntrance=taobao_pc&bizName=taobao` |
| 8 | POST | 200 | REST | `https://umdcv4.taobao.com/repWd.json?e=2072&sv=181&pv=234&pn=login.taobao.com&biz=0&bx-umidtoken=T2gA2PerAGDglcmJ9T_ZuW_` |
| 9 | GET | 200 | REST | `https://wwc.alicdn.com/avatar/getAvatar.do?userIdStrV2=6xx9Fk4dSnfkRas9zXdf4NTT&type=taobao` |
| 10 | POST | 200 | REST | `https://login.taobao.com/havanaone/login/autoLogin/choose.do?token=sm2_weghsllxfujscrekkltbloq67cw7rwza&chooseNextAction` |
| 11 | GET | 302 | REST | `https://list.tmall.hk/search_product.htm` |
| 12 | GET | -1 | REST | `https://pages.tmall.com/wow/z/import/tmg-rax-home/tmallimportwupr-index?wh_pid=tmg-ch-tubes/fJiiCQT5DbMxQXAaQeGc&q=&spm=` |
| 13 | POST | 200 | REST | `https://umdcv4.taobao.com/repWd.json?e=2072&sv=181&pv=234&pn=login.taobao.com&biz=0&bx-umidtoken=T2gA2PerAGDglcmJ9T_ZuW_` |
| 14 | GET | 200 | REST | `https://assets.alicdn.com/apps/login/static/css/images/loading.gif` |
| 15 | GET | 200 | REST | `https://g.alicdn.com/sell/taobao/0.7.82/manifest.json` |
| 16 | GET | 200 | REST | `https://market.m.taobao.com/app/service-hall/scenario-widget/prefetcher.html?env=prod` |
| 17 | GET | 200 | REST | `https://turbo-meta.insights.1688.com/meta.json` |
| 18 | GET | 200 | REST | `https://servicehall.cdn.taobao.com/widget/prefetch/prod/resource.json?1777701988457` |
| 19 | GET | 200 | REST | `https://meta.m.taobao.com/app/detail-project/simple-sku/h5?h5=true&preview=true` |
| 20 | GET | 200 | REST | `https://market.m.taobao.com/app/item-decoration/detail-preview/index.html` |
| 21 | GET | 200 | REST | `https://sell.xiangqing.taobao.com/template/ajax/get_template.do?isAdescription=1&catId=202123606&itemId=1048651737918&cl` |
| 22 | GET | 200 | REST | `https://item.upload.taobao.com/sell/draftList.json?catId=202123606&globalExtendInfo=%7B%22startTraceId%22%3A%22215042cd1` |
| 23 | POST | 200 | REST | `https://item.upload.taobao.com/sell/v2/asyncOpt.htm?optType=querySaleLimitTemplate` |
| 24 | GET | 200 | REST | `https://g.alicdn.com/service-hall/pkg-meet/2.5.6/index.css` |
| 25 | GET | 200 | REST | `https://g.alicdn.com/service-hall/sh-rax-web/1.2.3/widget.js` |
| 26 | GET | 200 | REST | `https://g.alicdn.com/service-hall/sh-rax-web/1.2.3/widget.css` |
| 27 | GET | 200 | REST | `https://g.alicdn.com/detail-project/simple-sku/1.0.14/css/main.css` |
| 28 | GET | 200 | REST | `https://g.alicdn.com/mtb/lib-login/3.6.4/login.js` |
| 29 | GET | 200 | REST | `https://g.alicdn.com/detail-project/simple-sku/1.0.14/js/main.js` |
| 30 | GET | 302 | REST | `https://emogine.insights.1688.com/page-targeting/rule-item.upload.taobao.com.json` |
| 31 | GET | 200 | REST | `https://g.alicdn.com/item-decoration/detail-preview/0.0.9/static/js/lib-axios.eb7d5f88.js` |
| 32 | GET | 200 | REST | `https://g.alicdn.com/item-decoration/detail-preview/0.0.9/static/js/316.b6b24925.js` |
| 33 | GET | 200 | REST | `https://g.alicdn.com/item-decoration/detail-preview/0.0.9/static/js/index.a3731c9e.js` |
| 34 | GET | 200 | REST | `https://g.alicdn.com/item-decoration/detail-preview/0.0.9/static/css/index.19b33f30.css` |
| 35 | GET | 200 | REST | `https://emogine.insights.1688.com/empty.json` |
| 36 | GET | 200 | REST | `https://everyhelp.cdn.taobao.com/widget/queryServiceStrategy` |
| 37 | POST | 200 | REST | `https://wgo.mmstat.com/detail.simple-sku.Page_New_SKU_Preview_EXP` |
| 38 | GET | 200 | REST | `https://g.alicdn.com/service-hall/scenario-widget/1.7.50/index.js` |
| 39 | GET | 200 | REST | `https://everyhelp.taobao.com/api/monitor?api=init&args=%257B%2522routeId%2522%253A85403%252C%2522widgetStyle%2522%253A%2` |
| 40 | GET | 200 | REST | `https://helpcenter.taobao.com/servicehall/widget/initial?routeId=85403&originUrl=https:%2F%2Fitem.upload.taobao.com%2Fse` |
| 41 | GET | 200 | REST | `https://helpcenter.taobao.com/servicehall/widget/guessV2?instanceId=84136&routeId=85403&sessionId=e4a64982e17a4766ad672a` |
| 42 | POST | 200 | REST | `https://gm.mmstat.com/service_hall.component.common` |
| 43 | POST | 200 | REST | `https://item.upload.taobao.com/sell/batch/image/detail` |
| 44 | POST | 200 | REST | `https://item.upload.taobao.com/sell/v2/asyncOpt.htm?optType=croRuleAsyncCheck&catId=202123606` |

---
*由 🐱 Web Scraping Analyzer v2 自动生成*