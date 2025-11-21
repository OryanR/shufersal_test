def is_firefox(request):
    return request.param == "firefox"

# -------------------------
# Page functions / actions
# -------------------------

def search_item(page, search_term, timeout=10000):
    """
    Performs a search and waits for results, 'no results' message,
    or any dialog popup caused by special characters.
    Returns a list of product names (empty if no products found).
    """

    page.wait_for_load_state("domcontentloaded")

    search_input = page.locator("#js-site-search-input")
    search_input.wait_for(state="visible", timeout=timeout)

    dialog_triggered = {"flag": False}

    def handle_dialog(dialog):
        print(f"Dialog detected: {dialog.message}")
        dialog.dismiss()  # dismiss it
        dialog_triggered["flag"] = True

    page.on("dialog", handle_dialog)

    search_input.fill(search_term)
    search_input.press("Enter")

    page.wait_for_timeout(500)

    # handle search dialog
    if dialog_triggered["flag"]:
        print("Search blocked by dialog; returning empty list")
        return []

    # If no dialog, proceed to wait for search results
    products_selector = "#mainProductGrid [data-product-name]"
    no_results_selector = "h2.textSearch"

    try:
        page.wait_for_selector(f"{products_selector}, {no_results_selector}", timeout=timeout)
    except TimeoutError:
        raise Exception("Neither products nor no-results message appeared.")

    products_locator = page.locator(products_selector)
    no_results_locator = page.locator(no_results_selector)

    if products_locator.count() > 0:
        return page.eval_on_selector_all(
            products_selector,
            "elements => elements.map(el => el.getAttribute('data-product-name'))"
        )
    elif no_results_locator.is_visible():
        return []
    else:
        raise Exception("Cannot determine search result state.")

def add_first_item_to_cart(page, product_name):
    items = page.query_selector_all(f"#mainProductGrid [data-product-name='{product_name}']")
    if not items:
        raise ValueError(f"Product '{product_name}' not found")
    first_item = items[0]
    button = first_item.query_selector(".js-add-to-cart")
    if not button:
        raise ValueError("Add to cart button not found for the first item")
    button.click()

def close_popup_window(page):
    popup = page.locator("section.deliverySection.canDeliver")
    popup.wait_for(state="visible", timeout=8000)
    close_btn = popup.locator(".btnClose")
    close_btn.wait_for(state="visible", timeout=3000)
    close_btn.click()

def verify_first_item_added_to_cart(page, product_name):
    name_in_cart = get_first_item_name_from_cart(page)
    return name_in_cart == product_name

def get_first_item_name_from_cart(page):
    cart = page.locator(".miglog-prodlist")
    items = cart.locator(".miglog-cart-summary-prod-wrp.miglog-cart-prod-wrp:visible")
    name_link = items.nth(0).locator(
        "article.miglog-cart-prod- >> div.wrapper-miglog-prod-body >> div.miglog-prod-body >> h3.miglog-prod-name  >> a")
    name_link.wait_for(state="visible", timeout=5000)
    name = name_link.first.inner_text()
    return name

def go_to_checkout(page):
    button = page.locator(".title-btn")
    button.click()

def verify_login_page_by_url(page):
    return "login" in page.url

def verify_login_page_by_element(page):
    login_div = page.locator("div#loginWrapper")
    login_div.wait_for(state="visible", timeout=5000)
    return login_div.is_visible()