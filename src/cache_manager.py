import os
import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class CacheManager:
    """Manages campaign data caching for performance optimization"""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize cache manager
        
        Args:
            project_root: Root directory of the project (defaults to parent of this file)
        """
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(__file__))
        self.project_root = project_root
        self.cache_dir = Path(project_root) / "cache"
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_path(self) -> Path:
        """Get the path for the campaign cache file"""
        return self.cache_dir / "campaign_ids_cache.pkl"
    
    def load_campaign_cache(self) -> Optional[Dict]:
        """Load cached campaign IDs and member counts
        
        Returns:
            Dictionary with cache data or None if no valid cache
        """
        cache_path = self._get_cache_path()
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    cache_data = pickle.load(f)
                cache_date = cache_data.get('extraction_date')
                if cache_date:
                    days_old = (datetime.now() - cache_date).days
                    logging.info(f"Found campaign cache from {cache_date.strftime('%Y-%m-%d')} ({days_old} days old)")
                return cache_data
            except Exception as e:
                logging.warning(f"Failed to load cache: {e}")
        return None
    
    def save_campaign_cache(self, campaign_ids: List[str], member_counts: Dict[str, int], total_campaigns_queried: Optional[int] = None, member_limit: Optional[int] = None, months_back: Optional[int] = None):
        """Save campaign IDs and member counts to cache
        
        Args:
            campaign_ids: List of campaign IDs
            member_counts: Dictionary mapping campaign IDs to member counts
            total_campaigns_queried: Total number of campaigns queried in the original query
            member_limit: The member limit used to create this cache (None = unlimited)
            months_back: The months back parameter used for this cache (default: 12)
        """
        cache_path = self._get_cache_path()
        queried_count = total_campaigns_queried if total_campaigns_queried is not None else len(campaign_ids)
        cache_data = {
            'campaign_ids': campaign_ids,
            'member_counts': member_counts,
            'total_campaigns_queried': queried_count,
            'extraction_date': datetime.now(),
            'total_campaigns': len(campaign_ids),
            'total_members': sum(member_counts.values()),
            'member_limit': member_limit,
            'months_back': months_back if months_back is not None else 12
        }
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            member_limit_str = "unlimited" if member_limit == 0 or member_limit is None else str(member_limit)
            months_back_value = months_back if months_back is not None else 12
            logging.info(f"Saved campaign cache with {len(campaign_ids)} campaigns (queried: {queried_count}, member_limit: {member_limit_str}, months_back: {months_back_value})")
        except Exception as e:
            logging.error(f"Failed to save cache: {e}")
    
    def clear_cache(self):
        """Clear the campaign cache"""
        cache_path = self._get_cache_path()
        if cache_path.exists():
            cache_path.unlink()
            logging.info("Campaign cache cleared successfully")
        else:
            logging.info("No cache found to clear")
    
    def is_cache_compatible(self, requested_member_limit: int, requested_months_back: int = 12) -> bool:
        """Check if existing cache is compatible with requested member limit and months back
        
        Args:
            requested_member_limit: The member limit for the current request (0 = unlimited)
            requested_months_back: The months back for the current request (default: 12)
            
        Returns:
            True if cache can be used, False otherwise
        """
        cache_data = self.load_campaign_cache()
        if not cache_data:
            return False
            
        cached_member_limit = cache_data.get('member_limit')
        cached_months_back = cache_data.get('months_back', 12)  # Default to 12 for legacy cache
        
        # Handle legacy cache without member_limit (assume unlimited)
        if cached_member_limit is None:
            logging.warning("Cache missing member_limit info - assuming unlimited. Consider clearing cache.")
            cached_member_limit = 0
            
        # Check months_back compatibility - must be exact match for isolated time windows
        # This ensures users get exactly the time window they request, not broader datasets
        # Example: 6-month request should not use 18-month cache (would include unwanted campaigns)
        if cached_months_back != requested_months_back:
            logging.info(f"Cache incompatible: cached months ({cached_months_back}) != requested months ({requested_months_back})")
            return False
            
        # Check member_limit compatibility
        # If cached limit was unlimited (0), it can be used for any request
        if cached_member_limit == 0:
            return True
            
        # If requesting unlimited (0), only use cache if it was also unlimited
        if requested_member_limit == 0:
            return cached_member_limit == 0
            
        # For limited requests, cache can be used if it has equal or more data
        return cached_member_limit >= requested_member_limit

    def get_cache_info(self) -> Optional[Dict]:
        """Get information about the current cache
        
        Returns:
            Dictionary with cache information or None if no cache
        """
        cache_data = self.load_campaign_cache()
        if cache_data:
            extraction_date = cache_data.get('extraction_date')
            member_limit = cache_data.get('member_limit')
            months_back = cache_data.get('months_back', 12)  # Default to 12 for legacy cache
            member_limit_str = "unlimited" if member_limit == 0 or member_limit is None else str(member_limit)
            days_old = (datetime.now() - extraction_date).days if extraction_date else 0
            return {
                'extraction_date': extraction_date,
                'total_campaigns': cache_data.get('total_campaigns'),
                'total_members': cache_data.get('total_members'),
                'days_old': days_old,
                'member_limit': member_limit,
                'member_limit_str': member_limit_str,
                'months_back': months_back
            }
        return None 