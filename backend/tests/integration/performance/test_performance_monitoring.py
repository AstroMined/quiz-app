# filename: backend/tests/integration/performance/test_performance_monitoring.py

import pytest
import tempfile
import os
import time
from pathlib import Path
from backend.tests.helpers.performance import PerformanceTracker
from backend.tests.helpers.performance_regression import (
    PerformanceRegressionDetector, 
    PerformanceMonitor,
    assert_no_performance_regression
)
from backend.app.core.jwt import create_access_token, decode_access_token


@pytest.fixture
def temp_performance_dir():
    """Create a temporary directory for performance monitoring tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_performance_baseline_establishment(temp_performance_dir, db_session, test_model_user):
    """Test establishing performance baselines."""
    tracker = PerformanceTracker()
    
    # Simulate some JWT operations for baseline
    for i in range(10):
        start_time = time.perf_counter()
        token = create_access_token(data={"sub": test_model_user.username}, db=db_session)
        payload = decode_access_token(token, db_session)
        end_time = time.perf_counter()
        
        tracker.record_test(
            test_name=f"jwt_baseline_test_{i}",
            duration=end_time - start_time,
            category="jwt_baseline"
        )
    
    # Establish baseline
    baselines_file = Path(temp_performance_dir) / "test_baselines.json"
    detector = PerformanceRegressionDetector(str(baselines_file))
    
    baseline = detector.establish_baseline(
        tracker, 
        "jwt_baseline", 
        version="v1.0.0",
        description="Initial JWT performance baseline"
    )
    
    # Verify baseline was created
    assert baseline.category == "jwt_baseline"
    assert baseline.mean_duration > 0
    assert baseline.sample_size == 10
    assert baseline.version == "v1.0.0"
    assert baselines_file.exists()
    
    # Verify baseline can be loaded
    detector2 = PerformanceRegressionDetector(str(baselines_file))
    assert "jwt_baseline" in detector2.baselines
    assert detector2.baselines["jwt_baseline"].mean_duration == baseline.mean_duration


def test_performance_regression_detection(temp_performance_dir, db_session, test_model_user):
    """Test performance regression detection."""
    baselines_file = Path(temp_performance_dir) / "regression_test.json"
    detector = PerformanceRegressionDetector(str(baselines_file))
    
    # Create baseline tracker with good performance
    baseline_tracker = PerformanceTracker()
    for i in range(5):
        baseline_tracker.record_test(f"fast_test_{i}", 0.001, "regression_test")
    
    detector.establish_baseline(baseline_tracker, "regression_test", "v1.0.0")
    
    # Create current tracker with degraded performance (regression)
    current_tracker = PerformanceTracker()
    for i in range(5):
        current_tracker.record_test(f"slow_test_{i}", 0.002, "regression_test")  # 2x slower
    
    # Check for regression
    result = detector.check_regression(current_tracker, "regression_test", threshold=0.2)
    
    assert result["status"] == "compared"
    assert result["regression_detected"] is True
    assert result["regressions"]["mean"] > 0.2  # 100% slower, above 20% threshold
    assert "regression detected" in result["message"].lower()
    
    # Test with no regression
    good_tracker = PerformanceTracker()
    for i in range(5):
        good_tracker.record_test(f"good_test_{i}", 0.001, "regression_test")  # Same performance
    
    good_result = detector.check_regression(good_tracker, "regression_test", threshold=0.2)
    assert good_result["regression_detected"] is False


def test_performance_monitor_system(temp_performance_dir, db_session, test_model_user):
    """Test the complete performance monitoring system."""
    monitor = PerformanceMonitor(temp_performance_dir)
    tracker = PerformanceTracker()
    
    # Simulate API test performance
    for i in range(5):
        start_time = time.perf_counter()
        # Simulate login operation
        token = create_access_token(data={"sub": test_model_user.username}, db=db_session)
        end_time = time.perf_counter()
        
        tracker.record_test(
            test_name=f"monitor_api_test_{i}",
            duration=end_time - start_time,
            category="api_monitoring"
        )
    
    # Record session results
    session_id = monitor.record_session_results(tracker, "test_session_001")
    assert session_id == "test_session_001"
    
    session_file = Path(temp_performance_dir) / "test_session_001.json"
    assert session_file.exists()
    
    # Update baselines
    updated_categories = monitor.update_baselines(tracker, "v1.0.0")
    assert "api_monitoring" in updated_categories
    
    # Check for regressions (should be none since we just established baseline)
    regressions = monitor.check_session_regressions(tracker)
    assert "api_monitoring" in regressions
    assert regressions["api_monitoring"]["regression_detected"] is False
    
    # Generate monitoring report
    report = monitor.generate_monitoring_report(tracker)
    assert "Performance Monitoring Report" in report
    assert "api_monitoring" in report
    assert "No performance regressions detected" in report


def test_performance_assertion_helper(temp_performance_dir, db_session, test_model_user):
    """Test the performance assertion helper function."""
    baselines_file = Path(temp_performance_dir) / "assertion_test.json"
    detector = PerformanceRegressionDetector(str(baselines_file))
    
    # Establish baseline
    baseline_tracker = PerformanceTracker()
    for i in range(3):
        baseline_tracker.record_test(f"baseline_{i}", 0.01, "assertion_test")
    
    detector.establish_baseline(baseline_tracker, "assertion_test")
    
    # Test with good performance (should not raise)
    good_tracker = PerformanceTracker()
    for i in range(3):
        good_tracker.record_test(f"good_{i}", 0.01, "assertion_test")
    
    # Test with the detector directly since the assertion helper uses default location
    result = detector.check_regression(good_tracker, "assertion_test")
    assert not result["regression_detected"], "No regression should be detected with good performance"
    
    # Test with poor performance (should detect regression)
    bad_tracker = PerformanceTracker()
    for i in range(3):
        bad_tracker.record_test(f"bad_{i}", 0.02, "assertion_test")  # 100% slower
    
    result = detector.check_regression(bad_tracker, "assertion_test", threshold=0.2)
    assert result["regression_detected"], "Regression should be detected with poor performance"


def test_comprehensive_performance_validation(performance_tracker, db_session, test_model_user):
    """Comprehensive validation of the new architecture performance."""
    
    # Test JWT operations performance
    jwt_durations = []
    for i in range(10):
        start_time = time.perf_counter()
        token = create_access_token(data={"sub": test_model_user.username}, db=db_session)
        payload = decode_access_token(token, db_session)
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        jwt_durations.append(duration)
        
        performance_tracker.record_test(
            test_name=f"comprehensive_jwt_test_{i}",
            duration=duration,
            category="comprehensive_validation"
        )
    
    # Validate JWT performance targets
    stats = performance_tracker.get_detailed_category_stats("comprehensive_validation")
    
    assert stats["mean"] < 0.01, f"JWT mean time {stats['mean']:.4f}s exceeds 0.01s target"
    assert stats["percentile_95"] < 0.02, f"JWT P95 time {stats['percentile_95']:.4f}s exceeds 0.02s target"
    assert stats["max"] < 0.05, f"JWT max time {stats['max']:.4f}s exceeds 0.05s target"
    
    # Performance improvement validation against documented baselines
    original_baseline = 2.19  # Pre-optimization API test duration
    current_performance = stats["mean"]
    improvement = (original_baseline - current_performance) / original_baseline
    
    assert improvement > 0.95, f"Improvement {improvement*100:.1f}% below 95% target"
    
    print(f"\nComprehensive Performance Validation Results:")
    print(f"  JWT Operations: {stats['count']} iterations")
    print(f"  Mean duration: {stats['mean']:.5f}s")
    print(f"  P95 duration: {stats['percentile_95']:.5f}s")
    print(f"  Performance improvement: {improvement*100:.1f}%")
    print(f"  ✅ All performance targets met")


def test_end_to_end_performance_monitoring_workflow(temp_performance_dir):
    """Test complete performance monitoring workflow."""
    
    print(f"\n=== End-to-End Performance Monitoring Workflow ===")
    
    # Initialize monitoring system
    monitor = PerformanceMonitor(temp_performance_dir)
    tracker = PerformanceTracker()
    
    # Simulate Phase 1 performance (baseline)
    print("Establishing Phase 1 baseline...")
    for i in range(10):
        tracker.record_test(f"phase1_test_{i}", 1.8, "e2e_monitoring")  # Slower baseline
    
    monitor.update_baselines(tracker, "phase1")
    
    # Simulate Phase 2 performance (improvement)
    print("Testing Phase 2 performance...")
    phase2_tracker = PerformanceTracker()
    for i in range(10):
        phase2_tracker.record_test(f"phase2_test_{i}", 0.5, "e2e_monitoring")  # Improved
    
    # Check for improvement (should detect significant improvement)
    regressions = monitor.check_session_regressions(phase2_tracker)
    result = regressions["e2e_monitoring"]
    
    # With improvement, regression percentages should be negative
    improvement_percentage = -result["regressions"]["mean"]  # Negative regression = improvement
    print(f"Phase 2 improvement detected: {improvement_percentage*100:.1f}%")
    
    assert improvement_percentage > 0.70, "Did not achieve 70% improvement target"
    
    # Generate final report
    final_report = monitor.generate_monitoring_report(phase2_tracker)
    print("\nFinal Monitoring Report Generated:")
    print("="*50)
    print(final_report[:500] + "..." if len(final_report) > 500 else final_report)
    
    # Verify monitoring files exist
    assert (Path(temp_performance_dir) / "baselines.json").exists()
    assert len(list(Path(temp_performance_dir).glob("*.json"))) >= 1
    
    print("✅ End-to-end monitoring workflow completed successfully")