# Shortlink Analytics

A small, self-hosted short-link service with SQLite analytics, a management CLI, a JSON API, and privacy-conscious click tracking.

**Author:** Radwan Abdulhadi Ahmed · رضوان عبدالهادي أحمد · [@rad03i2](https://github.com/rad03i2)

## English

### Overview
Shortlink Analytics turns long HTTP/HTTPS URLs into manageable slugs and records useful aggregate click information without storing visitor IP addresses, cookies, full referrer URLs, or browser fingerprints. It is useful for local tools, internal teams, campaigns, documentation links, and small self-hosted deployments.

### Why it exists
Many URL shorteners require an external account or send click data to a third party. This project keeps link definitions and analytics in a portable SQLite database under your control.

### Features
- Custom or cryptographically generated short slugs.
- HTTP 302 redirects with enable/disable controls.
- SQLite persistence with WAL mode and indexed click history.
- Total clicks, recent daily counts, and top referrer **hosts**.
- CLI for create/list/stats/enable/disable/serve.
- Read-only JSON endpoints for link inventory and statistics.
- URL validation: only absolute HTTP/HTTPS destinations; embedded credentials rejected.
- Privacy-conscious collection: no IP address, cookie, query-bearing referrer URL, or fingerprint storage.
- Python 3.10+; tested by CI across Linux, Windows, and macOS.

### Preview
```text
$ shortlink-analytics --db links.db create https://example.com/docs --slug docs
{
  "slug": "docs",
  "url": "https://example.com/docs",
  "active": true,
  "clicks": 0
}

$ shortlink-analytics --db links.db serve
# GET http://127.0.0.1:8080/docs -> 302 -> https://example.com/docs
```
For screenshots, run the service and capture the JSON returned by `/api/links` or `/api/links/docs/stats`; the project intentionally has no graphical dashboard.

### Requirements & installation
- Python 3.10+
- SQLite (included with normal Python builds)

```bash
git clone https://github.com/rad03i2/shortlink-analytics.git
cd shortlink-analytics
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
```

### Usage
```bash
shortlink-analytics --db links.db create https://example.com/guide --slug guide
shortlink-analytics --db links.db create https://example.com/automatic
shortlink-analytics --db links.db list
shortlink-analytics --db links.db stats guide
shortlink-analytics --db links.db disable guide
shortlink-analytics --db links.db enable guide
shortlink-analytics --db links.db serve --host 127.0.0.1 --port 8080
```
You can also run `python -m shortlink_analytics ...`.

### HTTP endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/links` | Link inventory and click totals |
| GET | `/api/links/<slug>/stats` | Link statistics |
| GET | `/<slug>` | Record a click and redirect |

Management is deliberately CLI-only, so a public HTTP deployment does not expose unauthenticated mutation endpoints.

### Configuration
`--db PATH` selects the SQLite database. `SHORTLINK_DB` provides its default value. No `.env` file or secret is required. `serve` defaults to `127.0.0.1:8080` so it is not accidentally exposed to a network.

### Project structure
```text
src/shortlink_analytics/
  core.py       validation, persistence, analytics
  app.py        Flask application and HTTP routes
  cli.py        management CLI
  __main__.py   python -m entry point
tests/           core and HTTP integration tests
.github/workflows/ci.yml
```

### Testing
```bash
python -m pip install -e ".[dev]"
python -m compileall -q src tests
python -m pytest
```
CI runs those checks plus a CLI smoke check on Python 3.10, 3.12, and 3.13 across Ubuntu, Windows, and macOS.

### Security & privacy
The application never needs an API key. SQL values are parameterized. Destination URLs reject non-HTTP schemes and embedded credentials. Click tracking stores timestamp, referrer **hostname only**, and a coarse user-agent family; it deliberately omits IP addresses, cookies, full referrers, and fingerprints. See [SECURITY.md](SECURITY.md). For Internet-facing use, place the app behind HTTPS and a production WSGI server/reverse proxy; Flask's built-in server is for local/development use.

### Limitations
- No authentication or multi-user authorization layer.
- No graphical dashboard; analytics are CLI/JSON only.
- SQLite is appropriate for modest single-service deployments, not high-volume distributed analytics.
- Referrer data may be absent because browsers and sites can suppress it.
- User-agent family parsing is intentionally coarse rather than a full browser/device parser.
- Links do not currently expire automatically.

### Optional roadmap
Authenticated administration, CSV analytics export, configurable retention, and an optional lightweight dashboard are reasonable future additions; none are required for the current core workflow.

### Contributing & license
See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under the [MIT License](LICENSE).

### Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **[@rad03i2](https://github.com/rad03i2)**

---

## العربية

### نظرة عامة
**Shortlink Analytics** خدمة صغيرة ذاتية الاستضافة لاختصار الروابط، مع قاعدة SQLite وتحليلات للنقرات وواجهة أوامر وواجهات JSON، مع تقليل البيانات التي يتم جمعها عن الزائر قدر الإمكان.

### لماذا يوجد المشروع؟
الكثير من خدمات اختصار الروابط تتطلب حسابًا خارجيًا أو ترسل بيانات النقرات إلى طرف ثالث. يحتفظ هذا المشروع بتعريفات الروابط والتحليلات داخل قاعدة SQLite محلية قابلة للنقل وتحت سيطرتك.

### المزايا
- إنشاء slug مخصص أو توليده عشوائيًا بصورة آمنة.
- إعادة توجيه HTTP 302 مع إمكانية تعطيل الرابط وإعادة تفعيله.
- تخزين SQLite مع WAL وفهرس لسجل النقرات.
- إجمالي النقرات، وعدد النقرات اليومي الحديث، وأهم نطاقات الإحالة.
- أوامر create وlist وstats وenable وdisable وserve.
- واجهات JSON للقراءة فقط لقائمة الروابط والإحصاءات.
- قبول روابط HTTP/HTTPS المطلقة فقط ومنع بيانات الدخول المضمنة في الرابط.
- لا يتم تخزين IP أو cookies أو رابط الإحالة الكامل أو بصمة المتصفح.

### المتطلبات والتثبيت
يتطلب Python 3.10 أو أحدث. SQLite مرفق عادةً مع Python.

```bash
git clone https://github.com/rad03i2/shortlink-analytics.git
cd shortlink-analytics
python -m venv .venv
python -m pip install -e .
```

### الاستخدام
```bash
shortlink-analytics --db links.db create https://example.com/guide --slug guide
shortlink-analytics --db links.db list
shortlink-analytics --db links.db stats guide
shortlink-analytics --db links.db disable guide
shortlink-analytics --db links.db enable guide
shortlink-analytics --db links.db serve --host 127.0.0.1 --port 8080
```
بعد التشغيل، زيارة `/guide` تسجل النقرة ثم تعيد التوجيه. يمكن استخدام `/api/links` و`/api/links/guide/stats` لقراءة البيانات. لا توجد لوحة رسومية حاليًا؛ يمكن التقاط معاينة من استجابة JSON عند الحاجة.

### الإعداد
الخيار `--db` يحدد مسار قاعدة البيانات، ويمكن استخدام `SHORTLINK_DB` كقيمة افتراضية. لا يحتاج المشروع إلى أسرار أو ملف `.env`. الخادم يستمع افتراضيًا على `127.0.0.1:8080` لتجنب كشفه للشبكة بالخطأ.

### بنية المشروع
المحرك والتحقق وقاعدة البيانات في `core.py`، ومسارات HTTP في `app.py`، وأوامر الإدارة في `cli.py`، والاختبارات في `tests/`، والتكامل المستمر في `.github/workflows/ci.yml`.

### الاختبارات
```bash
python -m pip install -e ".[dev]"
python -m compileall -q src tests
python -m pytest
```
ويشغّل CI الاختبارات وفحص الاستيراد وأمر الإصدار على Linux وWindows وmacOS وإصدارات Python المحددة في workflow.

### الأمان والخصوصية
لا يحتاج التطبيق إلى مفتاح API. استعلامات SQL تستخدم معاملات بدل دمج القيم داخل النص. يتم رفض المخططات غير HTTP/HTTPS وبيانات الدخول داخل URL. التحليلات تحفظ وقت النقرة واسم نطاق الإحالة وفئة مبسطة من User-Agent فقط، ولا تحفظ عنوان IP أو cookies أو رابط الإحالة الكامل أو بصمة الجهاز. راجع [SECURITY.md](SECURITY.md). عند النشر العام استخدم HTTPS وخادم WSGI إنتاجيًا أمام التطبيق.

### القيود
- لا توجد طبقة مصادقة أو صلاحيات متعددة المستخدمين.
- لا توجد لوحة رسومية؛ الإحصاءات عبر CLI وJSON.
- SQLite ليست مخصصة للتحليلات الموزعة ذات الأحمال الضخمة.
- قد لا يرسل المتصفح referrer أصلًا.
- تحليل User-Agent مبسط عمدًا.
- لا يوجد انتهاء تلقائي للروابط حاليًا.

### تطوير اختياري
يمكن مستقبلًا إضافة إدارة موثقة، وتصدير CSV، وسياسة احتفاظ، ولوحة خفيفة. هذه إضافات اختيارية وليست ادعاءات عن النسخة الحالية.

### المساهمة والترخيص
راجع [CONTRIBUTING.md](CONTRIBUTING.md). المشروع مرخص وفق [MIT](LICENSE).

### المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **[@rad03i2](https://github.com/rad03i2)**
