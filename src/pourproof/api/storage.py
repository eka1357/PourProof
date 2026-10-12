"""Ephemeral in-memory storage for inspection artifacts and sessions."""

from collections import OrderedDict
import threading
from typing import Optional, Tuple, Dict, Any


class EphemeralInspectionStore:
    """Bounded thread-safe in-memory cache for recent inspection results and images."""

    def __init__(self, capacity: int = 50) -> None:
        self._capacity = capacity
        self._lock = threading.Lock()
        self._results: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._images: OrderedDict[str, bytes] = OrderedDict()

    def store(self, inspection_id: str, result: Dict[str, Any], image_bytes: Optional[bytes] = None) -> None:
        with self._lock:
            # Enforce capacity
            if len(self._results) >= self._capacity:
                self._results.popitem(last=False)
            if image_bytes and len(self._images) >= self._capacity:
                self._images.popitem(last=False)

            self._results[inspection_id] = result
            if image_bytes:
                self._images[inspection_id] = image_bytes

    def get_result(self, inspection_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._results.get(inspection_id)

    def get_image(self, inspection_id: str) -> Optional[bytes]:
        with self._lock:
            return self._images.get(inspection_id)

    def clear(self) -> None:
        with self._lock:
            self._results.clear()
            self._images.clear()


# Global instance
inspection_store = EphemeralInspectionStore()
