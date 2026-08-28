// @ts-check
const { test, expect } = require("@playwright/test");

/**
 * E2E specs for BUG-1: Cart total ignores tax.
 *
 * Acceptance criteria from the ticket:
 *   1. Apply 20% tax to the cart total, after any discount has been taken off
 *   2. Show tax on the cart page as its own line, between the discount line
 *      and the total, using the same data-testid convention
 *
 * Cart fixture: Notebook 4.50×3 + Pen 1.25×4 + Desk lamp 22.00×1 = £40.50
 *
 * Expected values (all from the 20% rate stated in the ticket):
 *   No discount:  tax = 40.50 × 0.20 = £8.10,  grand = £48.60
 *   SAVE10 (10%): discounted = £36.45, tax = £7.29, grand = £43.74
 *   SAVE20 (20%): discounted = £32.40, tax = £6.48, grand = £38.88
 */

test.describe("Cart tax — BUG-1", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  // ── AC 1: Tax is shown on the cart page with no discount ──────

  test("tax line is visible with correct 20% value (no discount)", async ({
    page,
  }) => {
    const taxLine = page.getByTestId("tax");
    await expect(taxLine).toBeVisible();
    await expect(taxLine).toContainText("Tax (20%)");
    await expect(page.getByTestId("tax-value")).toHaveText("£8.10");
  });

  test("grand total includes tax (no discount)", async ({ page }) => {
    const grandTotal = page.getByTestId("grand-total");
    await expect(grandTotal).toBeVisible();
    await expect(page.getByTestId("grand-total-value")).toHaveText("£48.60");
  });

  test("subtotal is still shown separately from grand total", async ({
    page,
  }) => {
    // Subtotal unchanged at £40.50
    await expect(page.getByTestId("total-value")).toHaveText("£40.50");
    // Grand total is subtotal + tax
    await expect(page.getByTestId("grand-total-value")).toHaveText("£48.60");
  });

  // ── AC 1: Tax is applied after discount ───────────────────────

  test("tax is calculated on the discounted amount (SAVE10)", async ({
    page,
  }) => {
    await page.getByTestId("discount-code-input").fill("SAVE10");
    await page.getByTestId("apply-discount").click();

    // Discounted: 40.50 × 0.90 = 36.45
    await expect(page.getByTestId("discounted-value")).toHaveText("£36.45");
    // Tax on discounted: 36.45 × 0.20 = 7.29
    await expect(page.getByTestId("tax-value")).toHaveText("£7.29");
    // Grand total: 36.45 + 7.29 = 43.74
    await expect(page.getByTestId("grand-total-value")).toHaveText("£43.74");
  });

  test("tax is calculated on the discounted amount (SAVE20)", async ({
    page,
  }) => {
    await page.getByTestId("discount-code-input").fill("SAVE20");
    await page.getByTestId("apply-discount").click();

    // Discounted: 40.50 × 0.80 = 32.40
    await expect(page.getByTestId("discounted-value")).toHaveText("£32.40");
    // Tax on discounted: 32.40 × 0.20 = 6.48
    await expect(page.getByTestId("tax-value")).toHaveText("£6.48");
    // Grand total: 32.40 + 6.48 = 38.88
    await expect(page.getByTestId("grand-total-value")).toHaveText("£38.88");
  });

  test("tax recalculates when discount is applied by percentage", async ({
    page,
  }) => {
    await page.getByTestId("discount-input").fill("50");
    await page.getByTestId("apply-discount").click();

    // Discounted: 40.50 × 0.50 = 20.25
    await expect(page.getByTestId("discounted-value")).toHaveText("£20.25");
    // Tax on discounted: 20.25 × 0.20 = 4.05
    await expect(page.getByTestId("tax-value")).toHaveText("£4.05");
    // Grand total: 20.25 + 4.05 = 24.30
    await expect(page.getByTestId("grand-total-value")).toHaveText("£24.30");
  });

  // ── AC 2: Tax line placement — between discount and total ─────

  test("tax line appears between discount line and grand total in DOM order", async ({
    page,
  }) => {
    // Apply a discount so all three lines render
    await page.getByTestId("discount-code-input").fill("SAVE10");
    await page.getByTestId("apply-discount").click();

    // All three lines should be visible
    await expect(page.getByTestId("discounted-total")).toBeVisible();
    await expect(page.getByTestId("tax")).toBeVisible();
    await expect(page.getByTestId("grand-total")).toBeVisible();

    // Verify DOM order: discount < tax < grand-total
    // Get their bounding boxes — tax should be below discount and above grand total
    const discountBox = await page.getByTestId("discounted-total").boundingBox();
    const taxBox = await page.getByTestId("tax").boundingBox();
    const grandBox = await page.getByTestId("grand-total").boundingBox();

    expect(discountBox).toBeTruthy();
    expect(taxBox).toBeTruthy();
    expect(grandBox).toBeTruthy();

    // Tax is below discount line
    expect(taxBox.y).toBeGreaterThan(discountBox.y);
    // Tax is above grand total line
    expect(taxBox.y).toBeLessThan(grandBox.y);
  });

  test("tax line is between subtotal and grand total when no discount", async ({
    page,
  }) => {
    // No discount applied — discount line won't appear
    await expect(page.getByTestId("discounted-total")).toHaveCount(0);

    // Tax should be between subtotal and grand total
    const totalBox = await page.getByTestId("total").boundingBox();
    const taxBox = await page.getByTestId("tax").boundingBox();
    const grandBox = await page.getByTestId("grand-total").boundingBox();

    expect(totalBox).toBeTruthy();
    expect(taxBox).toBeTruthy();
    expect(grandBox).toBeTruthy();

    expect(taxBox.y).toBeGreaterThan(totalBox.y);
    expect(taxBox.y).toBeLessThan(grandBox.y);
  });

  // ── AC 2: data-testid convention ──────────────────────────────

  test("tax uses data-testid attributes consistent with the page", async ({
    page,
  }) => {
    // Container element
    await expect(page.getByTestId("tax")).toBeVisible();
    // Value span
    await expect(page.getByTestId("tax-value")).toBeVisible();
    // Grand total container and value
    await expect(page.getByTestId("grand-total")).toBeVisible();
    await expect(page.getByTestId("grand-total-value")).toBeVisible();
  });

  // ── Edge: invalid discount does not affect tax ────────────────

  test("invalid discount code still shows tax on full subtotal", async ({
    page,
  }) => {
    await page.getByTestId("discount-code-input").fill("BADCODE");
    await page.getByTestId("apply-discount").click();

    // Error shown, no discounted line
    await expect(page.getByTestId("error")).toBeVisible();
    await expect(page.getByTestId("discounted-total")).toHaveCount(0);

    // Tax is on the full subtotal
    await expect(page.getByTestId("tax-value")).toHaveText("£8.10");
    await expect(page.getByTestId("grand-total-value")).toHaveText("£48.60");
  });
});

// ── Narrow viewport ─────────────────────────────────────────────
// The Playwright config already runs on mobile (375×667), so these
// run at both viewports by default. This dedicated block exercises
// the tax display at the narrow breakpoint explicitly.

test.describe("Cart tax — narrow viewport", () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test("tax line and grand total render on narrow viewport", async ({
    page,
  }) => {
    await page.goto("/");

    await expect(page.getByTestId("tax")).toBeVisible();
    await expect(page.getByTestId("tax-value")).toHaveText("£8.10");
    await expect(page.getByTestId("grand-total")).toBeVisible();
    await expect(page.getByTestId("grand-total-value")).toHaveText("£48.60");
  });

  test("tax recalculates with discount on narrow viewport", async ({
    page,
  }) => {
    await page.goto("/");

    await page.getByTestId("discount-code-input").fill("SAVE10");
    await page.getByTestId("apply-discount").click();

    await expect(page.getByTestId("tax-value")).toHaveText("£7.29");
    await expect(page.getByTestId("grand-total-value")).toHaveText("£43.74");
  });
});
