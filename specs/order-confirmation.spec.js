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
 * Note on AC 5: the demo cart is a fixed in-memory array that is never empty,
 * so the empty-cart branch cannot be exercised end-to-end. It is covered by
 * unit tests (test_order_confirmation.py::TestEmptyCartCheckout). The E2E
 * specs verify the happy path only.
 */

test.describe("Order confirmation — APP-12", () => {
  // ── AC 1: heading "Order confirmed" ───────────────────────────

  test("checkout shows a confirmation panel with heading 'Order confirmed'", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByTestId("checkout-button").click();

    // We should be on the confirmation page
    const panel = page.getByTestId("confirmation-panel");
    await expect(panel).toBeVisible();

    const heading = page.getByTestId("confirmation-heading");
    await expect(heading).toBeVisible();
    await expect(heading).toHaveText("Order confirmed");
  });

  // ── AC 2: every item listed with quantity and line total ───────

  test("confirmation panel lists every item with quantity and line total", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByTestId("checkout-button").click();

    // Three items in the cart fixture
    const rows = page.getByTestId("order-row");
    await expect(rows).toHaveCount(3);

    // Notebook: 4.50 × 3 = £13.50
    const row0Name = page.getByTestId("order-item-name").nth(0);
    const row0Qty = page.getByTestId("order-item-qty").nth(0);
    const row0Total = page.getByTestId("order-item-total").nth(0);
    await expect(row0Name).toHaveText("Notebook");
    await expect(row0Qty).toHaveText("3");
    await expect(row0Total).toHaveText("£13.50");

    // Pen: 1.25 × 4 = £5.00
    const row1Name = page.getByTestId("order-item-name").nth(1);
    const row1Qty = page.getByTestId("order-item-qty").nth(1);
    const row1Total = page.getByTestId("order-item-total").nth(1);
    await expect(row1Name).toHaveText("Pen");
    await expect(row1Qty).toHaveText("4");
    await expect(row1Total).toHaveText("£5.00");

    // Desk lamp: 22.00 × 1 = £22.00
    const row2Name = page.getByTestId("order-item-name").nth(2);
    const row2Qty = page.getByTestId("order-item-qty").nth(2);
    const row2Total = page.getByTestId("order-item-total").nth(2);
    await expect(row2Name).toHaveText("Desk lamp");
    await expect(row2Qty).toHaveText("1");
    await expect(row2Total).toHaveText("£22.00");
  });

  // ── AC 3: amount paid matches cart total (no discount) ────────

  test("amount paid matches cart total when no discount is applied", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByTestId("checkout-button").click();

    const amountPaid = page.getByTestId("amount-paid");
    await expect(amountPaid).toBeVisible();
    await expect(page.getByTestId("amount-paid-value")).toHaveText("£40.50");
  });

  // ── AC 3: amount paid honours discount code ───────────────────

  test("amount paid matches discounted total when discount code is applied", async ({
    page,
  }) => {
    // Apply SAVE10 (10% off) via the cart page
    await page.goto("/");
    const codeInput = page.getByTestId("discount-code-input");
    await codeInput.fill("SAVE10");
    await page.getByTestId("apply-discount").click();

    // Verify the discount is applied on the cart page first
    await expect(page.getByTestId("discounted-value")).toHaveText("£36.45");

    // Now checkout
    await page.getByTestId("checkout-button").click();

    // Confirmation should show discounted amount: 40.50 × 0.90 = 36.45
    await expect(page.getByTestId("amount-paid-value")).toHaveText("£36.45");
  });

  test("amount paid matches discounted total with SAVE20 code", async ({
    page,
  }) => {
    await page.goto("/");
    const codeInput = page.getByTestId("discount-code-input");
    await codeInput.fill("SAVE20");
    await page.getByTestId("apply-discount").click();

    await expect(page.getByTestId("discounted-value")).toHaveText("£32.40");

    await page.getByTestId("checkout-button").click();

    // 40.50 × 0.80 = 32.40
    await expect(page.getByTestId("amount-paid-value")).toHaveText("£32.40");
  });

  // ── AC 4: order reference in ORD-00001 format ─────────────────

  test("confirmation panel shows an order reference in ORD-NNNNN format", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByTestId("checkout-button").click();

    const orderRef = page.getByTestId("order-ref");
    await expect(orderRef).toBeVisible();
    // The reference must match ORD- followed by 5 digits
    await expect(orderRef).toHaveText(/^ORD-\d{5}$/);
  });

  // ── AC 5: empty cart ──────────────────────────────────────────
  // The demo cart is a fixed in-memory array that is never empty.
  // The empty-cart path cannot be exercised E2E without server
  // modification. It is covered by unit tests:
  //   test_order_confirmation.py::TestEmptyCartCheckout (3 tests)

  // ── Confirmation page does NOT show the cart ───────────────────

  test("confirmation page replaces the cart — no cart table visible", async ({
    page,
  }) => {
    await page.goto("/");

    // Cart table is visible before checkout
    await expect(page.getByTestId("cart")).toBeVisible();

    await page.getByTestId("checkout-button").click();

    // After checkout, the cart table should be gone
    await expect(page.getByTestId("cart")).toHaveCount(0);
    // Confirmation panel is shown instead
    await expect(page.getByTestId("confirmation-panel")).toBeVisible();
  });

  // ── No checkout button or discount form on confirmation ───────

  test("confirmation page has no checkout button or discount form", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByTestId("checkout-button").click();

    await expect(page.getByTestId("checkout-button")).toHaveCount(0);
    await expect(page.getByTestId("discount-code-input")).toHaveCount(0);
    await expect(page.getByTestId("discount-input")).toHaveCount(0);
  });
});

// ── Narrow viewport ─────────────────────────────────────────────
// The Playwright config already runs on mobile (375×667), so these
// tests run at both viewports. This dedicated block exercises the
// checkout flow at the narrow breakpoint explicitly.

test.describe("Order confirmation — narrow viewport", () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test("checkout works on narrow viewport and shows all items", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByTestId("checkout-button").click();

    // Heading is visible
    await expect(page.getByTestId("confirmation-heading")).toHaveText(
      "Order confirmed"
    );

    // All items present
    await expect(page.getByTestId("order-row")).toHaveCount(3);

    // Amount paid visible
    await expect(page.getByTestId("amount-paid-value")).toHaveText("£40.50");

    // Order reference visible
    await expect(page.getByTestId("order-ref")).toBeVisible();
  });

  test("discounted checkout works on narrow viewport", async ({ page }) => {
    await page.goto("/");
    const codeInput = page.getByTestId("discount-code-input");
    await codeInput.fill("SAVE10");
    await page.getByTestId("apply-discount").click();

    await page.getByTestId("checkout-button").click();

    // 40.50 × 0.90 = 36.45
    await expect(page.getByTestId("amount-paid-value")).toHaveText("£36.45");
    await expect(page.getByTestId("order-row")).toHaveCount(3);
  });
});
