"""
Database performance comparison tests.

These tests measure current database performance and compare against historical
baselines to track performance improvements and detect regressions.

Compares current performance with baseline from performance_baseline_legacy.json.
"""

import time
import json
from pathlib import Path
from contextlib import contextmanager
from statistics import mean, stdev

import pytest
from sqlalchemy import event

from backend.app.models.users import UserModel
from backend.app.models.user_responses import UserResponseModel
from backend.app.models.leaderboard import LeaderboardModel
from backend.app.models.questions import QuestionModel
from backend.app.models.groups import GroupModel


class QueryCounter:
    """Utility to count database queries during operations."""
    
    def __init__(self):
        self.query_count = 0
        self.queries = []
    
    def __call__(self, conn, cursor, statement, parameters, context, executemany):
        self.query_count += 1
        self.queries.append({
            "statement": statement,
            "parameters": parameters
        })


@contextmanager
def measure_queries(db_session):
    """Context manager to measure database queries."""
    counter = QueryCounter()
    event.listen(db_session.bind, "before_cursor_execute", counter)
    try:
        yield counter
    finally:
        event.remove(db_session.bind, "before_cursor_execute", counter)


def calculate_stats(values):
    """Calculate statistical summary of performance measurements."""
    return {
        "mean": mean(values),
        "std_dev": stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "count": len(values)
    }


def load_baseline():
    """Load baseline performance data for comparison."""
    baseline_file = Path("backend/tests/performance/baselines/performance_baseline_legacy.json")
    with open(baseline_file, 'r') as f:
        return json.load(f)


@pytest.mark.performance
def test_user_creation_performance(db_session, test_model_role):
    """Test UserModel creation performance with database constraints."""
    iterations = 50
    durations = []
    query_counts = []
    
    for i in range(iterations):
        username = f"current_user_{i}"
        email = f"current_{i}@example.com"
        
        with measure_queries(db_session) as counter:
            start_time = time.perf_counter()
            
            user = UserModel(
                username=username,
                email=email,
                hashed_password="test_hash",
                role_id=test_model_role.id
            )
            db_session.add(user)
            db_session.commit()
            
            end_time = time.perf_counter()
        
        durations.append(end_time - start_time)
        query_counts.append(counter.query_count)
        
        # Cleanup
        db_session.delete(user)
        db_session.commit()
    
    # Calculate statistics
    duration_stats = calculate_stats(durations)
    query_stats = calculate_stats(query_counts)
    
    print(f"\nCURRENT - User Creation Performance:")
    print(f"  Average Duration: {duration_stats['mean']*1000:.2f}ms")
    print(f"  Average Queries: {query_stats['mean']:.1f}")
    print(f"  Query Range: {query_stats['min']}-{query_stats['max']}")
    
    # Load baseline for comparison
    baseline = load_baseline()
    baseline_user = baseline["operations"]["user_creation"]
    
    # Performance comparison
    print(f"\n{'='*60}")
    print("USER CREATION PERFORMANCE COMPARISON")
    print(f"{'='*60}")
    print(f"Baseline: {baseline_user['query_stats']['mean']:.1f} queries, {baseline_user['duration_stats']['mean']:.2f}ms")
    print(f"Current:  {query_stats['mean']:.1f} queries, {duration_stats['mean']*1000:.2f}ms")
    
    query_reduction = ((baseline_user['query_stats']['mean'] - query_stats['mean']) / baseline_user['query_stats']['mean']) * 100
    time_improvement = ((baseline_user['duration_stats']['mean'] - duration_stats['mean']*1000) / baseline_user['duration_stats']['mean']) * 100
    
    print(f"Query reduction: {query_reduction:.1f}%")
    print(f"Time improvement: {time_improvement:.1f}%")
    print(f"{'='*60}")
    
    # Store results
    results = {
        "operation": "user_creation",
        "database_constraints_active": True,
        "iterations": iterations,
        "duration_stats": {k: v*1000 if 'time' in k or k in ['mean', 'std_dev', 'min', 'max'] else v 
                         for k, v in duration_stats.items()},
        "query_stats": query_stats
    }
    
    # Performance improvement assertions
    assert query_stats['mean'] < baseline_user['query_stats']['mean'], f"Expected fewer queries than baseline {baseline_user['query_stats']['mean']}, got {query_stats['mean']}"
    assert duration_stats['mean'] < 0.1, f"Duration should be < 100ms, got {duration_stats['mean']*1000:.2f}ms"
    
    return results


