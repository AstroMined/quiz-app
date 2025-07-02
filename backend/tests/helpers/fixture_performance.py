# filename: backend/tests/helpers/fixture_performance.py

import time
import functools
from typing import Dict, List, Any, Callable
from dataclasses import dataclass

from backend.app.services.logging_service import logger


def get_worker_id():
    """Get the current pytest-xdist worker ID, or 'main' for non-parallel execution."""
    try:
        # Try to get worker ID from pytest-xdist
        import pytest
        if hasattr(pytest, 'current_node') and pytest.current_node:
            worker_input = getattr(pytest.current_node, 'workerinput', {})
            return worker_input.get('workerid', 'main')
    except (ImportError, AttributeError):
        pass
    
    # Fallback for non-parallel execution
    return 'main'


@dataclass
class FixturePerformanceRecord:
    """Record of a fixture's performance metrics."""
    fixture_name: str
    setup_duration: float
    scope: str
    session_reuse_count: int
    timestamp: float
    worker_id: str = "main"


class FixturePerformanceTracker:
    """Track fixture performance and reuse efficiency."""
    
    def __init__(self):
        self.records: List[FixturePerformanceRecord] = []
        self.fixture_reuse_counts: Dict[str, int] = {}
    
    def record_fixture_setup(self, fixture_name: str, duration: float, scope: str):
        """Record fixture setup performance."""
        worker_id = get_worker_id()
        fixture_key = f"{fixture_name}@{worker_id}"
        
        # Track reuse for session/module scoped fixtures per worker
        if scope in ("session", "module"):
            self.fixture_reuse_counts[fixture_key] = self.fixture_reuse_counts.get(fixture_key, 0) + 1
        
        record = FixturePerformanceRecord(
            fixture_name=fixture_name,
            setup_duration=duration,
            scope=scope,
            session_reuse_count=self.fixture_reuse_counts.get(fixture_key, 1),
            timestamp=time.time(),
            worker_id=worker_id
        )
        self.records.append(record)
        
        logger.debug(
            "Fixture %s (%s scope) setup in %.3fs on worker %s (reuse count: %d)",
            fixture_name, scope, duration, worker_id, record.session_reuse_count
        )
    
    def get_fixture_stats(self, fixture_name: str) -> Dict[str, Any]:
        """Get performance statistics for a specific fixture."""
        fixture_records = [r for r in self.records if r.fixture_name == fixture_name]
        
        if not fixture_records:
            return {}
        
        durations = [r.setup_duration for r in fixture_records]
        return {
            "fixture_name": fixture_name,
            "scope": fixture_records[0].scope,
            "setup_count": len(durations),
            "total_setup_time": sum(durations),
            "average_setup_time": sum(durations) / len(durations),
            "min_setup_time": min(durations),
            "max_setup_time": max(durations),
            "reuse_efficiency": fixture_records[0].session_reuse_count / len(durations) if durations else 0
        }
    
    def get_all_fixture_stats(self) -> List[Dict[str, Any]]:
        """Get performance statistics for all tracked fixtures."""
        fixture_names = set(r.fixture_name for r in self.records)
        return [self.get_fixture_stats(name) for name in fixture_names]
    
    def get_slowest_fixtures(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the slowest fixtures by average setup time."""
        all_stats = self.get_all_fixture_stats()
        return sorted(
            all_stats, 
            key=lambda x: x.get("average_setup_time", 0), 
            reverse=True
        )[:limit]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall fixture performance summary."""
        if not self.records:
            return {}
        
        total_setup_time = sum(r.setup_duration for r in self.records)
        function_scoped = [r for r in self.records if r.scope == "function"]
        session_scoped = [r for r in self.records if r.scope == "session"]
        module_scoped = [r for r in self.records if r.scope == "module"]
        
        # Worker statistics
        workers = set(r.worker_id for r in self.records)
        worker_stats = {}
        for worker_id in workers:
            worker_records = [r for r in self.records if r.worker_id == worker_id]
            worker_stats[worker_id] = {
                "setups": len(worker_records),
                "total_time": sum(r.setup_duration for r in worker_records)
            }
        
        return {
            "total_fixture_setups": len(self.records),
            "total_setup_time": total_setup_time,
            "average_setup_time": total_setup_time / len(self.records),
            "function_scoped_setups": len(function_scoped),
            "session_scoped_setups": len(session_scoped),
            "module_scoped_setups": len(module_scoped),
            "function_scope_time": sum(r.setup_duration for r in function_scoped),
            "session_scope_time": sum(r.setup_duration for r in session_scoped),
            "module_scope_time": sum(r.setup_duration for r in module_scoped),
            "parallel_workers": len(workers),
            "worker_stats": worker_stats,
        }


# Global fixture performance tracker
_fixture_tracker = FixturePerformanceTracker()


def track_fixture_performance(scope: str = "function"):
    """Decorator to track fixture performance."""
    def decorator(fixture_func: Callable) -> Callable:
        @functools.wraps(fixture_func)
        def wrapper(*args, **kwargs):
            fixture_name = fixture_func.__name__
            start_time = time.time()
            
            try:
                result = fixture_func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                setup_duration = end_time - start_time
                _fixture_tracker.record_fixture_setup(fixture_name, setup_duration, scope)
        
        return wrapper
    return decorator


def get_fixture_performance_tracker() -> FixturePerformanceTracker:
    """Get the global fixture performance tracker."""
    return _fixture_tracker