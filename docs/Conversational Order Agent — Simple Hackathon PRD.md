# Conversational Order Agent for Shopify

## 1. What are we building?

An **AI phone agent for Shopify merchants**.

When a customer places an order, the AI calls them and has a natural conversation.

It can:

* Confirm the order
* Offer relevant deals or products
* Understand requests like "add one more" or "change the color"
* Actually update the Shopify order
* Cancel/recover an order when appropriate
* Escalate complicated situations to the merchant

### Simple idea:

> **Customer talks → AI understands → Shopify gets updated.**

---

## 2. Why are we building it?

Today, after a customer places an order, merchants mostly wait for the order to be delivered.

But during that time:

* COD customers may cancel or refuse orders
* Customers may want to change their order
* Merchants miss upselling opportunities
* Simple changes often require manual support

We're turning that post-purchase phone call into an **AI-powered commerce interaction**.

---

## 3. Example

Customer orders:

> 1 × T-shirt — ₹999 COD

AI calls:

> "Hi, I'm calling to confirm your order for one T-shirt at ₹999."

Customer:

> "Yes."

AI:

> "Great. You can add another T-shirt at 20% off. Would you like me to add one?"

Customer:

> "Sure."

AI:

> "That would make your total ₹1,798. Should I update your order?"

Customer:

> "Yes."

Then:

**Shopify order changes from:**

> 1 T-shirt → ₹999

to:

> 2 T-shirts → ₹1,798

That's our **main demo.**

---

## 4. What makes it different?

We're NOT building just:

> ❌ AI COD confirmation

We're building:

> ✅ **AI that can actually perform actions on the Shopify order.**

The important loop is:

**CALL-E → Customer → AI understands → FastAPI → Shopify**

The AI doesn't simply tell the merchant what the customer wants.

It can actually execute the approved action.

---

# 5. Main features

### Order Confirmation

AI confirms that the customer still wants the order.

### Smart Offers

Merchant can define offers such as:

* Buy 2 → 20% off
* Add product → discount
* Spend ₹999 → free shipping
* Product A → recommend Product B

### Order Changes

Customer can say:

> "Add another."

> "Remove one."

> "Change it to black."

And the agent can update the Shopify order.

### Cancellation / Recovery

Customer can cancel.

Or, when appropriate, the agent can help preserve the original order instead of losing the entire purchase.

### Human Handoff

If the request is complicated, the agent sends it to the merchant.

---

# 6. How the system works

```text
Customer places Shopify order
            ↓
         FastAPI
            ↓
       CALL-E calls
            ↓
      Customer talks
            ↓
       AI understands
            ↓
    ┌───────┼────────┐
    ↓       ↓        ↓
 Confirm   Offer   Change
    │       │        │
    └───────┼────────┘
            ↓
        FastAPI
            ↓
         Shopify
            ↓
      Order updated
```

---

# 7. Tech Stack

### Frontend

**React**

Used for the merchant dashboard where merchants can:

* Connect their store
* Configure offers
* View calls
* View order changes
* See revenue generated

### Backend

**FastAPI + Python**

Responsible for:

* Shopify integration
* CALL-E integration
* Offer logic
* Order validation
* Order modification
* Agent tools
* API endpoints

### Database

**Neon PostgreSQL**

Stores:

* Connected stores
* Orders
* Offers
* Calls
* Call outcomes
* Order actions

### Commerce

**Shopify Admin GraphQL API**

Used to:

* Read orders
* Read products/variants
* Read customer information where required
* Edit existing orders
* Change quantities
* Add/remove products

Shopify's current documentation recommends the GraphQL Admin API for new integrations and provides access to products, customers, orders, inventory and other store data.

### Voice

**CALL-E**

Used for:

* Making the phone call
* Conversational interaction
* Understanding customer responses
* Returning structured results
* Driving the phone-based task

CALL-E currently provides Python and TypeScript SDKs as well as a Developer API.

---

# 8. How will a merchant use it?

The merchant experience should be very simple.

### Step 1 — Install the Shopify app

Merchant installs our **Conversational Order Agent** app into their Shopify store.

### Step 2 — Connect the store

The app gets the required Shopify permissions.

### Step 3 — Configure offers

Merchant creates something like:

```text
Offer:

Buy 2 T-shirts
→ 20% discount
```

Or:

```text
Spend ₹999
→ Free shipping
```

### Step 4 — Enable AI calls

Merchant chooses which orders should receive calls.

For the MVP:

```text
COD orders → AI call
```

### Step 5 — Customer places an order

Shopify creates the order.

Our backend receives the relevant Shopify event.

### Step 6 — AI calls the customer

FastAPI sends the required order context to CALL-E.

CALL-E calls the customer.

### Step 7 — Customer talks naturally

For example:

> "Yes, confirm it."

or:

> "Actually, add another one."

or:

> "Can you change it to black?"

### Step 8 — Agent takes action

If the request is allowed:

```text
CALL-E
   ↓
FastAPI
   ↓
Validate
   ↓
Shopify
```

### Step 9 — Merchant sees the result

Dashboard:

```text
Order #1047

Original:   ₹999
Updated:   ₹1,798

Result:
Upsell accepted
```

---

# 9. Shopify Integration

Shopify is the actual commerce system.

We don't want to build a fake order system for the demo.

