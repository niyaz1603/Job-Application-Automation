"""Job scraping from LinkedIn, Indeed, and Naukri."""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class JobScraper:
    """Scrapes job listings from various job boards."""
    
    def __init__(self):
        """Initialize job scraper."""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        logger.info("✅ Job Scraper initialized")
    
    def scrape_indeed_jobs(
        self,
        roles: List[str],
        location: str = "India",
        limit: int = 50
    ) -> List[Dict]:
        """Scrape jobs from Indeed.
        
        Args:
            roles: List of job roles to search for
            location: Job location
            limit: Number of results
            
        Returns:
            List of job dictings
        """
        
        jobs = []
        
        for role in roles:
            try:
                logger.info(f"🔍 Scraping Indeed for: {role} in {location}")
                
                # Indeed URL construction
                url = f"https://www.indeed.co.in/jobs?q={role}&l={location}"
                
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Parse job listings
                job_cards = soup.find_all("div", class_="job_seen_beacon")
                
                for card in job_cards[:limit]:
                    try:
                        title_elem = card.find("h2", class_="jobTitle")
                        company_elem = card.find("span", class_="companyName")
                        location_elem = card.find("div", class_="companyLocation")
                        
                        if title_elem and company_elem:
                            job = {
                                "platform": "indeed",
                                "title": title_elem.text.strip(),
                                "company": company_elem.text.strip(),
                                "location": location_elem.text.strip() if location_elem else "Not specified",
                                "url": card.find("a")["href"] if card.find("a") else "N/A",
                                "scraped_at": datetime.now().isoformat()
                            }
                            jobs.append(job)
                    except Exception as e:
                        logger.warning(f"⚠️  Error parsing Indeed job: {str(e)}")
                        continue
                
                logger.info(f"✅ Found {len(job_cards)} jobs on Indeed")
                
            except Exception as e:
                logger.error(f"❌ Error scraping Indeed: {str(e)}")
        
        return jobs
    
    def scrape_naukri_jobs(
        self,
        roles: List[str],
        location: str = "India",
        limit: int = 50
    ) -> List[Dict]:
        """Scrape jobs from Naukri.com.
        
        Args:
            roles: List of job roles
            location: Job location
            limit: Number of results
            
        Returns:
            List of job dictings
        """
        
        jobs = []
        
        for role in roles:
            try:
                logger.info(f"🔍 Scraping Naukri for: {role}")
                
                # Naukri URL construction
                role_param = role.lower().replace(" ", "-")
                url = f"https://www.naukri.com/{role_param}-jobs"
                
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Parse job listings
                job_cards = soup.find_all("div", class_="sjw__jobCard")
                
                for card in job_cards[:limit]:
                    try:
                        title_elem = card.find("a", class_="title")
                        company_elem = card.find("a", class_="companyName")
                        location_elem = card.find("span", class_="loc")
                        
                        if title_elem and company_elem:
                            job = {
                                "platform": "naukri",
                                "title": title_elem.text.strip(),
                                "company": company_elem.text.strip(),
                                "location": location_elem.text.strip() if location_elem else "Not specified",
                                "url": title_elem["href"] if "href" in title_elem.attrs else "N/A",
                                "scraped_at": datetime.now().isoformat()
                            }
                            jobs.append(job)
                    except Exception as e:
                        logger.warning(f"⚠️  Error parsing Naukri job: {str(e)}")
                        continue
                
                logger.info(f"✅ Found {len(job_cards)} jobs on Naukri")
                
            except Exception as e:
                logger.error(f"❌ Error scraping Naukri: {str(e)}")
        
        return jobs
    
    def extract_job_description(self, job_url: str, platform: str) -> Optional[str]:
        """Extract full job description from job URL.
        
        Args:
            job_url: Job posting URL
            platform: Platform name (indeed/naukri/linkedin)
            
        Returns:
            Job description text
        """
        
        try:
            response = requests.get(job_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Platform-specific parsing
            if platform == "indeed":
                description = soup.find("div", id="jobDescriptionText")
            elif platform == "naukri":
                description = soup.find("div", class_="job-desc")
            else:
                description = soup.find("div", class_="description")
            
            if description:
                return description.get_text(separator="\n", strip=True)
            
            logger.warning(f"⚠️  Could not extract description from {job_url}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting job description: {str(e)}")
            return None
