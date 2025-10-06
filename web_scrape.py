import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import pandas as pd
import numpy as np
import json

funds_df = pd.read_csv("all_funds.csv")
funds_name_list = set(funds_df["fund_name"].str.strip())

options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome(options=options)

driver.get("https://www.valueresearchonline.com/")

email_box = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.ID, "email"))
)
email_box.send_keys("poojicj@gmail.com")

continue_btn = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.ID, "fc-btn"))
)
continue_btn.click()

funds_link = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.ID, "navbarDropdown-funds"))
)
funds_link.click()

explore_more = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "a.table-foot-link.vr-page-links.with-arrow-icon")
    )
)
driver.execute_script("arguments[0].scrollIntoView(true);", explore_more)
time.sleep(3)
driver.execute_script("arguments[0].click();", explore_more)
time.sleep(50)


fund_house_link = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.ID, "vr_fund-house"))
)
fund_house_link.click()

fund_house_checkbox = WebDriverWait(driver, 20).until(
    EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "#fundHouse input[type='checkbox']")
    )
)

for checkbox in fund_house_checkbox[1:]:
    if not checkbox.is_selected():
        driver.execute_script("arguments[0].click();", checkbox)
time.sleep(3)


category = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "a.nav-link.fund-filter[href='#category']")
    )
)
driver.execute_script("arguments[0].click();", category)

all_equity_checkbox = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.ID, "primary_cat_id-1"))
)
if not all_equity_checkbox.is_selected():
    driver.execute_script("arguments[0].click();", all_equity_checkbox)
time.sleep(3)

apply = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.ID, "run_screen"))
)
apply.click()
time.sleep(50)

print("Filter applied...")

funds_data = []

rows = WebDriverWait(driver, 20).until(
    EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "#funds_screener_table tbody tr")
    )
)