The order should genuinely exist in Shopify and the agent should genuinely modify it.

### Important Shopify capability

Shopify supports editing existing orders through the GraphQL Admin API.

For significant changes such as:

* adding/removing line items
* changing quantities
* modifying discounts

Shopify uses the order editing flow:

```text
orderEditBegin
      ↓
Apply changes
      ↓
orderEditCommit
```

The order-edit functionality requires the `write_order_edits` scope.

That is the core API capability behind our main demo.

### Shopify development

We'll use a **Shopify development store**, so we can build and test without using a real merchant store.

Shopify's development stores are specifically intended for app development/testing and can be connected to Shopify CLI.

---

# 10. Shopify Resources

### Shopify Developer Documentation

[Shopify Developer Docs](https://shopify.dev/docs?utm_source=chatgpt.com)

### Shopify APIs

[Shopify APIs & Tools](https://shopify.dev/docs/api?utm_source=chatgpt.com)

### Development Stores

[Shopify Development Stores](https://shopify.dev/docs/apps/build/stores/development-stores?utm_source=chatgpt.com)

### GraphQL Admin API

[Shopify GraphQL Admin API](https://shopify.dev/docs/api/admin-graphql?utm_source=chatgpt.com)

### Editing Existing Orders

[Shopify — Edit Existing Orders](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps/edit-orders?utm_source=chatgpt.com)

### Order Editing API

[Shopify — orderEditBegin](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditBegin?utm_source=chatgpt.com)

---

# 11. CALL-E Integration

CALL-E is responsible for the phone conversation.

Our backend is responsible for connecting the conversation to Shopify.

### Architecture

```text
CALL-E
   ↓
Customer conversation
   ↓
Customer intent
   ↓
Agent tool
   ↓
FastAPI
   ↓
Shopify
```

CALL-E supports several integration paths including:

* API
* Python SDK
* TypeScript SDK
* MCP
* Skills
* Plugins

For our architecture, **Python SDK/API + FastAPI** is the most natural starting point.

CALL-E's current Python SDK can be installed with:

```bash
pip install calle-ai
```

and its Developer API supports creating calls and retrieving call results.

---

# 12. CALL-E Resources

### CALL-E Developer Docs

[CALL-E Developer Docs](https://docs.heycall-e.com/?utm_source=chatgpt.com)

### CALL-E Integrations

[CALL-E Integrations GitHub](https://github.com/CALLE-AI/call-e-integrations?utm_source=chatgpt.com)

This contains the current SDK/API/MCP integration information and examples.

### CALL-E Awesome Phone Call Agents

[Awesome Phone Call Agents](https://github.com/CALLE-AI/awesome-phone-call-agents?utm_source=chatgpt.com)

This is the community repository where we will eventually submit our project contribution. It contains examples, skills, apps and safety patterns for phone-call agents.

---

# 13. Hackathon

### CALL-E: Your Code Is Calling

The hackathon asks developers to build a project using CALL-E's:

* SDK
* API
* MCP
* CLI
* or Skill

to create an impactful business/project use case.

Our project fits because the phone call isn't just a conversation.

It performs a real business workflow:

```text
Customer
   ↓
Phone conversation
   ↓
Intent
   ↓
Order action
   ↓
Shopify
```

---

# 14. Hackathon Requirements

Our submission needs to include:

### 1. Working project

The project must actually use CALL-E.

### 2. Public demonstration

We need to show the product working.

### 3. Devpost description

Explain:

* What we built
* Why it matters
* How it works

### 4. Demo video

Show the actual product and workflow.

### 5. CALL-E repository contribution

We need to open a pull request to:

[CALL-E Awesome Phone Call Agents Repository](https://github.com/CALLE-AI/awesome-phone-call-agents?utm_source=chatgpt.com)

and provide that PR URL in the Devpost submission.

### Deadline

**September 14, 2026 at 11:45 PM SGT.**

---

# 15. Hackathon MVP

We only need ONE killer flow to work perfectly:

> **Shopify Order → CALL-E Call → Customer accepts upsell → AI gets confirmation → Shopify Order actually changes.**

Everything else is secondary.

### P0 — Must work

* Shopify development store
* Shopify app
* FastAPI backend
* Shopify order retrieval
* CALL-E outbound call
* Customer conversation
* One merchant-defined offer
* Explicit customer confirmation
* Shopify order modification
* Basic React dashboard

### P1 — Add if we have time

* Cancellation recovery
* Product cross-sell
* Variant changes
* Human escalation
* Better analytics

---

# 16. What the merchant sees

A simple dashboard:

```text
AI Revenue Agent

Calls:              124
Orders confirmed:    97
Upsells:              18
Orders recovered:      9

Additional Revenue:
₹18,420
```

And individual call results:

```text
Order #1047

Original:     ₹999
Updated:     ₹1,798

Result:
Upsell accepted
```

---

# 17. Our Main Pitch

> **"What if an AI could call a Shopify customer after checkout and actually change the order based on the conversation?"**

CALL-E provides the voice conversation.

Our system provides the commerce intelligence.

Shopify performs the actual transaction.

### **We aren't building an AI that talks about orders.**

### **We're building an AI that can act on them.**

---

# 18. One-line Product Definition

> **A CALL-E-powered conversational commerce agent that turns post-purchase phone conversations into real Shopify actions.**
