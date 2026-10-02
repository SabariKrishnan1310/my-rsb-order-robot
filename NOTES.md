# Level II Python - Tutor Notes

## 1. Package model
- `conda.yaml` = full env (python + rpaframework + robocorp + robocorp-browser). Lets clean clone run.
- `robot.yaml` = `python -m robocorp.tasks run tasks.py`, `artifactsDir: output`.
- `tasks.py:@task` = entry point. Docstring = robot description.

## 2. open + get_orders
- `browser.configure(slowmo=100)` then `browser.goto(.../#/robot-order)`.
- `HTTP().download(url=.../orders.csv, overwrite=True)` - robot fetches work, `overwrite=True` = re-runnable N times, no file-exists error.
- `Tables().read_table_from_csv(..., header=True)` -> list of dicts. `row["Order number"]`, `row["Head"]` etc. Must `return orders`.

## 3. close_annoying_modal
- Docs: use click + locator, learn CSS type/class/ID/attribute, XPath, text.
- `page.click("button:text('OK')")` - type + text selector.
- Wrapped in try/except - modal only first time, we call it in loop.

## 4. fill_the_form(order)
- `select_option("#head", str(...))` - dropdown, # = ID.
- `click(f"#id-body-{order['Body']}")` - radio cannot fill, must click.
- `fill("input[placeholder='Enter the part number for the legs']", ...)` - leg id is dynamic, use stable attribute selector.
- `fill("#address", ...)` - text input.
- Rule: dropdown=select, text=fill, radio/button=click.

## 5. preview + submit
- `preview`: `page.click("#preview")` + `wait_for_selector("#robot-preview-image")`. Yo-dawg step - must preview to get image.
- `submit`: `page.click("#order")`, while `.alert-danger` visible -> click again. Then `wait_for_selector("#receipt")`. Docs rule: complete all orders even with server failures.

## 6. store + screenshot + embed + next + zip (DONE per store-order-receipt-as-pdf + create-zip-file docs)
- `store_receipt_as_pdf(order_number)` takes number for unique name, returns path. `page.locator("#receipt").inner_html()` -> `PDF().html_to_pdf(html, output/receipts/order_<n>.pdf)`. Must be in `output/` for Control Room artifacts. Same pattern as Level I ch.11.
- `screenshot_robot(order_number)` same shape: arg in, path out. Uses already-imported browser lib: `page.locator("#robot-preview-image").screenshot(path=output/screenshots/robot_<n>.png)`.
- `embed_screenshot_to_receipt(screenshot, pdf_file)`: `PDF().add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)` - handles open/close, append=True = add to end not replace.
- `go_to_order_another_robot()`: `page.click("#order-another")` - resets for next loop iteration.
- `archive_receipts()`: `Archive().archive_folder_with_zip("output/receipts", "output/receipts.zip")` - Control Room does not support subdirs in artifacts, so single ZIP required.

## 7. Final steps (per final-steps + take-the-certification-exam docs)
- Verified: output/receipts/order_*.pdf (20), output/screenshots/robot_*.png, output/receipts.zip.
- Control Room: VS Code link to Control Room, Palette `Sema4.ai: Upload Task Package to Control Room` -> Create new Robot -> name -> Run in cloud.
- GitHub: public repo must contain tasks.py, conda.yaml, robot.yaml, README.md. Must run with no manual setup (auto-checker). Do NOT commit output/ or orders.csv (robot downloads it).
- Exam: https://robocorp.typeform.com/to/zvq45a2A - submit GitHub URL, unlimited retries, open-book. Pass = PDF certificate.