total_rows = len(rows)
for i in range(total_rows):
    row = rows[i]
    fund_name_ele = row.find_element(By.CSS_SELECTOR, "td a")
    fund_name = fund_name_ele.text.strip()

    if fund_name not in funds_name_list:
        continue

    columns = row.find_elements(By.CSS_SELECTOR, "td")
    category = columns[4].find_element(By.CSS_SELECTOR, "a.hyperlink.category")
    category_title = category.get_attribute("data-original-title")

    scrapped_data = {
        "fund_name": fund_name,
        "category": category_title,
    }

    print(f"\n>>> Processing {fund_name}...")

    driver.execute_script("arguments[0].click();", fund_name_ele)

    nav_value = np.nan
    try:
        nav_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "p.fd-values.growth-title")
            )
        )
        nav_value = nav_element.text
    except TimeoutException:
        print("No NAV value found")
    scrapped_data["nav_value"] = nav_value

    try:
        return_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(@class,'fund_details_tab') and @href='#performance']",
                )
            )
        )
        driver.execute_script("arguments[0].click();", return_link)

        returns_table = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "return_over_time_table"))
        )

        headers = [
            th.text.strip()
            for th in returns_table.find_elements(By.CSS_SELECTOR, "thead th")
        ]
        data_rows = returns_table.find_elements(By.CSS_SELECTOR, "tbody tr")

        if len(data_rows) >= 2:
            fund_cells = data_rows[0].find_elements(By.TAG_NAME, "td")
            fund_row_data = {
                headers[j]: fund_cells[j].text.strip() for j in range(len(fund_cells))
            }
            scrapped_data.update(
                {
                    "fund_ytd": fund_row_data.get("YTD", "N/A"),
                    "fund_1y": fund_row_data.get("1Y", "N/A"),
                    "fund_3y": fund_row_data.get("3Y", "N/A"),
                    "fund_5y": fund_row_data.get("5Y", "N/A"),
                }
            )

            benchmark_cells = data_rows[1].find_elements(By.TAG_NAME, "td")
            benchmark_row_data = {
                headers[j]: benchmark_cells[j].text.strip()
                for j in range(len(benchmark_cells))
            }
            scrapped_data.update(
                {
                    "benchmark_name": benchmark_row_data.get("Fund name", "N/A"),
                    "benchmark_ytd": benchmark_row_data.get("YTD", "N/A"),
                    "benchmark_1y": benchmark_row_data.get("1Y", "N/A"),
                    "benchmark_3y": benchmark_row_data.get("3Y", "N/A"),
                    "benchmark_5y": benchmark_row_data.get("5Y", "N/A"),
                }
            )
    except TimeoutException:
        print("Returns tab not found")

    try:
        risk_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@class,'fund_details_tab') and @href='#risk']")
            )
        )
        driver.execute_script("arguments[0].click();", risk_link)

        risk_table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#risk table.datatable-fixedheader")
            )
        )

        risk_headers = [
            th.text.strip()
            for th in risk_table.find_elements(By.CSS_SELECTOR, "thead th")
        ][1:]
        data_rows = risk_table.find_elements(By.CSS_SELECTOR, "tbody tr")

        if len(data_rows) >= 2:
            fund_cells = data_rows[0].find_elements(By.TAG_NAME, "td")[1:]
            fund_risk = {
                risk_headers[j]: fund_cells[j].text.strip()
                for j in range(len(fund_cells))
            }
            scrapped_data.update(
                {
                    "fund_mean": fund_risk.get("Mean Return (%)"),
                    "fund_std_dev": fund_risk.get("Std Dev (%)"),
                    "fund_Sharpe": fund_risk.get("Sharpe (%)"),
                    "fund_Sortino": fund_risk.get("Sortino (%)"),
                    "fund_Beta": fund_risk.get("Beta (%)"),
                    "fund_Alpha": fund_risk.get("Alpha (%)"),
                }
            )

            benchmark_cells = data_rows[1].find_elements(By.TAG_NAME, "td")[1:]
            benchmark_risk = {
                risk_headers[j]: benchmark_cells[j].text.strip()
                for j in range(len(benchmark_cells))
            }
            scrapped_data.update(
                {
                    "benchmark_mean": benchmark_risk.get("Mean Return (%)"),
                    "benchmark_std_dev": benchmark_risk.get("Std Dev (%)"),
                    "benchmark_Sharpe": benchmark_risk.get("Sharpe (%)"),
                    "benchmark_Sortino": benchmark_risk.get("Sortino (%)"),
                }
            )
    except TimeoutException:
        print("Risk tab not found")

    try:
        portfolio_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(@class,'fund_details_tab') and @href='#fund-portfolio']",
                )
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", portfolio_link)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", portfolio_link)

        sector_table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "sector_wise-holding_table"))
        )
        sector_rows = sector_table.find_elements(
            By.CSS_SELECTOR, "tbody#sector_table_tooltip tr"
        )
        top3_sectors = []
        for row in sector_rows[:3]:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 3:
                sector_name = cols[0].text.strip()
                fund_percent = cols[1].text.strip()
                top3_sectors.append(
                    {"sector": sector_name, "fund_percent": fund_percent}
                )
        scrapped_data["top3_sector"] = top3_sectors
    except TimeoutException:
        print("Portfolio tab not found")
    try:
        other = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(@class,'fund_details_tab') and @href='#other']",
                )
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", other)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", other)

        def safe_text(xpath):
            try:
                return driver.find_element(By.XPATH, xpath).text.strip()
            except NoSuchElementException:
                return np.nan

        scrapped_data.update(
            {
                "fund_house": safe_text(
                    "//span[normalize-space(text())='Fund House']/following-sibling::span/a"
                ),
                "Type": safe_text(
                    "//span[normalize-space(text())='Type']/following-sibling::span"
                ),
                "Expense_ratio": safe_text(
                    "//span[normalize-space(text())='Expense']/following-sibling::span"
                ),
                "AMC": safe_text(
                    "//span[normalize-space(text())='AMC']/following-sibling::span"
                ),
                "Benchmark": safe_text(
                    "//span[normalize-space(text())='Benchmark']/following-sibling::span"
                ),
            }
        )

        try:
            fund_manager_element = driver.find_element(
                By.CSS_SELECTOR, "div#fund-manager p.v2-p--section-desc"
            )
            fund_manager_text = fund_manager_element.text.strip()
            fund_manager_name = fund_manager_text.split(" since")[0]
        except NoSuchElementException:
            fund_manager_name = np.nan
        scrapped_data["Fund Manager"] = fund_manager_name

    except TimeoutException:
        print("Other tab not found")
    funds_data.append(scrapped_data)
    with open("scrape_sep30.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(scrapped_data, ensure_ascii=False, indent=4) + ",\n")

    driver.back()
    time.sleep(5)

    rows = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "#funds_screener_table tbody tr")
        )
    )

print("Scraping finished!")
print(f"Total scraped: {len(funds_data)} funds")

with open("equity_data.json", "w", encoding="utf-8") as f:
    json.dump(funds_data, f, ensure_ascii=False, indent=4)

print("All equity fund data saved to equity_data.json")
