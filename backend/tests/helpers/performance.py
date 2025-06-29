# filename: backend/tests/helpers/performance.py

import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestPerformanceRecord:
    """Record of a single test's performance metrics."""
    test_name: str
    duration: float
    category: str
    timestamp: float


class PerformanceTracker:
    """Track and analyze test performance metrics."""
    
    def __init__(self):
        self.records: List[TestPerformanceRecord] = []
    
    def record_test(self, test_name: str, duration: float, category: str = "unknown"):
        """Record a test's performance metrics."""
        record = TestPerformanceRecord(
            test_name=test_name,
            duration=duration,
            category=category,
            timestamp=time.time()
        )
        self.records.append(record)
    
    def get_category_stats(self, category: str) -> Dict[str, float]:
        """Get performance statistics for a test category."""
        category_records = [r for r in self.records if r.category == category]
        if not category_records:
            return {}
        
        durations = [r.duration for r in category_records]
        return {
            "count": len(durations),
            "total": sum(durations),
            "average": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations)
        }
    
    def get_slowest_tests(self, category: Optional[str] = None, limit: int = 10) -> List[TestPerformanceRecord]:
        """Get the slowest tests, optionally filtered by category."""
        records = self.records
        if category:
            records = [r for r in records if r.category == category]
        
        return sorted(records, key=lambda r: r.duration, reverse=True)[:limit]
    
    def report_summary(self) -> str:
        """Generate a performance summary report."""
        lines = ["=== Test Performance Summary ==="]
        
        categories = set(r.category for r in self.records)
        for category in sorted(categories):
            stats = self.get_category_stats(category)
            if stats:
                lines.append(f"\n{category.upper()} Tests:")
                lines.append(f"  Count: {stats['count']}")
                lines.append(f"  Average: {stats['average']:.3f}s")
                lines.append(f"  Range: {stats['min']:.3f}s - {stats['max']:.3f}s")
                lines.append(f"  Total: {stats['total']:.3f}s")
        
        return "\n".join(lines)


def assert_api_test_performance(duration: float, max_expected: float = 0.5):
    """Assert that API test completed within performance target."""
    assert duration < max_expected, f"API test took {duration:.3f}s, expected < {max_expected}s"


def categorize_test_name(test_path: str) -> str:
    """Categorize a test based on its file path."""
    path = Path(test_path)
    
    if "integration/api" in str(path):
        return "api"
    elif "integration/crud" in str(path):
        return "crud"
    elif "integration" in str(path):
        return "integration"
    elif "unit" in str(path):
        return "unit"
    else:
        return "other"