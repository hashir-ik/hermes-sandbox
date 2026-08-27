# hermes-sandbox

A deliberately small project used to test the Hermes Agent Dev Team pipeline
end to end. Nothing here is real — it exists so agents have somewhere safe to
create branches, write code, run tests and open pull requests.

## What's in it

- `pricing.py` — shopping cart pricing helpers
- `app.py` + `templates/` — a small Flask cart page over those helpers
- `tests/` — the unit suite (pytest)
- `specs/` — the end-to-end suite (Playwright)

## Running the tests

```
pip install -r requirements.txt
python -m pytest
```

## Running the app

```
pip install -r requirements.txt
python app.py          # http://localhost:5000
```

## Running the end-to-end specs

```
npm ci
npx playwright install chromium
npm test
```

The page is deliberately plain, but every element a test would want to
select carries a `data-testid`, and the cart collapses to stacked rows
below 30rem — so a spec that only runs at desktop width will miss a
layout the site actually ships.

## Why the UI exists

The QA stage of the pipeline is supposed to write and commit Playwright
specs. With only a Python library here it always took the "this repo has
no browser surface" path, so that half of the stage had never run. This
page exists to make it run.

**Playwright was deliberately not set up.** Setting it up was part of what
the QA stage is meant to do on a repo that lacks it, and pre-installing it
would have skipped the step being tested.

On 2026-08-26 the QA stage did exactly that, unprompted: it installed
Playwright from scratch and committed `specs/discount-field.spec.js`. Three
earlier runs had read the same instruction and skipped it; the fourth met a
gate it could not complete past. The specs now run in CI (`.github/workflows/e2e.yml`).

## The bug that was left in on purpose

`cart_total` used to sum `price` and ignore `quantity`, so the page showed
**£27.75** for a basket worth **£40.50**. It was wrong in the browser, not
only in a unit test — which was the point: it gave an end-to-end test
something true to catch.

It was fixed by the pipeline and merged in #5. If you want a fresh one, break
something the specs cover and open a PR — CI will tell you.
