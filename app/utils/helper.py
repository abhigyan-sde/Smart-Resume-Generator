import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from app.utils.constants import Constants

class Helper:
    @staticmethod
    def fetch_job_posting(url: str) -> str:
        """
        Fetch raw job posting HTML and extract readable text.
        For blocked job boards, return a message asking user to copy-paste the JD.
        All other URLs will be fetched automatically.
        """
        domain = urlparse(url).netloc.lower()

        if any(blocked in domain for blocked in Constants.BLOCKED_DOMAINS):
            # Federated board — require manual input
            return (
                "Automatic fetch not supported for this site. "
                "Please provide the job description text manually."
            )

        # Fetch allowed domains
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            raise ValueError(f"Unable to fetch job posting from {url}: {str(e)}")

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()
        text = " ".join(soup.stripped_strings)
        return text