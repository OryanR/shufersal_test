import time
import allure
import pytest
from utils.helpers import search_item

@allure.feature("Search")
@allure.story("Search results validate inclusion of search term")
def test_search_results_include_term(page, logger):
    search_term = "חלב"
    logger.info("Starting search test")

    try:
        with allure.step(f"Search for term: '{search_term}'"):
            products = search_item(page, search_term)

        with allure.step("Verify products were found"):
            assert products, f"No products found for '{search_term}'"

        with allure.step("Validate each product name contains the search term"):
            for name in products:
                assert search_term in name, (
                    f"Product name '{name}' does not include search term '{search_term}'"
                )

    except Exception as e:
        # Get browser version/name for screenshot
        browser_version = page.context.browser.version
        screenshot_path = f"screenshots/search_error_{search_term}_{browser_version}.png"

        with allure.step("Capture screenshot on failure"):
            page.screenshot(path=screenshot_path)
            allure.attach.file(
                screenshot_path,
                name="Failure Screenshot",
                attachment_type=allure.attachment_type.PNG,
            )

        logger.error(f"Search failed for '{search_term}': {e}")
        raise

@pytest.mark.parametrize("search_term", ["חלב", "לחם", "גבינה"])
def test_parallel_search(page, search_term):
    products = search_item(page, search_term)
    assert products, f"No products found for '{search_term}'"

def test_search_non_existing_item(page):
    search_term = "qwertyuiop"
    products = search_item(page, search_term)

    assert not products, f"Expected no products for '{search_term}', but some were found: {products}"
    no_results = page.locator("h2.textSearch")
    assert no_results.is_visible(), "'No results' message should be visible"

def test_functioning_after_search_special_characters(page):
    search_term = '!@#$%^'
    search_item(page, search_term)
    products = search_item(page, 'חלב')
    assert len(products) > 0

def test_search_loading_time(page):
    search_term = 'חלב'
    acceptable_loading_time = 2
    start_time = time.time()
    search_item(page, search_term)
    end_time = time.time()
    load_time = end_time - start_time
    print(f"\nstart time: " + str(start_time))
    print(f"\nend time: " + str(end_time))
    print(f"\nload time: " + str(load_time))
    assert load_time < acceptable_loading_time, f"loading time took more than {acceptable_loading_time} seconds"
