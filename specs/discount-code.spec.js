// @ts-check
const { test, expect } = require("@playwright/test");

/**
 * E2E specs for APP-7: Discount code applies at checkout.
 *
 * Acceptance criteria from the ticket:
 *   1. SAVE10 applies 10% off; the code stays visible in the field
 *   2. SAVE20 applies 20% off; the code stays visible in the field
 *   3. Unrecognised code shows an error, total unchanged, code stays in field
 *   4. Empty code is not an error — page renders normally
 *   5. Codes are case-insensitive: save10 works the same as SAVE10
 *
 * Out-of-scope interaction: if both code and percentage are filled, code wins.
 *
 * Cart fixture: Notebook 4.50×3 + Pen 1.25×4 + Desk lamp 22.00×1 = £40.50
 */

test.describe("Discount code — APP-7", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  // ── AC 1: SAVE10 applies 10% off, code stays visible ──────────

  test("SAVE10 applies 10% off and stays in the field", async ({ page }) => {
    const codeInput = page.getByTestId("discount-code-input");
    await codeInput.fill("SAVE10");
    await page.getByTestId("apply-discount").click();

    // Code stays in the field
    await expect(codeInput).toHaveValue("SAVE10");

    // No error shown
    await expect(page.getByTestId("error")).toHaveCount(0);

    // Discounted total: 40.50 × 0.90 = 36.45
    const discounted = page.getByTestId("discounted-total");
    await expect(discounted).toBeVisible();
    await expect(page.getByTestId("discounted-value")).toHaveText("£36.45");
  });

  // ── AC 2: SAVE20 applies 20% off, code stays visible ──────────

  test("SAVE20 applies 20% off and stays in the field", async ({ page }) => {
    const codeInput = page.getByTestId("discount-code-input");
    await codeInput.fill("SAVE20");
    await page.getByTestId("apply-discount").click();

    // Code stays in the field
    await expect(codeInput).toHaveValue("SAVE20");

    // No error shown
    await expect(page.getByTestId("error")).toHaveCount(0);

    // Discounted total: 40.50 × 0.80 = 32.40
    const discounted = page.getByTestId("discounted-total");
    await expect(discounted).toBeVisible();
    await expect(page.getByTestId("discounted-value")).toHaveText("£32.40");
  });

  // ── AC 3: unrecognised code → error, total unchanged, code stays ──

  test("unrecognised code shows error, total unchanged, code stays", async ({
    page,
  }) => {
    const codeInput = page.getByTestId("discount-code-input");
    await codeInput.fill("NOTREAL");
    await page.getByTestId("apply-discount").click();

    // Code stays in the field
    await expect(codeInput).toHaveValue("NOTREAL");

    // Error message is visible
    const error = page.getByTestId("error");
    await expect(error).toBeVisible();
    await expect(error).toContainText("Unrecognised");

    // No discounted total — original total unchanged
    await expect(page.getByTestId("discounted-total")).toHaveCount(0);
    await expect(page.getByTestId("total-value")).toHaveText("£40.50");
  });

  // ── AC 4: empty code is not an error ──────────────────────────

  test("empty code is not an error — page renders normally", async ({
    page,
  }) => {
    // By default the field is empty
    await expect(page.getByTestId("discount-code-input")).toHaveValue("");

    // No error
    await expect(page.getByTestId("error")).toHaveCount(0);

    // No discounted total (no discount applied)
    await expect(page.getByTestId("discounted-total")).toHaveCount(0);

    // Cart still shows items and a total
    await expect(page.getByTestId("cart-row")).toHaveCount(3);
    await expect(page.getByTestId("total-value")).toHaveText("£40.50");
  });

  test("submitting with empty code field is not an error", async ({
    page,
  }) => {
    // Leave code field empty and click Apply
    await page.getByTestId("apply-discount").click();

    await expect(page.getByTestId("error")).toHaveCount(0);
    await expect(page.getByTestId("discounted-total")).toHaveCount(0);
    await expect(page.getByTestId("total-value")).toHaveText("£40.50");
  });

  // ── AC 5: case-insensitive ────────────────────────────────────

  test("lowercase 'save10' works the same as SAVE10", async ({ page }) => {
    const codeInput = page.getByTestId("discount-code-input");
    await codeInput.fill("save10");
    await page.getByTestId("apply-discount").click();

    // The typed code stays as-is (lowercase)
    await expect(codeInput).toHaveValue("save10");

    // Same discount applied: 10% off
    await expect(page.getByTestId("error")).toHaveCount(0);
    await expect(page.getByTestId("discounted-value")).toHaveText("£36.45");
  });

  test("mixed-case 'SaVe20' works the same as SAVE20", async ({ page }) => {
    const codeInput = page.getByTestId("discount-code-input");
    await codeInput.fill("SaVe20");
    await page.getByTestId("apply-discount").click();

    await expect(codeInput).toHaveValue("SaVe20");
    await expect(page.getByTestId("error")).toHaveCount(0);
    await expect(page.getByTestId("discounted-value")).toHaveText("£32.40");
  });

  // ── Out-of-scope interaction: code wins over percentage ───────

  test("when both code and percentage are filled, code wins", async ({
    page,
  }) => {
    const codeInput = page.getByTestId("discount-code-input");
    const pctInput = page.getByTestId("discount-input");

    await codeInput.fill("SAVE10");
    await pctInput.fill("50");
    await page.getByTestId("apply-discount").click();

    // 10% off (code), NOT 50% off (percentage)
    await expect(page.getByTestId("discounted-value")).toHaveText("£36.45");
    // 50% would give 20.25 — make sure that's absent
    await expect(page.getByTestId("discounted-total")).not.toContainText(
      "20.25"
    );
  });

  // ── Discount code field exists on the page ────────────────────

  test("discount code input is present on the cart page", async ({ page }) => {
    const codeInput = page.getByTestId("discount-code-input");
    await expect(codeInput).toBeVisible();
    await expect(codeInput).toHaveAttribute("placeholder", "Discount code");
  });
});

// ── Narrow viewport ─────────────────────────────────────────────
// The Playwright config already runs on mobile (375×667), so these
// tests run at both viewports. This dedicated block exercises the
// cart at the narrow breakpoint explicitly.

test.describe("Discount code — narrow viewport", () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test("SAVE10 applies correctly on a narrow viewport", async ({ page }) => {
    await page.goto("/");

    const codeInput = page.getByTestId("discount-code-input");
    await codeInput.fill("SAVE10");
    await page.getByTestId("apply-discount").click();

    await expect(codeInput).toHaveValue("SAVE10");
    await expect(page.getByTestId("error")).toHaveCount(0);
    await expect(page.getByTestId("discounted-value")).toHaveText("£36.45");

    // Cart rows still render
    await expect(page.getByTestId("cart-row")).toHaveCount(3);
  });

  test("unrecognised code shows error on narrow viewport", async ({
    page,
  }) => {
    await page.goto("/");

    const codeInput = page.getByTestId("discount-code-input");
    await codeInput.fill("BADCODE");
    await page.getByTestId("apply-discount").click();

    await expect(codeInput).toHaveValue("BADCODE");
    await expect(page.getByTestId("error")).toBeVisible();
    await expect(page.getByTestId("discounted-total")).toHaveCount(0);
  });
});
