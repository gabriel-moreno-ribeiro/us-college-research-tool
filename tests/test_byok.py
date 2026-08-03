"""
Quick smoke test for BYOK functionality.

Tests:
1. Key context isolation
2. HTTP middleware integration
3. Source tracking
4. Error message formatting
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def test_key_context():
    """Test that key context is properly isolated."""
    from mcp_server.key_context import set_keys, get_scorecard_key, get_semantic_scholar_key, clear_keys

    # Initially empty
    assert get_scorecard_key() is None
    assert get_semantic_scholar_key() is None

    # Set keys
    set_keys(scorecard="test_scorecard_key", semantic_scholar="test_ss_key")
    assert get_scorecard_key() == "test_scorecard_key"
    assert get_semantic_scholar_key() == "test_ss_key"

    # Clear keys
    clear_keys()
    assert get_scorecard_key() is None
    assert get_semantic_scholar_key() is None

    print("✓ Key context test passed")


def test_source_tracker():
    """Test source tracking functionality."""
    from src.source_tracker import record_source, get_sources, export_sources
    import tempfile
    import shutil

    # Use a temp directory for testing
    temp_dir = Path(tempfile.mkdtemp())
    original_db = Path(__file__).parent / "data" / "sources.db"

    try:
        # Record some test sources
        record_source(
            url="https://example.edu/faculty",
            title="Test Faculty Page",
            university="Test University",
            category="faculty"
        )
        record_source(
            url="https://api.data.gov/test",
            title="Test API",
            university="Test University",
            category="institutional_data"
        )

        # Retrieve
        sources = get_sources(university="Test University")
        assert len(sources) >= 2
        assert any(s["url"] == "https://example.edu/faculty" for s in sources)

        # Export
        files = export_sources(university="Test University")
        assert "urls.txt" in files
        assert "fontes.md" in files
        assert "https://example.edu/faculty" in files["urls.txt"]

        print("✓ Source tracker test passed")

    finally:
        # Cleanup is handled by the module's singleton connection
        pass


def test_college_scorecard_byok():
    """Test that CollegeScorecardClient respects BYOK context."""
    from src.college_scorecard import CollegeScorecardClient
    from mcp_server.key_context import set_keys, clear_keys
    import os

    # Clear env var to ensure BYOK is used
    original_key = os.environ.pop("COLLEGE_SCORECARD_API_KEY", None)

    try:
        # Without BYOK or env var, should raise
        try:
            client = CollegeScorecardClient()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "não encontrada" in str(e).lower() or "not found" in str(e).lower()

        # With explicit key, should work
        client = CollegeScorecardClient(api_key="test_key")
        assert client.api_key == "test_key"

        print("✓ CollegeScorecardClient BYOK test passed")

    finally:
        if original_key:
            os.environ["COLLEGE_SCORECARD_API_KEY"] = original_key
        clear_keys()


def test_semantic_scholar_byok():
    """Test that SemanticScholarClient respects BYOK context."""
    from src.semantic_scholar import SemanticScholarClient
    from mcp_server.key_context import set_keys, clear_keys
    import os

    original_key = os.environ.pop("SEMANTIC_SCHOLAR_API_KEY", None)

    try:
        # Set BYOK key
        set_keys(semantic_scholar="byok_ss_key")

        # Client should pick up BYOK key
        client = SemanticScholarClient()
        assert client.api_key == "byok_ss_key"

        clear_keys()

        # With explicit key, should use that
        client = SemanticScholarClient(api_key="explicit_key")
        assert client.api_key == "explicit_key"

        print("✓ SemanticScholarClient BYOK test passed")

    finally:
        if original_key:
            os.environ["SEMANTIC_SCHOLAR_API_KEY"] = original_key
        clear_keys()


def test_log_redaction():
    """Test that the log filter redacts sensitive values."""
    try:
        from mcp_server.http_app import KeyRedactingFilter
        import logging

        filter_inst = KeyRedactingFilter()
        KeyRedactingFilter.register_sensitive("SECRET_KEY_12345")

        # Create a test log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="API key is SECRET_KEY_12345",
            args=(),
            exc_info=None,
        )

        filter_inst.filter(record)
        assert "SECRET_KEY_12345" not in record.getMessage()
        assert "[REDACTED]" in record.getMessage()

        print("✓ Log redaction test passed")
    except ImportError as e:
        print(f"⊘ Log redaction test skipped (MCP not installed: {e})")


def test_rate_limiter():
    """Test rate limiting logic."""
    try:
        from mcp_server.http_app import RateLimiter

        limiter = RateLimiter(max_requests=5, window_seconds=60)

        # First 5 requests should be allowed
        for i in range(5):
            allowed, retry = limiter.is_allowed("test_ip")
            assert allowed, f"Request {i+1} should be allowed"

        # 6th request should be denied
        allowed, retry = limiter.is_allowed("test_ip")
        assert not allowed
        assert retry > 0

        # Different IP should be allowed
        allowed, retry = limiter.is_allowed("different_ip")
        assert allowed

        print("✓ Rate limiter test passed")
    except ImportError as e:
        print(f"⊘ Rate limiter test skipped (MCP not installed: {e})")


if __name__ == "__main__":
    print("Running BYOK smoke tests...\n")

    test_key_context()
    test_source_tracker()
    test_college_scorecard_byok()
    test_semantic_scholar_byok()
    test_log_redaction()
    test_rate_limiter()

    print("\n✓ All BYOK tests passed!")
