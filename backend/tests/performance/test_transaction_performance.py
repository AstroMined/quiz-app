# Performance tests for database transaction operations

import pytest
import time
from backend.app.models.users import UserModel
from backend.app.core.security import get_password_hash

pytestmark = pytest.mark.performance


def test_performance_of_transaction_isolation(db_session, test_model_role, performance_tracker):
    """Test that transaction isolation doesn't significantly impact performance."""
    
    # Pre-hash password once to avoid bcrypt performance impact
    hashed_password = get_password_hash("TestPassword123!")
    
    start_time = time.perf_counter()
    
    # Perform multiple database operations
    users = []
    for i in range(10):  # Reduced to 10 for reasonable test time
        user = UserModel(
            username=f"perf_test_user_{i}",
            email=f"perf_test_user_{i}@example.com",
            hashed_password=hashed_password,  # Use pre-hashed password
            is_active=True,
            is_admin=True,
            role_id=test_model_role.id,
        )
        db_session.add(user)
        users.append(user)
    
    db_session.flush()
    
    # Perform some queries
    for user in users:
        found_user = db_session.query(UserModel).filter_by(id=user.id).first()
        assert found_user is not None
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    performance_tracker.record_test(
        test_name="transaction_isolation_performance",
        duration=duration,
        category="isolation_performance"
    )
    
    # Performance should be reasonable (excluding bcrypt hashing time)
    assert duration < 0.5, f"Transaction isolation operations took {duration:.3f}s, expected < 0.5s"
    
    print(f"\nTransaction Isolation Performance:")
    print(f"  Operations: 10 user creations + 10 queries")
    print(f"  Duration: {duration:.4f}s")
    print(f"  Per operation: {duration/20:.4f}s")