@pytest.mark.performance  
def test_user_response_creation_performance(
    db_session, 
    test_model_user, 
    test_model_questions, 
    test_model_answer_choices
):
    """Test UserResponseModel creation performance with database constraints."""
    iterations = 50
    durations = []
    query_counts = []
    
    for i in range(iterations):
        with measure_queries(db_session) as counter:
            start_time = time.perf_counter()
            
            response = UserResponseModel(
                user_id=test_model_user.id,
                question_id=test_model_questions[0].id,
                answer_choice_id=test_model_answer_choices[0].id,
                is_correct=True,
                response_time=30
            )
            db_session.add(response)
            db_session.commit()
            
            end_time = time.perf_counter()
        
        durations.append(end_time - start_time)
        query_counts.append(counter.query_count)
        
        # Cleanup
        db_session.delete(response)
        db_session.commit()
    
    # Calculate statistics
    duration_stats = calculate_stats(durations)
    query_stats = calculate_stats(query_counts)
    
    print(f"\nCURRENT - UserResponse Creation Performance:")
    print(f"  Average Duration: {duration_stats['mean']*1000:.2f}ms")
    print(f"  Average Queries: {query_stats['mean']:.1f}")
    print(f"  Query Range: {query_stats['min']}-{query_stats['max']}")
    
    # Load baseline for comparison
    baseline = load_baseline()
    baseline_response = baseline["operations"]["user_response_creation"]
    
    query_reduction = ((baseline_response['query_stats']['mean'] - query_stats['mean']) / baseline_response['query_stats']['mean']) * 100
    time_improvement = ((baseline_response['duration_stats']['mean'] - duration_stats['mean']*1000) / baseline_response['duration_stats']['mean']) * 100
    
    print(f"Query reduction: {query_reduction:.1f}%")
    print(f"Time improvement: {time_improvement:.1f}%")
    
    # Store results
    results = {
        "operation": "user_response_creation",
        "database_constraints_active": True,
        "iterations": iterations,
        "duration_stats": {k: v*1000 if 'time' in k or k in ['mean', 'std_dev', 'min', 'max'] else v 
                         for k, v in duration_stats.items()},
        "query_stats": query_stats
    }
    
    # Performance improvement assertions
    assert query_stats['mean'] < baseline_response['query_stats']['mean'], f"Expected fewer queries than baseline {baseline_response['query_stats']['mean']}, got {query_stats['mean']}"
    assert duration_stats['mean'] < 0.15, f"Duration should be < 150ms, got {duration_stats['mean']*1000:.2f}ms"
    
    return results


@pytest.mark.performance
def test_leaderboard_creation_performance(
    db_session, 
    test_model_user, 
    test_model_group, 
    time_period_daily
):
    """Test LeaderboardModel creation performance with database constraints."""
    iterations = 50
    durations = []
    query_counts = []
    
    for i in range(iterations):
        with measure_queries(db_session) as counter:
            start_time = time.perf_counter()
            
            leaderboard = LeaderboardModel(
                user_id=test_model_user.id,
                score=100 + i,
                time_period_id=time_period_daily.id,
                group_id=test_model_group.id
            )
            db_session.add(leaderboard)
            db_session.commit()
            
            end_time = time.perf_counter()
        
        durations.append(end_time - start_time)
        query_counts.append(counter.query_count)
        
        # Cleanup
        db_session.delete(leaderboard)
        db_session.commit()
    
    # Calculate statistics
    duration_stats = calculate_stats(durations)
    query_stats = calculate_stats(query_counts)
    
    print(f"\nCURRENT - Leaderboard Creation Performance:")
    print(f"  Average Duration: {duration_stats['mean']*1000:.2f}ms")
    print(f"  Average Queries: {query_stats['mean']:.1f}")
    print(f"  Query Range: {query_stats['min']}-{query_stats['max']}")
    
    # Load baseline for comparison
    baseline = load_baseline()
    baseline_leaderboard = baseline["operations"]["leaderboard_creation"]
    
    query_reduction = ((baseline_leaderboard['query_stats']['mean'] - query_stats['mean']) / baseline_leaderboard['query_stats']['mean']) * 100
    time_improvement = ((baseline_leaderboard['duration_stats']['mean'] - duration_stats['mean']*1000) / baseline_leaderboard['duration_stats']['mean']) * 100
    
    print(f"Query reduction: {query_reduction:.1f}%")
    print(f"Time improvement: {time_improvement:.1f}%")
    
    # Store results
    results = {
        "operation": "leaderboard_creation",
        "database_constraints_active": True,
        "iterations": iterations,
        "duration_stats": {k: v*1000 if 'time' in k or k in ['mean', 'std_dev', 'min', 'max'] else v 
                         for k, v in duration_stats.items()},
        "query_stats": query_stats
    }
    
    # Performance improvement assertions
    assert query_stats['mean'] < baseline_leaderboard['query_stats']['mean'], f"Expected fewer queries than baseline {baseline_leaderboard['query_stats']['mean']}, got {query_stats['mean']}"
    assert duration_stats['mean'] < 0.15, f"Duration should be < 150ms, got {duration_stats['mean']*1000:.2f}ms"
    
    return results


