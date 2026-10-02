"""Orders robots from RobotSpareBin Industries Inc.
Saves the order HTML receipt as a PDF file.
Saves the screenshot of the ordered robot.
Embeds the screenshot of the robot to the PDF receipt.
Creates ZIP archive of the receipts and the images.
"""
from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import os


@task
def order_robots_from_RobotSpareBin():
    """Orders robots from RobotSpareBin Industries Inc."""
    browser.configure(
        slowmo=100,
    )
    open_robot_order_website()
    orders = get_orders()
    for row in orders:
        close_annoying_modal()
        fill_the_form(row)
        preview_robot()
        submit_order()
        order_number = row["Order number"]
        pdf_file = store_receipt_as_pdf(order_number)
        screenshot = screenshot_robot(order_number)
        embed_screenshot_to_receipt(screenshot, pdf_file)
        go_to_order_another_robot()
    archive_receipts()


def open_robot_order_website():
    """Navigates to the robot order website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def get_orders():
    """Downloads orders.csv and returns it as a table"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    tables = Tables()
    orders = tables.read_table_from_csv("orders.csv", header=True)
    return orders


def close_annoying_modal():
    """Clicks OK to dismiss the startup modal"""
    page = browser.page()
    try:
        page.click("button:text('OK')")
    except Exception:
        # Modal already closed on later orders - ignore
        pass


def fill_the_form(order):
    """Fills the order form for one row from orders.csv"""
    page = browser.page()
    # Head dropdown: value is 1-6 as string
    page.select_option("#head", str(order["Head"]))
    # Body radio: ids are id-body-1 ... id-body-6
    page.click(f"#id-body-{order['Body']}")
    # Legs input: id is dynamic, so use stable placeholder selector
    page.fill("input[placeholder='Enter the part number for the legs']", str(order["Legs"]))
    # Address input
    page.fill("#address", str(order["Address"]))


def preview_robot():
    """Clicks Preview and waits for robot image"""
    page = browser.page()
    page.click("#preview")
    page.wait_for_selector("#robot-preview-image")


def submit_order():
    """Clicks Order, retries while server error is visible"""
    page = browser.page()
    page.click("#order")
    # Server sometimes fails: .alert-danger appears, no receipt yet.
    # Docs rule: if error, click Order again.
    while page.locator(".alert-danger").is_visible():
        page.click("#order")
    # Ensure receipt loaded before continuing to PDF step
    page.wait_for_selector("#receipt")


def store_receipt_as_pdf(order_number):
    """Saves receipt HTML as PDF in output/, returns pdf path"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    os.makedirs("output/receipts", exist_ok=True)
    pdf_path = f"output/receipts/order_{order_number}.pdf"
    pdf = PDF()
    pdf.html_to_pdf(receipt_html, pdf_path)
    return pdf_path


def screenshot_robot(order_number):
    """Screenshots robot preview, returns png path"""
    page = browser.page()
    os.makedirs("output/screenshots", exist_ok=True)
    screenshot_path = f"output/screenshots/robot_{order_number}.png"
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path


def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Appends robot screenshot to receipt PDF"""
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)


def go_to_order_another_robot():
    """Clicks Order another robot to reset form"""
    page = browser.page()
    page.click("#order-another")


def archive_receipts():
    """Zips all PDFs to output/receipts.zip for Control Room"""
    archive = Archive()
    archive.archive_folder_with_zip("output/receipts", "output/receipts.zip")
