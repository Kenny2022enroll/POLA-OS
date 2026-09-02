import gc
import time

class MemoryService:
    """Heap watchdog that reclaims large objects before they exhaust RAM.

    Embedded ESP32 heaps fragment easily when big pages (frame buffers,
    item lists) are created and destroyed. This service nudges the runtime
    to collect earlier and performs an explicit full collection when free
    memory falls below a low-water mark.
    """
    # Collect when free heap drops below this many bytes.
    LOW_WATER = 6144
    MIN_INTERVAL_MS = 1000
    def __init__(self, low_water=None):
        if low_water is not None:
            self.LOW_WATER = low_water
        self.last_collect_ms = time.ticks_ms()
        # Ask the runtime to run its own GC before large allocations
        # exhaust the heap, so evicted page objects are reclaimed promptly.
        try:
            gc.threshold(self.LOW_WATER)
        except Exception:
            pass

    def free(self):
        try:
            return gc.mem_free()
        except Exception:
            return 0

    def pressure(self):
        return self.free() < self.LOW_WATER

    def collect(self, force=False):
        """Run a full GC. Returns free bytes afterwards, or None if skipped."""
        now = time.ticks_ms()
        if not force and time.ticks_diff(
                now, self.last_collect_ms) < self.MIN_INTERVAL_MS:
            return None
        self.last_collect_ms = now
        try:
            gc.collect()
        except Exception:
            pass
        return self.free()

    def collect_if_needed(self, force=False):
        if force or self.pressure():
            return self.collect(force=True)
        return None