@pytest.mark.performance
def test_question_creation_performance(db_session, test_model_user):
    """Test QuestionModel creation performance with database constraints."""
    iterations = 50
    durations = []
    query_counts = []
    
    for i in range(iterations):
        question_text = f"Current question {i}?"
        
        with measure_queries(db_session) as counter:
            start_time = time.perf_counter()
            
            question = QuestionModel(
                text=question_text,
                difficulty="EASY",
                creator_id=test_model_user.id
            )
            db_session.add(question)
            db_session.commit()
            
            end_time = time.perf_counter()
        
        durations.append(end_time - start_time)
        query_counts.append(counter.query_count)
        
        # Cleanup
        db_session.delete(question)
        db_session.commit()
    
    # Calculate statistics
    duration_stats = calculate_stats(durations)
    query_stats = calculate_stats(query_counts)
    
    print(f"\nCURRENT - Question Creation Performance:")
    print(f"  Average Duration: {duration_stats['mean']*1000:.2f}ms")
    print(f"  Average Queries: {query_stats['mean']:.1f}")
    print(f"  Query Range: {query_stats['min']}-{query_stats['max']}")
    
    # Load baseline for comparison
    baseline = load_baseline()
    baseline_question = baseline["operations"]["question_creation"]
    
    query_reduction = ((baseline_question['query_stats']['mean'] - query_stats['mean']) / baseline_question['query_stats']['mean']) * 100
    time_improvement = ((baseline_question['duration_stats']['mean'] - duration_stats['mean']*1000) / baseline_question['duration_stats']['mean']) * 100
    
    print(f"Query reduction: {query_reduction:.1f}%")
    print(f"Time improvement: {time_improvement:.1f}%")
    
    # Store results
    results = {
        "operation": "question_creation",
        "database_constraints_active": True,
        "iterations": iterations,
        "duration_stats": {k: v*1000 if 'time' in k or k in ['mean', 'std_dev', 'min', 'max'] else v 
                         for k, v in duration_stats.items()},
        "query_stats": query_stats
    }
    
    # Performance improvement assertions
    assert query_stats['mean'] < baseline_question['query_stats']['mean'], f"Expected fewer queries than baseline {baseline_question['query_stats']['mean']}, got {query_stats['mean']}"
    assert duration_stats['mean'] < 0.1, f"Duration should be < 100ms, got {duration_stats['mean']*1000:.2f}ms"
    
    return results


@pytest.mark.performance
def test_group_creation_performance(db_session, test_model_user):
    """Test GroupModel creation performance with database constraints."""
    iterations = 50
    durations = []
    query_counts = []
    
    for i in range(iterations):
        group_name = f"Current Group {i}"
        
        with measure_queries(db_session) as counter:
            start_time = time.perf_counter()
            
            group = GroupModel(
                name=group_name,
                description="Test group for current measurement",
                creator_id=test_model_user.id
            )
            db_session.add(group)
            db_session.commit()
            
            end_time = time.perf_counter()
        
        durations.append(end_time - start_time)
        query_counts.append(counter.query_count)
        
        # Cleanup
        db_session.delete(group)
        db_session.commit()
    
    # Calculate statistics
    duration_stats = calculate_stats(durations)
    query_stats = calculate_stats(query_counts)
    
    print(f"\nCURRENT - Group Creation Performance:")
    print(f"  Average Duration: {duration_stats['mean']*1000:.2f}ms")
    print(f"  Average Queries: {query_stats['mean']:.1f}")
    print(f"  Query Range: {query_stats['min']}-{query_stats['max']}")
    
    # Load baseline for comparison
    baseline = load_baseline()
    baseline_group = baseline["operations"]["group_creation"]
    
    query_reduction = ((baseline_group['query_stats']['mean'] - query_stats['mean']) / baseline_group['query_stats']['mean']) * 100
    time_improvement = ((baseline_group['duration_stats']['mean'] - duration_stats['mean']*1000) / baseline_group['duration_stats']['mean']) * 100
    
    print(f"Query reduction: {query_reduction:.1f}%")
    print(f"Time improvement: {time_improvement:.1f}%")
    
    # Store results
    results = {
        "operation": "group_creation",
        "database_constraints_active": True,
        "iterations": iterations,
        "duration_stats": {k: v*1000 if 'time' in k or k in ['mean', 'std_dev', 'min', 'max'] else v 
                         for k, v in duration_stats.items()},
        "query_stats": query_stats
    }
    
    # Performance improvement assertions
    assert query_stats['mean'] < baseline_group['query_stats']['mean'], f"Expected fewer queries than baseline {baseline_group['query_stats']['mean']}, got {query_stats['mean']}"
    assert duration_stats['mean'] < 0.1, f"Duration should be < 100ms, got {duration_stats['mean']*1000:.2f}ms"
    
    return results


