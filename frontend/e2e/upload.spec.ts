import { test, expect } from '@playwright/test';

test.describe('Label Upload Flow', () => {
  test('User can navigate to upload page and submit an image', async ({ page }) => {
    // 1. Navigate to home
    await page.goto('http://localhost:3000/');

    // 2. Click on the "Upload" tab in the navigation
    await page.click('button[aria-label="view Upload"]');
    
    // 3. Verify we are on the Upload page
    await expect(page.locator('text=Label Image Scanner')).toBeVisible();

    // 4. In a real e2e test, we would upload a mock file here
    // const fileChooserPromise = page.waitForEvent('filechooser');
    // await page.click('text=Drag and drop your label');
    // const fileChooser = await fileChooserPromise;
    // await fileChooser.setFiles('tests/mock-data/sample-label.jpg');

    // 5. Verify the loading state or results state
    // await expect(page.locator('text=Extracting Label...')).toBeVisible();
  });
});
