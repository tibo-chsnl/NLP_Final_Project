import { test, expect } from "@playwright/test";

test("full QA flow: ask question, get answer, send feedback", async ({ page }) => {
  await page.goto("/");

  await expect(page.locator("h1")).toContainText("Document QA");

  const contextInput = page.locator("textarea");
  await contextInput.fill(
    "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris. It was constructed from 1887 to 1889 as the centerpiece of the 1889 World Fair."
  );

  const questionInput = page.locator('input[type="text"]').first();
  await questionInput.fill("Where is the Eiffel Tower located?");

  await page.getByRole("button", { name: "Get Answer" }).click();

  const answerSection = page.locator("text=Answer").first();
  await expect(answerSection).toBeVisible({ timeout: 10000 });

  const thumbsUp = page.locator("text=Was this helpful?").locator("..").locator("button").first();
  await thumbsUp.click();

  await expect(page.locator("text=Thanks for your feedback")).toBeVisible();
});
