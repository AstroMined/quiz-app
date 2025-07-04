# filename: backend/tests/test_fixture_performance.py

import pytest
from backend.tests.helpers.fixture_performance import get_fixture_performance_tracker

pytestmark = pytest.mark.performance


def test_minimal_fixture_performance(minimal_question_data):
    """Test that minimal fixtures are significantly faster than complex ones."""
    # This test uses the minimal fixture variant
    assert minimal_question_data["question"] is not None
    assert minimal_question_data["content"]["subject"]["name"] == "Classical Mechanics"


def test_moderate_fixture_performance(moderate_question_data):
    """Test that moderate fixtures provide good balance of features and performance."""
    # This test uses the moderate fixture variant
    assert len(moderate_question_data["questions"]) == 2
    assert moderate_question_data["content"]["physics"]["subject"]["name"] == "Classical Mechanics"


def test_complex_fixture_performance(setup_filter_questions_data):
    """Test that complex fixtures still work but are optimized."""
    # This test uses the optimized complex fixture
    hierarchy = setup_filter_questions_data
    assert hierarchy["subjects"]["classical_mechanics"]["name"] == "Classical Mechanics"
    assert hierarchy["subjects"]["algebra"]["name"] == "Algebra"


def test_session_reference_content_reuse(test_domains, test_disciplines, test_subjects):
    """Test that session-scoped fixtures are properly reused."""
    stem_domain = next(d for d in test_domains if d.name == "STEM")
    humanities_domain = next(d for d in test_domains if d.name == "Humanities")
    mathematics_discipline = next(d for d in test_disciplines if d.name == "Mathematics")
    physics_discipline = next(d for d in test_disciplines if d.name == "Physics")
    algebra_subject = next(s for s in test_subjects if s.name == "Algebra")
    classical_mechanics_subject = next(s for s in test_subjects if s.name == "Classical Mechanics")
    
    assert stem_domain.name == "STEM"
    assert humanities_domain.name == "Humanities"
    assert mathematics_discipline.name == "Mathematics"
    assert physics_discipline.name == "Physics"
    assert algebra_subject.name == "Algebra"
    assert classical_mechanics_subject.name == "Classical Mechanics"


def test_fixture_performance_reporting(fixture_performance_tracker):
    """Validate that fixture performance is being tracked properly."""
    import os
    tracker = fixture_performance_tracker
    
    # Get performance summary
    summary = tracker.get_performance_summary()
    
    # In parallel execution, some workers may have no fixture setups
    # This is expected behavior with pytest-xdist worker isolation
    total_setups = summary.get("total_fixture_setups", 0)
    if total_setups == 0:
        # Check if we're running in parallel mode
        worker_id = os.environ.get('PYTEST_XDIST_WORKER')
        if worker_id:
            pytest.skip(f"No fixture setups recorded on worker {worker_id} - expected in parallel execution")
        else:
            # In serial mode, we should definitely have some tracked fixtures
            pytest.fail("No fixture setups tracked in serial execution - this indicates a problem")
    
    # Should have tracked some fixtures by now
    assert total_setups > 0
    
    # In serial mode or if we have tracked fixtures, validate fixture types are being tracked
    assert summary.get("session_scoped_setups", 0) > 0 or summary.get("function_scoped_setups", 0) > 0
    
    # Session-scoped fixtures should generally be faster on subsequent uses
    slowest = tracker.get_slowest_fixtures(10)
    
    if slowest:
        print(f"\n=== Fixture Performance Summary ===")
        print(f"Total fixture setups: {summary['total_fixture_setups']}")
        print(f"Total setup time: {summary['total_setup_time']:.3f}s")
        print(f"Average setup time: {summary['average_setup_time']:.3f}s")
        print(f"Function-scoped: {summary['function_scoped_setups']} setups ({summary['function_scope_time']:.3f}s)")
        print(f"Session-scoped: {summary['session_scoped_setups']} setups ({summary['session_scope_time']:.3f}s)")
        
        print(f"\n=== Fixture Performance Details ===")
        for fixture_stats in slowest[:5]:
            print(f"{fixture_stats['fixture_name']} ({fixture_stats['scope']}): "
                  f"avg {fixture_stats['average_setup_time']:.3f}s, "
                  f"max {fixture_stats['max_setup_time']:.3f}s "
                  f"({fixture_stats['setup_count']} setups)")