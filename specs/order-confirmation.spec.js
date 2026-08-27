// @ts-check
const { test, expect } = require("@playwright/test");

/**
 * E2E specs for APP-12: Order confirmation panel on checkout.
 *
 * Acceptance criteria from the ticket:
 *   1. Checking out shows a confirmation panel with the heading "Order confirmed"
 *   2. The panel lists every item with its quantity and line total
 *   3. The panel shows the amount paid, matching the cart total including any discount
 *   4. The panel shows an order reference in the form ORD-00001
 *   5. Checking out with an empty cart shows "Your cart is empty" and no order reference
 *
 * Cart fixture: Notebook 4.50×3 + Pen 1.25×4 + Desk lamp 22.00×1 = £40.50
 *
 * Note on AC5: The app uses a fixed ITEMS constant that is never empty, so
 * the empty-cart checkout path is unreachable via the UI. The code handles
 * it defensively but cannot be exercised through E2E tests. Unit tests in
 * test_order_confirmation.py cover this path.
 */

test.describe("Order confirmation — APP-12", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  // ── AC 1: confirmation panel with "Order confirmed" heading ────

  test("checkout shows confirmation panel with 'Order confirmed' heading", async ({
    page,
  }) => {
    await page.getByTestId("checkout-button").click();

    const panel = page.getByTestId("confirmation-panel");
    await expect(panel).toBeVisible();

    const heading = page.getByTestId("confirmation-heading");
    await expect(heading).toBeVisible();
    await expect(heading).toHaveText("Order confirmed");
  });

  test("confirmation panel replaces the cart (cart table is gone)", async ({
    page,
  }) => {
    await page.getByTestId("checkout-button").click();

    await expect(page.getByTestId("confirmation-panel")).toBeVisible();
    await expect(page.getByTestId("cart")).toHaveCount(0);
    await expect(page.getByTestId("checkout-button")).toHaveCount(0);
  });

  // ── AC 2: line items with quantity and line total ──────────────

  test("confirmation lists all 3 items with correct names", async ({
    page,
  }) => {
    await page.getByTestId("checkout-button").click();

    const rows = page.getByTestId("confirmation-row");
    await expect(rows).toHaveCount(3);

    const names = page.getByTestId("conf-item-name");
    await expect(names.nth(0)).toHaveText("Notebook");
    await expect(names.nth(1)).toHaveText("Pen");
    await expect(names.nth(2)).toHaveText("Desk lamp");
  });

  test("confirmation shows correct quantities for each item", async ({
    page,
  }) => {
    await page.getByTestId("checkout-button").click();

    const qtys = page.getByTestId("conf-item-qty");
    await expect(qtys.nth(0)).toHaveText("3");
    await expect(qtys.nth(1)).toHaveText("4");
    await expect(qtys.nth(2)).toHaveText("1");
  });

  test("confirmation shows correct line totals for each item", async ({
    page,
  }) => {
    await page.getByTestId("checkout-button").click();

    const totals = page.getByTestId("conf-item-line-total");
    await expect(totals.nth(0)).toHaveText("£13.50"); // 4.50 × 3
    await expect(totals.nth(1)).toHaveText("£5.00"); // 1.25 × 4
    await expect(totals.nth(2)).toHaveText("£22.00"); // 22.00 × 1
  });

  // ── AC 3: amount paid matches cart total (no discount) ─────────

  test("amount paid shows £40.50 when no discount applied", async ({
    page,
  }) => {
    await page.getByTestId("checkout-button").click();

    const paid = page.getByTestId("paid-value");
    await expect(paid).toBeVisible();
    await expect(paid).toHaveText("£40.50");
  });

  // ── AC 3: amount paid with discount code ──────────────────────

  test("amount paid reflects SAVE10 discount (10% off = £36.45)", async ({
    page,
  }) => {
    await page.getByTestId("discount-code-input").fill("SAVE10");
    await page.getByTestId("apply-discount").click();

    await page.getByTestId("checkout-button").click();

    const paid = page.getByTestId("paid-value");
    await expect(paid).toHaveText("£36.45"); // 40.50 × 0.90
  });

  test("amount paid reflects SAVE20 discount (20% off = £32.40)", async ({
    page,
  }) => {
    await page.getByTestId("discount-code-input").fill("SAVE20");
    await page.getByTestId("apply-discount").click();

    await page.getByTestId("checkout-button").click();

    const paid = page.getByTestId("paid-value");
    await expect(paid).toHaveText("£32.40"); // 40.50 × 0.80
  });

  // ── AC 3: amount paid with manual percentage discount ─────────

  test("amount paid reflects manual 10% discount (£36.45)", async ({
    page,
  }) => {
    await page.getByTestId("discount-input").fill("10");
    await page.getByTestId("apply-discount").click();

    await page.getByTestId("checkout-button").click();

    const paid = page.getByTestId("paid-value");
    await expect(paid).toHaveText("£36.45"); // 40.50 × 0.90
  });

  // ── AC 4: order reference in ORD-NNNNN format ─────────────────

  test("confirmation shows an order reference matching ORD-NNNNN format", async ({
    page,
  }) => {
    await page.getByTestId("checkout-button").click();

    const ref = page.getByTestId("order-ref");
    await expect(ref).toBeVisible();
    await expect(ref).toHaveText(/^ORD-\d{5}$/);
  });

  // ── AC 5 note: empty cart ─────────────────────────────────────
  // The fixed ITEMS array is never empty, so the empty-cart branch
  // (data-testid="empty-cart" with "Your cart is empty") cannot be
  // reached through the browser. Unit tests cover it directly.
  // See tests/test_order_confirmation.py::test_empty_cart_*.
});

// ── Narrow viewport ─────────────────────────────────────────────

test.describe("Order confirmation — narrow viewport", () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test("checkout shows confirmation on narrow viewport", async ({ page }) => {
    await page.goto("/");
    await page.getByTestId("checkout-button").click();

    await expect(page.getByTestId("confirmation-panel")).toBeVisible();
    await expect(page.getByTestId("confirmation-heading")).toHaveText(
      "Order confirmed"
    );
    await expect(page.getByTestId("order-ref")).toHaveText(/^ORD-\d{5}$/);

    // All items still visible
    await expect(page.getByTestId("confirmation-row")).toHaveCount(3);
    await expect(page.getByTestId("paid-value")).toHaveText("£40.50");
  });

  test("checkout with SAVE10 on narrow viewport shows discounted total", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByTestId("discount-code-input").fill("SAVE10");
    await page.getByTestId("apply-discount").click();
    await page.getByTestId("checkout-button").click();

    await expect(page.getByTestId("confirmation-panel")).toBeVisible();
    await expect(page.getByTestId("paid-value")).toHaveText("£36.45");
  });
});
