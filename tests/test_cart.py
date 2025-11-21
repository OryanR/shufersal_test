from utils.helpers import search_item, add_first_item_to_cart, close_popup_window, verify_first_item_added_to_cart, \
    go_to_checkout, verify_login_page_by_url, verify_login_page_by_element


def test_add_first_item_to_cart(page):
    search_term = "חלב"
    products = search_item(page, search_term)
    assert products, f"No products found for '{search_term}'"
    add_first_item_to_cart(page, products[0])
    close_popup_window(
        page)  # apparently there is a popup window if you are not logged in and trying to add item to the cart
    assert verify_first_item_added_to_cart(page, products[0])

def test_login_page_on_checkout(page):
    search_term = "חלב"
    products = search_item(page, search_term)
    add_first_item_to_cart(page, products[0])
    close_popup_window(page)
    go_to_checkout(page)
    assert verify_login_page_by_url(page)
    assert verify_login_page_by_element(page)