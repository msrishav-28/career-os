"""
Proxy service for reliable web scraping.

Per ELITE_REDESIGN_MASTER_PLAN.md §5.3 — Scraping Reliability:
  - Residential proxies (BrightData/Smartproxy)
  - Proxycurl or similar APIs as fallbacks
  - Hybrid strategy: Scrape → Proxy → API → Cache fallback

Per OPERATIONAL_RUNBOOK.md §2 — LinkedIn Scraping Blocked:
  - Proxy rotation
  - Proxycurl API fallback
  - Rate limit adjustment
"""
from typing import Any, Dict, Optional, Tuple
import logging
import os

from config.settings import settings
from services.feature_flags import feature_flags

logger = logging.getLogger(__name__)


class ProxyService:
    """
    Manages proxy rotation and fallback chain for web scraping.

    Strategy:
    1. Direct request (if flag disabled)
    2. Residential proxy (BrightData / Smartproxy)
    3. API fallback (Proxycurl)
    4. Cached response (Redis)
    """

    def __init__(self):
        # Proxy configuration from env
        self.brightdata_host = os.getenv("BRIGHTDATA_HOST", "")
        self.brightdata_port = os.getenv("BRIGHTDATA_PORT", "22225")
        self.brightdata_user = os.getenv("BRIGHTDATA_USER", "")
        self.brightdata_pass = os.getenv("BRIGHTDATA_PASS", "")
        self.proxycurl_key = os.getenv("PROXYCURL_API_KEY", "")

    def get_proxy_config(self) -> Optional[Dict[str, str]]:
        """
        Get proxy configuration if proxies are enabled.

        Returns None if proxies are disabled or not configured.
        """
        if not feature_flags.is_enabled("use_proxies"):
            return None

        if not self.brightdata_host or not self.brightdata_user:
            logger.warning("Proxy flag enabled but BrightData not configured")
            return None

        proxy_url = (
            f"http://{self.brightdata_user}:{self.brightdata_pass}"
            f"@{self.brightdata_host}:{self.brightdata_port}"
        )

        return {
            "http": proxy_url,
            "https": proxy_url,
        }

    async def fetch_linkedin_profile(
        self,
        linkedin_url: str,
        user_id: Optional[str] = None,
    ) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Fetch a LinkedIn profile using the fallback chain.

        Returns:
            (profile_data, source) where source is "direct"|"proxy"|"api"|"cache"
        """
        from services.redis_service import redis_service

        # 1. Check cache first
        cache_key = f"linkedin_profile:{linkedin_url}"
        cached = redis_service.get_json(cache_key)
        if cached:
            logger.info(f"LinkedIn profile cache hit: {linkedin_url}")
            return cached, "cache"

        # 2. Try direct scraping (if proxies disabled)
        if not feature_flags.is_enabled("use_proxies"):
            result = await self._scrape_direct(linkedin_url)
            if result:
                redis_service.set_json(cache_key, result, expiry=86400)  # 24h cache
                return result, "direct"

        # 3. Try proxy scraping
        proxy_config = self.get_proxy_config()
        if proxy_config:
            result = await self._scrape_with_proxy(linkedin_url, proxy_config)
            if result:
                redis_service.set_json(cache_key, result, expiry=86400)
                return result, "proxy"

        # 4. Try Proxycurl API fallback
        if self.proxycurl_key:
            result = await self._fetch_via_proxycurl(linkedin_url)
            if result:
                redis_service.set_json(cache_key, result, expiry=86400)
                return result, "api"

        logger.error(f"All LinkedIn fetch strategies failed for {linkedin_url}")
        return None, "failed"

    # ------------------------------------------------------------------
    # Internal strategies
    # ------------------------------------------------------------------
    async def _scrape_direct(self, url: str) -> Optional[Dict]:
        """Direct scraping without proxy."""
        try:
            from tools.linkedin_tools import LinkedInProfileTool
            tool = LinkedInProfileTool()
            result = tool._run(url)
            return {"raw": result} if result else None
        except Exception as e:
            logger.warning(f"Direct LinkedIn scrape failed: {e}")
            return None

    async def _scrape_with_proxy(
        self, url: str, proxy_config: Dict[str, str]
    ) -> Optional[Dict]:
        """Scraping through residential proxy."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    proxy=proxy_config.get("https"),
                    timeout=aiohttp.ClientTimeout(total=30),
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
                        ),
                    },
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        return {"raw_html": html[:5000]}  # Truncate for storage
                    else:
                        logger.warning(f"Proxy scrape returned {response.status}")
                        return None
        except Exception as e:
            logger.warning(f"Proxy LinkedIn scrape failed: {e}")
            return None

    async def _fetch_via_proxycurl(self, linkedin_url: str) -> Optional[Dict]:
        """Fetch profile via Proxycurl API."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://nubela.co/proxycurl/api/v2/linkedin",
                    params={"url": linkedin_url},
                    headers={"Authorization": f"Bearer {self.proxycurl_key}"},
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"Proxycurl returned {response.status}")
                        return None
        except Exception as e:
            logger.warning(f"Proxycurl API failed: {e}")
            return None


# Singleton
proxy_service = ProxyService()
