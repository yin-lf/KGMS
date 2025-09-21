import enum
import time
import threading
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set


class CacheType(enum.Enum):
    SEARCH = enum.auto()
    AUTHOR = enum.auto()
    PAPER = enum.auto()
    CATEGORY = enum.auto()
    OVERVIEW = enum.auto()


@dataclass
class CacheEntry:
    """A cache entry with metadata."""

    key: str
    cache_type: CacheType
    data: Any
    created_at: float
    accessed_at: float
    ttl: float
    dependencies: Set[str]  # IDs of entities this cache depends on


class CacheManager:
    """
    Intelligent cache manager that automatically invalidates cache entries
    when related data changes in the database.
    """

    def __init__(self, max_size: int = 10000, default_ttl: float = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()

        # Statistics
        self._stats = {"hits": 0, "misses": 0, "evictions": 0, "invalidations": 0}

        # Dependency tracking: entity_id -> set of cache keys that depend on it
        self._dependencies: Dict[str, Set[str]] = {}

    def _generate_key(self, cache_type: CacheType, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        # Convert all arguments to strings
        key_parts = [cache_type.value]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))

        # Create hash from key parts
        key_string = "|".join(str(key_parts))
        # Use built-in hash for simplicity and speed
        return hash(key_string)

    def get(self, cache_type: CacheType, *args, **kwargs) -> Optional[Any]:
        """Get a value from cache."""
        key = self._generate_key(cache_type, *args, **kwargs)

        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._stats["misses"] += 1
                return None

            # Check if expired
            current_time = time.time()
            if current_time - entry.created_at > entry.ttl:
                del self._cache[key]
                self._remove_dependencies(key)
                self._stats["misses"] += 1
                return None

            # Update access time
            entry.accessed_at = current_time
            self._stats["hits"] += 1
            return entry.data

    def put(
        self,
        cache_type: CacheType,
        data: Any,
        dependencies: Optional[List[str]] = None,
        ttl: Optional[float] = None,
        *args,
        **kwargs,
    ) -> str:
        """Put a value in cache with optional dependencies."""
        key = self._generate_key(cache_type, *args, **kwargs)

        if ttl is None:
            ttl = self.default_ttl

        if dependencies is None:
            dependencies = []

        current_time = time.time()
        entry = CacheEntry(
            key=key,
            cache_type=cache_type,
            data=data,
            created_at=current_time,
            accessed_at=current_time,
            ttl=ttl,
            dependencies=set(dependencies),
        )

        with self._lock:
            # Remove old entry if exists
            if key in self._cache:
                self._remove_dependencies(key)

            # Check cache size and evict if necessary
            if len(self._cache) >= self.max_size:
                self._evict_lru()

            # Add new entry
            self._cache[key] = entry

            # Update dependency tracking
            for dep_id in dependencies:
                if dep_id not in self._dependencies:
                    self._dependencies[dep_id] = set()
                self._dependencies[dep_id].add(key)

        return key

    def invalidate_by_entity(self, entity_id: str):
        """Invalidate all cache entries that depend on a specific entity."""
        with self._lock:
            if entity_id in self._dependencies:
                keys_to_invalidate = self._dependencies[entity_id].copy()

                for key in keys_to_invalidate:
                    if key in self._cache:
                        del self._cache[key]
                        self._remove_dependencies(key)
                        self._stats["invalidations"] += 1

                del self._dependencies[entity_id]

    def invalidate_by_type(self, cache_type: CacheType):
        """Invalidate all cache entries of a specific type."""
        with self._lock:
            keys_to_remove = [
                key
                for key, entry in self._cache.items()
                if entry.cache_type == cache_type
            ]

            for key in keys_to_remove:
                del self._cache[key]
                self._remove_dependencies(key)
                self._stats["invalidations"] += 1

    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._dependencies.clear()
            self._stats["invalidations"] += len(self._cache)

    def _evict_lru(self):
        """Evict the least recently used cache entry."""
        if not self._cache:
            return

        # Find LRU entry
        lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].accessed_at)

        del self._cache[lru_key]
        self._remove_dependencies(lru_key)
        self._stats["evictions"] += 1

    def _remove_dependencies(self, cache_key: str):
        """Remove dependency mappings for a cache key."""
        entry = self._cache.get(cache_key)
        if entry:
            for dep_id in entry.dependencies:
                if dep_id in self._dependencies:
                    self._dependencies[dep_id].discard(cache_key)
                    if not self._dependencies[dep_id]:
                        del self._dependencies[dep_id]

    def get_stats(self) -> Dict:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0

            return {
                "cache_size": len(self._cache),
                "max_size": self.max_size,
                "hit_rate": hit_rate,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "evictions": self._stats["evictions"],
                "invalidations": self._stats["invalidations"],
                "dependency_count": len(self._dependencies),
            }

    def get_cache_info(self) -> Dict:
        """Get detailed cache information for debugging."""
        with self._lock:
            cache_by_type = {}
            for entry in self._cache.values():
                cache_type = entry.cache_type.value
                if cache_type not in cache_by_type:
                    cache_by_type[cache_type] = 0
                cache_by_type[cache_type] += 1

            return {
                "total_entries": len(self._cache),
                "entries_by_type": cache_by_type,
                "dependencies": {k: len(v) for k, v in self._dependencies.items()},
                "stats": self.get_stats(),
            }


# Global cache manager instance
_CM = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _CM
    if _CM is None:
        _CM = CacheManager()
    return _CM


def invalidate_paper_cache(paper_id: str):
    """Invalidate all cache entries related to a paper."""
    cache_manager = get_cache_manager()
    cache_manager.invalidate_by_entity(f"paper:{paper_id}")


def invalidate_author_cache(author_name: str):
    """Invalidate all cache entries related to an author."""
    cache_manager = get_cache_manager()
    cache_manager.invalidate_by_entity(f"author:{author_name}")


def invalidate_category_cache(category_name: str):
    """Invalidate all cache entries related to a category."""
    cache_manager = get_cache_manager()
    cache_manager.invalidate_by_entity(f"category:{category_name}")


def invalidate_search_cache():
    """Invalidate all search cache entries."""
    cache_manager = get_cache_manager()
    cache_manager.invalidate_by_type(CacheType.SEARCH)


def invalidate_all_cache():
    """Invalidate all cache entries."""
    cache_manager = get_cache_manager()
    cache_manager.clear()
