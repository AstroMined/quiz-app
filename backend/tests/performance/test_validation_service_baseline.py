"""
Performance baseline tests for validation service.

These tests measure performance WITH the validation service active to establish
baselines for comparison after validation service removal.

CRITICAL: These tests must be run BEFORE removing the validation service!
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
from backend.app.models.question_sets import QuestionSetModel


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


class TestValidationServiceBaseline:
    """Baseline performance tests with validation service active."""
    
    @pytest.mark.performance
    def test_user_creation_baseline(self, db_session, test_model_role):
        """Baseline: UserModel creation with role_id FK validation."""
        iterations = 50
        durations = []
        query_counts = []
        
        for i in range(iterations):
            username = f"baseline_user_{i}"
            email = f"baseline_{i}@example.com"
            
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
        
        print(f"\nBASELINE - User Creation (with validation service):")
        print(f"  Average Duration: {duration_stats['mean']*1000:.2f}ms")
        print(f"  Average Queries: {query_stats['mean']:.1f}")
        print(f"  Query Range: {query_stats['min']}-{query_stats['max']}")
        
        # Store results
        results = {
            "operation": "user_creation",
            "validation_service_active": True,
            "iterations": iterations,
            "duration_stats": {k: v*1000 if 'time' in k or k in ['mean', 'std_dev', 'min', 'max'] else v 
                             for k, v in duration_stats.items()},
            "query_stats": query_stats
        }
        
        # Assertions for validation service behavior
        assert query_stats['mean'] >= 2.0, f"Expected 2+ queries with validation service, got {query_stats['mean']}"
        assert duration_stats['mean'] < 0.1, f"Duration should be < 100ms, got {duration_stats['mean']*1000:.2f}ms"
        
        return results
    
    @pytest.mark.performance  
    def test_user_response_creation_baseline(
        self, 
        db_session, 
        test_model_user, 
        test_model_questions, 
        test_model_answer_choices
    ):
        """Baseline: UserResponseModel creation with 3 FK validations."""
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
        
        print(f"\nBASELINE - UserResponse Creation (with validation service):")
        print(f"  Average Duration: {duration_stats['mean']*1000:.2f}ms")
        print(f"  Average Queries: {query_stats['mean']:.1f}")
        print(f"  Query Range: {query_stats['min']}-{query_stats['max']}")
        
        # Store results
        results = {
            "operation": "user_response_creation",
            "validation_service_active": True,
            "iterations": iterations,
            "duration_stats": {k: v*1000 if 'time' in k or k in ['mean', 'std_dev', 'min', 'max'] else v 
                             for k, v in duration_stats.items()},
            "query_stats": query_stats
        }
        
        # Assertions for validation service behavior
        assert query_stats['mean'] >= 4.0, f"Expected 4+ queries with validation service, got {query_stats['mean']}"
        assert duration_stats['mean'] < 0.15, f"Duration should be < 150ms, got {duration_stats['mean']*1000:.2f}ms"
        
        return results
    
    @pytest.mark.performance
    def test_leaderboard_creation_baseline(
        self, 
        db_session, 
        test_model_user, 
        test_model_group, 
        time_period_daily
    ):
        """Baseline: LeaderboardModel creation with 3 FK validations."""
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
        
        print(f"\nBASELINE - Leaderboard Creation (with validation service):")
        print(f"  Average Duration: {duration_stats['mean']*1000:.2f}ms")
        print(f"  Average Queries: {query_stats['mean']:.1f}")
        print(f"  Query Range: {query_stats['min']}-{query_stats['max']}")
        
        # Store results
        results = {
            "operation": "leaderboard_creation",
            "validation_service_active": True,
            "iterations": iterations,
            "duration_stats": {k: v*1000 if 'time' in k or k in ['mean', 'std_dev', 'min', 'max'] else v 
                             for k, v in duration_stats.items()},
            "query_stats": query_stats
        }
        
        # Assertions for validation service behavior
        assert query_stats['mean'] >= 4.0, f"Expected 4+ queries with validation service, got {query_stats['mean']}"
        assert duration_stats['mean'] < 0.15, f"Duration should be < 150ms, got {duration_stats['mean']*1000:.2f}ms"
        
        return results
    
    @pytest.mark.performance
    def test_question_creation_baseline(self, db_session, test_model_user):
        """Baseline: QuestionModel creation with creator_id FK validation."""
        iterations = 50
        durations = []
        query_counts = []
        
        for i in range(iterations):
            question_text = f"Baseline question {i}?"
            
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
        
        print(f"\nBASELINE - Question Creation (with validation service):")
        print(f"  Average Duration: {duration_stats['mean']*1000:.2f}ms")
        print(f"  Average Queries: {query_stats['mean']:.1f}")
        print(f"  Query Range: {query_stats['min']}-{query_stats['max']}")
        
        # Store results
        results = {
            "operation": "question_creation",
            "validation_service_active": True,
            "iterations": iterations,
            "duration_stats": {k: v*1000 if 'time' in k or k in ['mean', 'std_dev', 'min', 'max'] else v 
                             for k, v in duration_stats.items()},
            "query_stats": query_stats
        }
        
        # Assertions for validation service behavior
        assert query_stats['mean'] >= 2.0, f"Expected 2+ queries with validation service, got {query_stats['mean']}"
        assert duration_stats['mean'] < 0.1, f"Duration should be < 100ms, got {duration_stats['mean']*1000:.2f}ms"
        
        return results
    
    @pytest.mark.performance
    def test_group_creation_baseline(self, db_session, test_model_user):
        """Baseline: GroupModel creation with creator_id FK validation."""
        iterations = 50
        durations = []
        query_counts = []
        
        for i in range(iterations):
            group_name = f"Baseline Group {i}"
            
            with measure_queries(db_session) as counter:
                start_time = time.perf_counter()
                
                group = GroupModel(
                    name=group_name,
                    description="Test group for baseline measurement",
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
        
        print(f"\nBASELINE - Group Creation (with validation service):")
        print(f"  Average Duration: {duration_stats['mean']*1000:.2f}ms")
        print(f"  Average Queries: {query_stats['mean']:.1f}")
        print(f"  Query Range: {query_stats['min']}-{query_stats['max']}")
        
        # Store results
        results = {
            "operation": "group_creation",
            "validation_service_active": True,
            "iterations": iterations,
            "duration_stats": {k: v*1000 if 'time' in k or k in ['mean', 'std_dev', 'min', 'max'] else v 
                             for k, v in duration_stats.items()},
            "query_stats": query_stats
        }
        
        # Assertions for validation service behavior
        assert query_stats['mean'] >= 2.0, f"Expected 2+ queries with validation service, got {query_stats['mean']}"
        assert duration_stats['mean'] < 0.1, f"Duration should be < 100ms, got {duration_stats['mean']*1000:.2f}ms"
        
        return results
    
    @pytest.mark.performance
    def test_comprehensive_baseline_summary(
        self, 
        db_session, 
        test_model_user, 
        test_model_role,
        test_model_questions, 
        test_model_answer_choices,
        test_model_group,
        time_period_daily
    ):
        """Run all baseline tests and generate comprehensive summary."""
        
        print(f"\n{'='*60}")
        print("VALIDATION SERVICE BASELINE PERFORMANCE SUMMARY")
        print(f"{'='*60}")
        
        # Run all baseline tests
        user_results = self.test_user_creation_baseline(db_session, test_model_role)
        response_results = self.test_user_response_creation_baseline(
            db_session, test_model_user, test_model_questions, test_model_answer_choices
        )
        leaderboard_results = self.test_leaderboard_creation_baseline(
            db_session, test_model_user, test_model_group, time_period_daily
        )
        question_results = self.test_question_creation_baseline(db_session, test_model_user)
        group_results = self.test_group_creation_baseline(db_session, test_model_user)
        
        # Compile comprehensive results
        all_results = {
            "baseline_metadata": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "validation_service_active": True,
                "database_type": "sqlite",
                "python_version": "3.12.10",
                "test_environment": "baseline_measurement"
            },
            "operations": {
                "user_creation": user_results,
                "user_response_creation": response_results,
                "leaderboard_creation": leaderboard_results,
                "question_creation": question_results,
                "group_creation": group_results
            }
        }
        
        # Save results to file for comparison
        baseline_dir = Path("backend/tests/performance/baselines")
        baseline_dir.mkdir(parents=True, exist_ok=True)
        
        results_file = baseline_dir / "validation_service_active_baseline.json"
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n{'='*60}")
        print("BASELINE RESULTS SUMMARY")
        print(f"{'='*60}")
        
        for operation, results in all_results["operations"].items():
            duration_mean = results["duration_stats"]["mean"]
            query_mean = results["query_stats"]["mean"]
            print(f"{operation.replace('_', ' ').title():<25}: {duration_mean:6.2f}ms, {query_mean:4.1f} queries")
        
        print(f"\nResults saved to: {results_file}")
        print(f"{'='*60}")
        
        # Overall validation - ensure validation service is working
        total_operations = len(all_results["operations"])
        high_query_operations = sum(
            1 for results in all_results["operations"].values() 
            if results["query_stats"]["mean"] >= 2.0
        )
        
        assert high_query_operations == total_operations, (
            f"Expected all {total_operations} operations to have 2+ queries with validation service, "
            f"but only {high_query_operations} did"
        )
        
        print(f"\n✅ Validation service baseline successfully established!")
        print(f"   All {total_operations} operations show expected validation overhead")
        
        return all_results


# Required fixtures for baseline tests are imported from existing fixture modules