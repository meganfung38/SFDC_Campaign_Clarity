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
    
    def save_campaign_cache(self, campaign_ids: List[str], member_counts: Dict[str, int], total_campaigns_queried: Optional[int] = None):
        """Save campaign IDs and member counts to cache
        
        Args:
            campaign_ids: List of campaign IDs
            member_counts: Dictionary mapping campaign IDs to member counts
            total_campaigns_queried: Total number of campaigns queried in the original query
        """
        cache_path = self._get_cache_path()
        queried_count = total_campaigns_queried if total_campaigns_queried is not None else len(campaign_ids)
        cache_data = {
            'campaign_ids': campaign_ids,
            'member_counts': member_counts,
            'total_campaigns_queried': queried_count,
            'extraction_date': datetime.now(),
            'total_campaigns': len(campaign_ids),
            'total_members': sum(member_counts.values())
        }
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            logging.info(f"Saved campaign cache with {len(campaign_ids)} campaigns (queried: {queried_count})")
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
    
    def get_cache_info(self) -> Optional[Dict]:
        """Get information about the current cache
        
        Returns:
            Dictionary with cache information or None if no cache
        """
        cache_data = self.load_campaign_cache()
        if cache_data:
            extraction_date = cache_data.get('extraction_date')
            days_old = (datetime.now() - extraction_date).days if extraction_date else 0
            return {
                'extraction_date': extraction_date,
                'total_campaigns': cache_data.get('total_campaigns'),
                'total_members': cache_data.get('total_members'),
                'days_old': days_old
            }
        return None 