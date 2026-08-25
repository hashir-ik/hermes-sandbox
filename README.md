# hermes-sandbox

A deliberately small project used to test the Hermes Agent Dev Team pipeline
end to end. Nothing here is real — it exists so agents have somewhere safe to
create branches, write code, run tests and open pull requests.

## What's in it

- `pricing.py` — shopping cart pricing helpers
- `app.py` + `templates/` — a small Flask cart page over those helpers
- `tests/test_pricing.py` — the unit suite

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

The page is deliberately plain, but every element a test would want to
select carries a `data-testid`, and the cart collapses to stacked rows
below 30rem — so a spec that only runs at desktop width will miss a
layout the site actually ships.

## Why the UI exists

The QA stage of the pipeline is supposed to write and commit Playwright
specs. With only a Python library here it always took the "this repo has
no browser surface" path, so that half of the stage had never run. This
page exists to make it run.

**Playwright is deliberately not set up.** Setting it up is part of what
the QA stage is meant to do on a repo that lacks it, and pre-installing it
would skip the step being tested.

## A known bug, left in on purpose

`cart_total` sums `price` and ignores `quantity`, so the page shows
**£27.75** for a basket worth **£40.50**. It is wrong in the browser, not
only in a unit test — which is the point: it gives an end-to-end test
something true to catch.
