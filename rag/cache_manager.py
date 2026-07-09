"""
Cache Manager for BM25 and other retrievers
Stores indices in session to avoid rebuilding on every query
"""

import pickle
import os
from typing import Optional, Any


class CacheManager:
    """
    Simple cache manager for storing retriever objects
    Uses pickle for serialization
    """

    def __init__(self, cache_dir: str = "cache"):
        """
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve cached object by key

        Args:
            key: Cache key

        Returns:
            Cached object or None if not found
        """
        cache_path = os.path.join(self.cache_dir, f"{key}.pkl")

        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading cache for {key}: {e}")
            return None

    def set(self, key: str, value: Any) -> bool:
        """
        Store object in cache

        Args:
            key: Cache key
            value: Object to cache

        Returns:
            True if successful, False otherwise
        """
        cache_path = os.path.join(self.cache_dir, f"{key}.pkl")

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            return True
        except Exception as e:
            print(f"Error saving cache for {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete cached object

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        cache_path = os.path.join(self.cache_dir, f"{key}.pkl")

        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                return True
            except Exception as e:
                print(f"Error deleting cache for {key}: {e}")
                return False

        return False

    def clear_all(self) -> bool:
        """
        Clear all cache files

        Returns:
            True if successful, False otherwise
        """
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.pkl'):
                    os.remove(os.path.join(self.cache_dir, filename))
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Check if cache exists for key

        Args:
            key: Cache key

        Returns:
            True if cache exists, False otherwise
        """
        cache_path = os.path.join(self.cache_dir, f"{key}.pkl")
        return os.path.exists(cache_path)


# Global cache manager instance
_cache_manager = None


def get_cache_manager(cache_dir: str = "bm25_cache") -> CacheManager:
    """
    Get or create global cache manager instance

    Args:
        cache_dir: Directory for cache files

    Returns:
        CacheManager instance
    """
    global _cache_manager

    if _cache_manager is None:
        _cache_manager = CacheManager(cache_dir)

    return _cache_manager
