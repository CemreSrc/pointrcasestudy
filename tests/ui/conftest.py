import shutil
import pytest
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


def firefox_installed() -> bool:
    """Return True if a Firefox binary is available on PATH.

    We keep this simple and reliable across platforms by checking PATH only.
    """
    return shutil.which("firefox") is not None


def make_chrome() -> webdriver.Chrome:
    """Create a headless Chrome WebDriver with sane defaults for CI/local runs."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options,
    )


def make_firefox() -> webdriver.Firefox:
    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")
    try:
        return webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=options,
        )
    except (SessionNotCreatedException, WebDriverException) as e:
        pytest.skip(f"Firefox not available: {e}")


@pytest.fixture(params=["chrome", "firefox"] if firefox_installed() else ["chrome"])
def browser(request):
    name = request.param
    driver = make_chrome() if name == "chrome" else make_firefox()
    try:
        yield driver
    finally:
        driver.quit()
