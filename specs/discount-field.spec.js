// @ts-check
const { test, expect } = require("@playwright/test");

/**
 * E2E specs for BUG-16: Discount field is cleared when the value is invalid.
 *
 * Acceptance criteria from the ticket:
 *   1. An invalid discount value stays in the field after submitting
 *   2. The error message still appears
 *   3. A valid discount still applies and still displays in the field
 *   4. Existing behaviour for empty input is unchanged
 */

test.describe("Discount field — BUG-16 regression", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  // --- AC 1 & 2: invalid value stays, error shown ---

  test("invalid discount 'abc' stays in field after Apply", async ({
    page,
  }) => {
    const input = page.getByTestId("discount-input");
    await input.fill("abc");
    await page.getByTestId("apply-discount").click();

    // Field still contains the invalid value
    await expect(input).toHaveValue("abc");
    // Error message is visible
    const error = page.getByTestId("error");
    await expect(error).toBeVisible();
    await expect(error).toContainText("not a number");
  });

  test("invalid discount with special characters stays in field", async ({
    page,
  }) => {
    const input = page.getByTestId("discount-input");
    await input.fill("12%off");
    await page.getByTestId("apply-discount").click();

    await expect(input).toHaveValue("12%off");
    await expect(page.getByTestId("error")).toBeVisible();
  });

  // --- AC 3: valid discount applies and stays in the field ---

  test("valid discount '10' applies and stays in field", async ({ page }) => {
    const input = page.getByTestId("discount-input");
    await input.fill("10");
    await page.getByTestId("apply-discount").click();

    // Field retains value
    await expect(input).toHaveValue("10");
    // No error shown
    await expect(page.getByTestId("error")).toHaveCount(0);
    // Discounted total is visible
    await expect(page.getByTestId("discounted-total")).toBeVisible();
    await expect(page.getByTestId("discounted-total")).toContainText("10.0%");
  });

  // --- AC 4: empty input behaviour unchanged ---

  test("empty discount shows no error and no discounted total", async ({
    page,
  }) => {
    const input = page.getByTestId("discount-input");
    // Field starts empty
    await expect(input).toHaveValue("");
    // No error
    await expect(page.getByTestId("error")).toHaveCount(0);
    // No discounted total
    await expect(page.getByTestId("discounted-total")).toHaveCount(0);
  });

  test("submitting empty discount field keeps it empty, no error", async ({
    page,
  }) => {
    await page.getByTestId("apply-discount").click();

    await expect(page.getByTestId("discount-input")).toHaveValue("");
    await expect(page.getByTestId("error")).toHaveCount(0);
    await expect(page.getByTestId("discounted-total")).toHaveCount(0);
  });

  // --- Cart contents sanity (guards against blank page) ---

  test("cart table displays the expected items", async ({ page }) => {
    const rows = page.getByTestId("cart-row");
    await expect(rows).toHaveCount(3);

    const names = page.getByTestId("item-name");
    await expect(names.nth(0)).toHaveText("Notebook");
    await expect(names.nth(1)).toHaveText("Pen");
    await expect(names.nth(2)).toHaveText("Desk lamp");
  });
});
