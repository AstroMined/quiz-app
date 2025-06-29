# filename: backend/tests/helpers/performance.py

import time
import statistics
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
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
    
    def get_detailed_category_stats(self, category: str) -> Dict[str, float]:
        """Get detailed performance statistics for a test category."""
        category_records = [r for r in self.records if r.category == category]
        if not category_records:
            return {}
        
        durations = [r.duration for r in category_records]
        return {
            "count": len(durations),
            "total": sum(durations),
            "mean": statistics.mean(durations),
            "median": statistics.median(durations),
            "mode": statistics.mode(durations) if len(set(durations)) < len(durations) else durations[0],
            "std_dev": statistics.stdev(durations) if len(durations) > 1 else 0.0,
            "variance": statistics.variance(durations) if len(durations) > 1 else 0.0,
            "min": min(durations),
            "max": max(durations),
            "percentile_25": statistics.quantiles(durations, n=4)[0] if len(durations) >= 4 else min(durations),
            "percentile_75": statistics.quantiles(durations, n=4)[2] if len(durations) >= 4 else max(durations),
            "percentile_95": statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else max(durations),
            "percentile_99": statistics.quantiles(durations, n=100)[98] if len(durations) >= 100 else max(durations),
        }
    
    def compare_with_baseline(self, category: str, baseline_stats: Dict[str, float]) -> Dict[str, float]:
        """Compare current performance with baseline statistics."""
        current_stats = self.get_detailed_category_stats(category)
        if not current_stats or not baseline_stats:
            return {}
        
        comparison = {
            "baseline_mean": baseline_stats.get("mean", 0),
            "current_mean": current_stats["mean"],
            "mean_improvement": (baseline_stats.get("mean", 0) - current_stats["mean"]) / baseline_stats.get("mean", 1),
            "baseline_median": baseline_stats.get("median", 0),
            "current_median": current_stats["median"],
            "median_improvement": (baseline_stats.get("median", 0) - current_stats["median"]) / baseline_stats.get("median", 1),
            "baseline_p95": baseline_stats.get("percentile_95", 0),
            "current_p95": current_stats["percentile_95"],
            "p95_improvement": (baseline_stats.get("percentile_95", 0) - current_stats["percentile_95"]) / baseline_stats.get("percentile_95", 1),
            "meets_70_percent_target": (baseline_stats.get("mean", 0) - current_stats["mean"]) / baseline_stats.get("mean", 1) >= 0.70,
            "meets_80_percent_target": (baseline_stats.get("mean", 0) - current_stats["mean"]) / baseline_stats.get("mean", 1) >= 0.80,
        }
        
        return comparison
    
    def generate_performance_report(self, include_baselines: Optional[Dict[str, Dict[str, float]]] = None) -> str:
        """Generate a comprehensive performance report."""
        lines = ["=== Comprehensive Test Performance Report ==="]
        lines.append(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total tests recorded: {len(self.records)}")
        
        categories = set(r.category for r in self.records)
        for category in sorted(categories):
            detailed_stats = self.get_detailed_category_stats(category)
            if detailed_stats:
                lines.append(f"\n=== {category.upper()} TESTS ===")
                lines.append(f"  Count: {detailed_stats['count']}")
                lines.append(f"  Mean: {detailed_stats['mean']:.4f}s")
                lines.append(f"  Median: {detailed_stats['median']:.4f}s")
                lines.append(f"  Std Dev: {detailed_stats['std_dev']:.4f}s")
                lines.append(f"  Min: {detailed_stats['min']:.4f}s")
                lines.append(f"  Max: {detailed_stats['max']:.4f}s")
                lines.append(f"  P25: {detailed_stats['percentile_25']:.4f}s")
                lines.append(f"  P75: {detailed_stats['percentile_75']:.4f}s")
                lines.append(f"  P95: {detailed_stats['percentile_95']:.4f}s")
                lines.append(f"  P99: {detailed_stats['percentile_99']:.4f}s")
                
                if include_baselines and category in include_baselines:
                    baseline_stats = include_baselines[category]
                    comparison = self.compare_with_baseline(category, baseline_stats)
                    lines.append(f"\n  BASELINE COMPARISON:")
                    lines.append(f"    Mean improvement: {comparison['mean_improvement']*100:.1f}%")
                    lines.append(f"    Median improvement: {comparison['median_improvement']*100:.1f}%")
                    lines.append(f"    P95 improvement: {comparison['p95_improvement']*100:.1f}%")
                    lines.append(f"    Meets 70% target: {'✅' if comparison['meets_70_percent_target'] else '❌'}")
                    lines.append(f"    Meets 80% target: {'✅' if comparison['meets_80_percent_target'] else '❌'}")
        
        return "\n".join(lines)
    
    def save_results_to_file(self, filepath: str):
        """Save performance results to a JSON file."""
        results = {
            "timestamp": time.time(),
            "records": [asdict(record) for record in self.records],
            "categories": {}
        }
        
        categories = set(r.category for r in self.records)
        for category in categories:
            results["categories"][category] = self.get_detailed_category_stats(category)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
    
    @classmethod
    def load_results_from_file(cls, filepath: str) -> 'PerformanceTracker':
        """Load performance results from a JSON file."""
        tracker = cls()
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for record_data in data.get("records", []):
            record = TestPerformanceRecord(**record_data)
            tracker.records.append(record)
        
        return tracker
    
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