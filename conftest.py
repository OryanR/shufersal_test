import logging
import time
import pytest
import allure
import os
from playwright.sync_api import sync_playwright

browsers = ["chromium", "edge", "firefox"]

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.failed:
        # Get the 'page' fixture from the test, if it exists
        page = item.funcargs.get("page")
        if page:
            # Make folder if it doesn't exist
            os.makedirs("screenshots", exist_ok=True)

            # Save screenshot with test name
            browser_name = page.context.browser.browser_type.name
            screenshot_path = f"screenshots/{item.name}_{browser_name}.png"
            page.screenshot(path=screenshot_path)

            # Attach screenshot to Allure report
            allure.attach.file(
                screenshot_path,
                name="Failure Screenshot",
                attachment_type=allure.attachment_type.PNG
            )

@pytest.fixture(params=browsers)
def page(request):
    HEADLESS = os.environ.get("CI", "false") == "true"
    browser_name = request.param
    with sync_playwright() as p:
        if browser_name == "chromium":
            browser = p.chromium.launch(headless=HEADLESS)
        elif browser_name == "edge":
            browser = p.chromium.launch(channel="msedge", headless=HEADLESS)
        elif browser_name == "firefox":
            if browser_name == "firefox":
                pytest.skip("Skipping Firefox tests due to network/launch instability.")
            browser = p.firefox.launch(headless=HEADLESS)
        else:
            raise ValueError(f"Unsupported browser: {browser_name}")

        context = browser.new_context()
        page = context.new_page()
        time.sleep(1)
        page.goto("https://shufersal.co.il", wait_until="domcontentloaded", timeout=30000)
        yield page
        browser.close()

@pytest.fixture
def logger(request):
    test_name = request.node.name
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_path = f"{log_dir}/{test_name}.log"

    # Configure logger
    logger = logging.getLogger(test_name)
    logger.setLevel(logging.INFO)

    # Prevent adding duplicate handlers
    if not logger.handlers:
        fh = logging.FileHandler(log_path, mode="w", encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # after test, attach the log file
    yield logger

    if os.path.exists(log_path):
        allure.attach.file(
            log_path,
            name=f"{test_name} Log",
            attachment_type=allure.attachment_type.TEXT
        )
