# Environments

هذا المستند هو المرجع الوحيد لروابط وحالة كل بيئة تشغيل في مشروع OpenLearn AI.

## نظرة عامة

| البيئة | الغرض | تعمل من | الحالة |
|---|---|---|---|
| `dev` | بيئة تطوير محلية على جهاز كل مطور | `docker compose -f infra/docker-compose.dev.yml up` | ✅ شغالة ومتحقق منها |
| `staging` | بيئة مشتركة لعروض الجمعة والاختبار المتكامل | كل push على `main` (لسه مش متصلة) | ⏳ قيد التخطيط |
| `prod` | بيئة الإنتاج النهائية | tagged releases فقط (لسه مش متصلة) | ⏳ قيد التخطيط |

## `dev` — التفاصيل

- **الطريقة**: Docker Compose، يشتغل بالكامل محليًا، مفيش أي حساب سحابي مطلوب.
- **الملفات**:
  - `infra/docker-compose.dev.yml` — يشغّل الـ backend + قاعدة بيانات PostgreSQL
  - `backend/Dockerfile` — يبني image الـ backend
- **كيفية التشغيل**:
```bash
  cd infra
  docker compose -f docker-compose.dev.yml up --build
```
- **الروابط المحلية**:
  - Backend: `http://localhost:8000`
  - Database: `localhost:5432` (user: `openlearn`, db: `openlearn_dev`)
- **تم التحقق**: 9 أغسطس 2026 — تم إرسال طلب GET فعلي واستقبال رد `200 OK` مع `{"Hello":"World"}`.

## `staging` و `prod` — قيد الانتظار

القرارات النهائية (المزود السحابي، الميزانية، الأولوية الزمنية) لسه معلقة، في انتظار اجتماع محمد صيام (Team Lead).

## الوصول والأسرار (Secrets)

- ممنوع رفع أي secrets حقيقية على Git — `.env` مضاف في `.gitignore`.
- أسرار `staging`/`prod` (لما تتحدد) هتتخزن في GitHub Environments، مش في الكود.

## المسؤول

Pod D (هشام) — التوثيق والتحديث المستمر مع أي تغيير في البنية التحتية.
