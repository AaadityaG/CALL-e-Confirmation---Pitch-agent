# Build Plan — Conversational Order Agent (Hackathon)

Deadline: **Sep 14, 2026, 11:45 PM SGT**. Today: **Sep 6**. ~8 days.

## 0. North Star (MVP — the only thing that must work)

> Merchant places a COD order in the dev store → webhook hits FastAPI → CALL-E calls the customer → customer confirms order + accepts the upsell offer → FastAPI validates → Shopify order is genuinely edited (line item added) → dashboard shows before/after.

Everything else is cut if time runs out.

## 1. Integration decisions (make before writing code)

### CALL-E → use the one-shot Calls API, NOT tool-calling
- SDK: `pip install calle-ai` (server SDK). `CalleClient(api_key=...)`, `client.calls.create_and_wait(task=..., result_schema=...)`.
- **CALL-E only talks and returns structure.** FastAPI owns all Shopify writes. This removes the "agent tool" complexity and makes the demo reliable.
- `result_schema` (JSON Schema the call must satisfy). The agent prompt tells the AI the order context and the one offer.
- Webhook note: CALL-E delivers terminal events via `POST` webhook, de-dupe with `CALL-E-Event-Id` header. For the demo, `create_and_wait` is fine; webhook is the production path.

**Structured result shape (v1):**
```json
{
  "intent": "confirm_order | add_item | change_variant | cancel | escalate | other",
  "line_item_id": null,
  "variant_id": null,
  "quantity_delta": 0,
  "customer_confirmed": false,     // explicit "yes"
  "requested_total": null
}
```
- If `intent == other` or `customer_confirmed == false` → **no Shopify write. Escalate** (mark for merchant).

### Shopify → Admin GraphQL order editing
- Dev store + custom app. Scopes: `read_orders, write_orders, write_order_edits, read_products, read_customers`.
- Read order line items/variants via `order(id)` query.
- Edit flow (all three mutation steps):
  1. `orderEditBegin(id: <orderId>, quantity: <qty>)` → gives `calculatedOrder.id` (the editId)
  2. `orderEditAddLineItem(calculatedOrder.id, variantId, quantity)` (or update qty via `orderEditUpdateQuantity`)
  3. `orderEditCommit(calculatedOrder.id)` → returns the edited `order`; read `totalPrice` + line items after.
- **Spike this day 1** — Shopify restricts order editing on some orders (e.g. paid/fullfilled). Verify on a fresh test order that it actually works.

### Trigger
- Shopify webhook `orders/create` → FastAPI → fetch order → check COD / eligible → evaluate offers → `create_and_wait`.

## 2. Architecture

```
Shopify (dev store)
   │  orders/create webhook
   ▼
FastAPI ──► Neon Postgres (orders, offers, calls, order_actions)
   │  create call
   ▼
CALL-E ──► AI phone call ──► customer
   │  structured result
   ▼
FastAPI ── validate + offer match ──► Shopify GraphQL orderEditBegin/AddLineItem/Commit
   ▼
Dashboard (React) reads from FastAPI REST
```

## 3. Repo layout (monorepo)

```
backend/        FastAPI app
  app/main.py           # router wiring
  app/shopify_client.py # GraphQL query + order edit helper
  app/calle_client.py   # create_and_wait wrapper + result_schema
  app/offers.py         # offer matching + build prompt + validate result
  app/order_actions.py  # apply confirmed action to Shopify, record it
  app/webhooks.py       # order/create receiver, CALL-E result webhook
  app/db.py             # SQLModel/SQLAlchemy sync
  app/models.py         # Store, Offer, Order, Call, OrderAction
  app/routes_dashboard.py
  app/auth.py           # simple Shopify HMAC webhook verification
frontend/       Vite + React + Tailwind dashboard
  connect store / offers CRUD / calls list / orders + revenue
```

Keep the DB plain: 5 tables.

## 4. Data model (Neon Postgres)

- `stores` — shop_domain, access_token, scopes, installed_at
- `offers` — store_id, name, type (`buy_more_discount` for MVP), config JSON, active
- `orders` — store_id, shopify_order_id (unique), phone, total_original, total_updated, status
- `calls` — store_id, order_id, calle_call_id, status, result JSON, structured_result JSON, recording_path
- `order_actions` — call_id, action_type, payload JSON, shopify_edit_id, before_total, after_total, ok

## 5. Milestones (time-boxed)

