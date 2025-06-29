# filename: backend/tests/helpers/performance_regression.py

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from backend.tests.helpers.performance import PerformanceTracker, TestPerformanceRecord


@dataclass
class PerformanceBaseline:
    """Represents a performance baseline for regression detection."""
    category: str
    mean_duration: float
    median_duration: float
    p95_duration: float
    std_dev: float
    sample_size: int
    timestamp: float
    version: str = "unknown"
    description: str = ""


class PerformanceRegressionDetector:
    """Detects performance regressions by comparing against established baselines."""
    
    def __init__(self, baselines_file: str = "performance_baselines.json"):
        self.baselines_file = Path(baselines_file)
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.load_baselines()
    
    def load_baselines(self):
        """Load performance baselines from file."""
        if self.baselines_file.exists():
            try:
                with open(self.baselines_file, 'r') as f:
                    data = json.load(f)
                    for category, baseline_data in data.items():
                        self.baselines[category] = PerformanceBaseline(**baseline_data)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Warning: Could not load baselines from {self.baselines_file}: {e}")
    
    def save_baselines(self):
        """Save performance baselines to file."""
        data = {category: asdict(baseline) for category, baseline in self.baselines.items()}
        with open(self.baselines_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def establish_baseline(self, tracker: PerformanceTracker, category: str, 
                          version: str = "unknown", description: str = ""):
        """Establish a new performance baseline for a category."""
        stats = tracker.get_detailed_category_stats(category)
        if not stats:
            raise ValueError(f"No performance data found for category: {category}")
        
        baseline = PerformanceBaseline(
            category=category,
            mean_duration=stats["mean"],
            median_duration=stats["median"],
            p95_duration=stats["percentile_95"],
            std_dev=stats["std_dev"],
            sample_size=stats["count"],
            timestamp=time.time(),
            version=version,
            description=description
        )
        
        self.baselines[category] = baseline
        self.save_baselines()
        return baseline
    
    def check_regression(self, tracker: PerformanceTracker, category: str, 
                        threshold: float = 0.2) -> Dict[str, Any]:
        """Check for performance regression against baseline."""
        if category not in self.baselines:
            return {
                "status": "no_baseline",
                "message": f"No baseline found for category: {category}",
                "regression_detected": False
            }
        
        baseline = self.baselines[category]
        current_stats = tracker.get_detailed_category_stats(category)
        
        if not current_stats:
            return {
                "status": "no_current_data",
                "message": f"No current performance data for category: {category}",
                "regression_detected": False
            }
        
        # Calculate regression percentages
        mean_regression = (current_stats["mean"] - baseline.mean_duration) / baseline.mean_duration
        median_regression = (current_stats["median"] - baseline.median_duration) / baseline.median_duration
        p95_regression = (current_stats["percentile_95"] - baseline.p95_duration) / baseline.p95_duration
        
        # Determine if regression occurred
        regression_detected = (
            mean_regression > threshold or 
            median_regression > threshold or 
            p95_regression > threshold
        )
        
        return {
            "status": "compared",
            "regression_detected": regression_detected,
            "baseline": asdict(baseline),
            "current": current_stats,
            "regressions": {
                "mean": mean_regression,
                "median": median_regression,
                "p95": p95_regression
            },
            "threshold": threshold,
            "message": self._generate_regression_message(
                regression_detected, mean_regression, median_regression, p95_regression, threshold
            )
        }
    
    def _generate_regression_message(self, regression_detected: bool, mean_reg: float, 
                                   median_reg: float, p95_reg: float, threshold: float) -> str:
        """Generate a human-readable regression message."""
        if not regression_detected:
            return "No performance regression detected"
        
        regressions = []
        if mean_reg > threshold:
            regressions.append(f"mean ({mean_reg*100:.1f}%)")
        if median_reg > threshold:
            regressions.append(f"median ({median_reg*100:.1f}%)")
        if p95_reg > threshold:
            regressions.append(f"P95 ({p95_reg*100:.1f}%)")
        
        return f"Performance regression detected in {', '.join(regressions)} (threshold: {threshold*100:.1f}%)"
    
    def generate_regression_report(self, tracker: PerformanceTracker) -> str:
        """Generate a comprehensive regression report."""
        lines = ["=== Performance Regression Report ==="]
        lines.append(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Baselines file: {self.baselines_file}")
        lines.append("")
        
        categories_tested = set()
        overall_regressions = []
        
        # Check all categories that have current data
        current_categories = {r.category for r in tracker.records}
        
        for category in current_categories:
            result = self.check_regression(tracker, category)
            categories_tested.add(category)
            
            lines.append(f"Category: {category}")
            lines.append(f"  Status: {result['status']}")
            lines.append(f"  Regression: {'YES' if result['regression_detected'] else 'NO'}")
            lines.append(f"  Message: {result['message']}")
            
            if result['regression_detected']:
                overall_regressions.append(category)
                regressions = result.get('regressions', {})
                lines.append(f"  Details:")
                lines.append(f"    Mean regression: {regressions.get('mean', 0)*100:.1f}%")
                lines.append(f"    Median regression: {regressions.get('median', 0)*100:.1f}%")
                lines.append(f"    P95 regression: {regressions.get('p95', 0)*100:.1f}%")
            
            lines.append("")
        
        # Check for baselines without current data
        baseline_only_categories = set(self.baselines.keys()) - categories_tested
        if baseline_only_categories:
            lines.append("Categories with baselines but no current data:")
            for category in baseline_only_categories:
                lines.append(f"  - {category}")
            lines.append("")
        
        # Summary
        lines.append("=== SUMMARY ===")
        lines.append(f"Categories tested: {len(categories_tested)}")
        lines.append(f"Regressions detected: {len(overall_regressions)}")
        if overall_regressions:
            lines.append(f"Regression categories: {', '.join(overall_regressions)}")
        else:
            lines.append("No performance regressions detected")
        
        return "\n".join(lines)


class PerformanceMonitor:
    """Continuous performance monitoring system."""
    
    def __init__(self, results_dir: str = "performance_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.detector = PerformanceRegressionDetector(
            self.results_dir / "baselines.json"
        )
    
    def record_session_results(self, tracker: PerformanceTracker, 
                             session_id: str = None) -> str:
        """Record performance results for a test session."""
        if session_id is None:
            session_id = f"session_{int(time.time())}"
        
        session_file = self.results_dir / f"{session_id}.json"
        tracker.save_results_to_file(str(session_file))
        
        return session_id
    
    def check_session_regressions(self, tracker: PerformanceTracker) -> Dict[str, Any]:
        """Check current session for regressions."""
        results = {}
        categories = {r.category for r in tracker.records}
        
        for category in categories:
            results[category] = self.detector.check_regression(tracker, category)
        
        return results
    
    def update_baselines(self, tracker: PerformanceTracker, version: str = "unknown"):
        """Update baselines with current performance data."""
        categories = {r.category for r in tracker.records}
        updated = []
        
        for category in categories:
            try:
                baseline = self.detector.establish_baseline(
                    tracker, category, version, 
                    f"Auto-updated baseline from test session"
                )
                updated.append(category)
            except ValueError as e:
                print(f"Could not update baseline for {category}: {e}")
        
        return updated
    
    def generate_monitoring_report(self, tracker: PerformanceTracker) -> str:
        """Generate a comprehensive monitoring report."""
        lines = ["=== Performance Monitoring Report ==="]
        lines.append(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Results directory: {self.results_dir}")
        lines.append("")
        
        # Current session performance
        lines.append("=== Current Session Performance ===")
        current_report = tracker.generate_performance_report()
        lines.append(current_report)
        lines.append("")
        
        # Regression analysis
        lines.append("=== Regression Analysis ===")
        regression_report = self.detector.generate_regression_report(tracker)
        lines.append(regression_report)
        
        return "\n".join(lines)


def assert_no_performance_regression(tracker: PerformanceTracker, category: str, 
                                   threshold: float = 0.2):
    """Assert that no performance regression occurred for a category."""
    detector = PerformanceRegressionDetector()
    result = detector.check_regression(tracker, category, threshold)
    
    if result["regression_detected"]:
        raise AssertionError(
            f"Performance regression detected in {category}: {result['message']}"
        )