@pytest.mark.performance
def test_comprehensive_performance_comparison(
    db_session, 
    test_model_user, 
    test_model_role,
    test_model_questions, 
    test_model_answer_choices,
    test_model_group,
    time_period_daily
):
    """Run all performance tests and generate comprehensive comparison."""
    
    print(f"\n{'='*60}")
    print("DATABASE PERFORMANCE COMPARISON SUMMARY")
    print(f"{'='*60}")
    
    # Load baseline data
    baseline = load_baseline()
    
    # Run all current performance tests
    user_results = test_user_creation_performance(db_session, test_model_role)
    response_results = test_user_response_creation_performance(
        db_session, test_model_user, test_model_questions, test_model_answer_choices
    )
    leaderboard_results = test_leaderboard_creation_performance(
        db_session, test_model_user, test_model_group, time_period_daily
    )
    question_results = test_question_creation_performance(db_session, test_model_user)
    group_results = test_group_creation_performance(db_session, test_model_user)
    
    # Compile comprehensive results
    all_results = {
        "comparison_metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "database_constraints_active": True,
            "database_type": "sqlite",
            "python_version": "3.12.10",
            "test_environment": "database_constraints_measurement"
        },
        "operations": {
            "user_creation": user_results,
            "user_response_creation": response_results,
            "leaderboard_creation": leaderboard_results,
            "question_creation": question_results,
            "group_creation": group_results
        }
    }
    
    # Save results to file for future reference
    results_dir = Path("backend/tests/performance/baselines")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    results_file = results_dir / "performance_baseline_current.json"
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("PERFORMANCE IMPROVEMENT SUMMARY")
    print(f"{'='*60}")
    
    total_query_reduction = 0
    total_time_improvement = 0
    operation_count = 0
    
    for operation_name, current_results in all_results["operations"].items():
        if operation_name in baseline["operations"]:
            baseline_op = baseline["operations"][operation_name]
            current_queries = current_results["query_stats"]["mean"]
            baseline_queries = baseline_op["query_stats"]["mean"]
            current_time = current_results["duration_stats"]["mean"]
            baseline_time = baseline_op["duration_stats"]["mean"]
            
            query_reduction = ((baseline_queries - current_queries) / baseline_queries) * 100
            time_improvement = ((baseline_time - current_time) / baseline_time) * 100
            
            print(f"{operation_name.replace('_', ' ').title():<25}:")
            print(f"  Queries: {baseline_queries:4.1f} → {current_queries:4.1f} ({query_reduction:+5.1f}%)")
            print(f"  Time:    {baseline_time:6.2f}ms → {current_time:6.2f}ms ({time_improvement:+5.1f}%)")
            
            total_query_reduction += query_reduction
            total_time_improvement += time_improvement
            operation_count += 1
    
    avg_query_reduction = total_query_reduction / operation_count if operation_count > 0 else 0
    avg_time_improvement = total_time_improvement / operation_count if operation_count > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"OVERALL IMPROVEMENTS:")
    print(f"  Average Query Reduction: {avg_query_reduction:5.1f}%")
    print(f"  Average Time Improvement: {avg_time_improvement:5.1f}%")
    print(f"{'='*60}")
    
    print(f"\nResults saved to: {results_file}")
    print(f"Baseline data from: backend/tests/performance/baselines/performance_baseline_legacy.json")
    
    # Overall validation - ensure we have improvements
    total_operations = len(all_results["operations"])
    improved_operations = sum(
        1 for operation_name, current_results in all_results["operations"].items()
        if operation_name in baseline["operations"] and
        current_results["query_stats"]["mean"] < baseline["operations"][operation_name]["query_stats"]["mean"]
    )
    
    assert improved_operations == total_operations, (
        f"Expected all {total_operations} operations to show query improvements, "
        f"but only {improved_operations} did"
    )
    
    assert avg_query_reduction > 0, f"Expected overall query reduction, got {avg_query_reduction:.1f}%"
    
    print(f"\n✅ Performance improvements confirmed!")
    print(f"   All {total_operations} operations show query reduction")
    print(f"   Average improvement: {avg_query_reduction:.1f}% fewer queries")
    
    return all_results