### M1 — Sep 6–7: Accounts + spikes (unblocking, parallel)
- [ ] Shopify partner account + dev store + custom app, get store-front Admin token with above scopes.
- [ ] Make a test order in dev store (COD, a T-shirt product). **Manually run `orderEditBegin/Add/Commit` via GraphQL Playground and confirm it works** (biggest risk — kills it first).
- [ ] CALL-E dashboard → API key. `pip install calle-ai`; run `create_and_wait` on a real number with a result_schema; confirm structured result returns.
- [ ] Sign the repo skeleton: `backend/` + `frontend/` scaffolds.

Accept: order edit works in Playground on the real store; one real CALL-E call returns structured JSON.

### M2 — Sep 7–8: Backend core
- [ ] `shopify_client.py` — fetch order (line items, totals, variant ids), edit order (begin/add/update/commit), return post-edit total.
- [ ] `db.py` + `models.py` on Neon (5 tables).
- [ ] `webhooks.py` — broadcast style `orders/create` verifier (HMAC) + handler that loads order and persists to `orders`.
- [ ] Manual endpoint `POST /debug/call/{order_id}` to fire a call without webhook (for demo fallback).

Accept: hit `/debug/call` → order row exists; script edits that order end-to-end via GraphQL.

### M3 — Sep 8–9: CALL-E + offers + execution
- [ ] `offers.py` — MVP: "order contains line item X → suggest adding 1 more of same variant at 20% off". Offer to JSON prompt.
- [ ] `calle_client.py` — build task prompt (greeting, confirm order line, offer, explicit-confirm), attach `result_schema`, call.
- [ ] `order_actions.py` — given a structured result: guard (`customer_confirmed == true` AND intent in allowed set), run the Shopify edit, write `order_actions` + update `orders.total_updated`.
- [ ] CALL-E result webhook endpoint (de-dupe by `CALL-E-Event-Id`) → same executor.

Accept: real phone call → customer says yes → GraphQL shows line item added, total ₹999 → ₹1,798, rows written.

### M4 — Sep 9–10: Dashboard (React)
- [ ] Auth/setup screen — paste dev-store Admin token (hackathon-simple; real OAuth only if time).
- [ ] Offers page — create/toggle the one offer type.
- [ ] Calls & orders page — call status, result, before/after ₹, revenue delta.
- [ ] Revenue stat cards (calls, confirmed, upsells, additional revenue).

Accept: full demo walkable in browser off the real data.

### M5 — Sep 11–13: Harden + demo assets
- [ ] End-to-end dry run several times; record both sides of the phone call + Shopify before/after + dashboard (screen capture).
- [ ] Error handling: CALL-E unreachable, Shopify edit failure, `unsupported_region` → mark status, don't crash.
- [ ] README with setup steps + architecture diagram.
- [ ] Devpost description (what/why/how) + demo video.
- [ ] PR to `CALLE-AI/awesome-phone-call-agents` — add our skill under `skills/` or app under `apps/python/` (we "eventually submit our project contribution" — the requirement is a PR URL). Keep it minimal: a `README.md` + `SKILL.md` describing the order-confirm + upsell + Shopify-write skill. **Do this early (Sep 9) so reviewer cycles don't eat the deadline.**

### M6 — Sep 14: Submit
- [ ] Final video + Devpost submitted. Buffer for any submission friction.

## 6. Parallelization (if >1 dev)

- Track A (backend): M1.spikes → M2 → M3. 
- Track B (frontend): scaffold + offer form + read-only calls/orders pages against a mocked `GET` contract agreed in M2.
- Track C (biz): Devpost draft + video outline + PR skeleton from day 1 (cheap, no code dependency).

## 7. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Shopify order editing restricted on paid/fulfilled orders | Spike in M1; place fresh unpaid/COD test orders for demo; use `draft orders`→`mark as paid` trick only if needed. |
| CALL-E region/phone support (`unsupported_region`, outbound not available everywhere) | Verify during M1 spike with a real number we control; fallback = record audio-only demo of the transcript + result JSON. |
| `calle-ai` API surface differs from docs | M1 spike pins the real calls; keep all CALL-E code behind `calle_client.py` so only one file changes. |
| Webhooks can't reach localhost | Use `ngrok`/tunnel for dev; keep `/debug/call` as no-tunnel path. |
| Scope creep (P1 features) | No P1 unless P0 is 100% green at Sep 11. |
| Timezone slip | Treat deadline as **Sep 14, 12:00 PM local**, submit early Sep 14. |

## 8. Key open questions (confirm, don't block on)

1. Do we have Shopify + CALL-E accounts yet? (M1 = create if no.)
2. Which US/IN/phone region for the demo number? (Determines CALL-E region support.)
3. 1 merchant demo store or per-team? (1 for MVP.)
4. Team size → split per §6.