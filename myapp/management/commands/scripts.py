import traceback
from selenium import webdriver
from django.core.management.base import BaseCommand
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from myapp.models import Products
import re
import logging
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Scrapes product data from Brooks Brothers sale page"

    def handle(self, *args, **options):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--start-maximized')
        # chrome_options.add_argument('--headless')  # Uncomment to run in headless mode

        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            logger.error("Error initializing WebDriver: %s", e)
            self.stdout.write(self.style.ERROR("Failed to initialize WebDriver."))
            return

        try:
            driver.get("https://brooksbrothers.in/collection/sale-men-polos-and-tshirt")

            wait = WebDriverWait(driver, 60)  # Increased to 60 seconds
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))  # Ensure the page is fully loaded

            last_height = driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scroll_attempts = 10

            product_elements = driver.find_elements(By.CLASS_NAME, "product-card")
            previous_product_count = len(product_elements)

            while scroll_attempts < max_scroll_attempts:
                try:
                    logger.info(f"Scrolling... Current height: {last_height}")
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    WebDriverWait(driver, 5).until(lambda d: len(driver.find_elements(By.CLASS_NAME, "product-card")) > previous_product_count)

                    new_product_count = len(driver.find_elements(By.CLASS_NAME, "product-card"))
                    if new_product_count == previous_product_count:
                        logger.info("No new products loaded, stopping scroll.")
                        break

                    previous_product_count = new_product_count
                    scroll_attempts += 1
                except TimeoutException:
                    logger.warning("TimeoutException during scrolling. Retrying...")
                    continue

            product_elements = driver.find_elements(By.CLASS_NAME, "product-card")

            data = []
            for product in product_elements:
                try:
                    name = product.find_element(By.CLASS_NAME, "product-name").text.strip()
                    price_elem = product.find_element(By.CLASS_NAME, "discount-price")
                    price = re.sub(r'[^\d.]', '', price_elem.text.strip())
                    image = product.find_element(By.CLASS_NAME, "image_slider").get_attribute("src")
                    link = product.find_element(By.TAG_NAME, 'a').get_attribute('href')

                    if not link:
                        logger.warning("No link found in product element. Skipping product.")
                        continue

                    # Visit product detail page to extract more info
                    driver.execute_script("window.open(arguments[0]);", link)
                    driver.switch_to.window(driver.window_handles[1])
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "product-details-bb"))
                    )

                    details_html = driver.find_element(By.CLASS_NAME, "product-details-bb").text

                    # Default values
                    gender = category = material = 'N/A'

                    # Gender Extraction
                    try:
                        gender_element = driver.find_element(By.XPATH, "//span[contains(text(),'Gender')]/following-sibling::span[@class='value']")
                        gender = gender_element.text.strip()
                    except Exception as e:
                        logger.warning("Error extracting gender: %s", e)

                    # Category Extraction
                    try:
                        category_element = driver.find_element(By.XPATH, "//span[contains(text(),'Category')]/following-sibling::span[@class='value']")
                        category = category_element.text.strip()
                    except Exception as e:
                        logger.warning("Error extracting category: %s", e)

                    # Material Extraction
                    try:
                        material_element = driver.find_element(By.XPATH, "//span[contains(text(),'Primary Material')]/following-sibling::span[@class='value']")
                        material = material_element.text.strip()
                    except Exception as e:
                        logger.warning("Error extracting material: %s", e)

                    details_combined = f"Gender: {gender}, Category: {category}, Material: {material}"

                    data.append({
                        "name": name,
                        "description": name,
                        "price": price,
                        "image": image,
                        "details": details_combined,
                    })

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                except Exception as e:
                    logger.warning("Error extracting product info: %s", e)
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])

            for item in data:
                try:
                    product_obj = Products.objects.create(
                        name=item['name'],
                        description=item['description'],
                        price=item['price'],
                        image=item['image'],
                        details=item['details'],
                    )
                    logger.info("Saved product: %s", product_obj)
                except Exception as e:
                    logger.error("Error saving product to database: %s", e)

            self.stdout.write(self.style.SUCCESS('Successfully scraped and saved products.'))

        except Exception as e:
            logger.error("An error occurred during scraping: %s", e)
            self.stdout.write(self.style.ERROR("An error occurred during scraping."))
            logger.error("An error occurred during scraping: %s", e)
            traceback.print_exc()
        finally:
            driver.quit()