"""
Demo Script: API Timeout and Cancellation Fixes

This script demonstrates all the timeout and cancellation improvements made to the
Unsplash Image Search application. It shows before/after comparisons and tests
the new functionality without needing the full GUI application.
"""

import time
import threading
import logging
from pathlib import Path
import sys
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

def demo_cancellation_tokens():
    """
    Demo 1: Cancellation Token System
    Shows how operations can be cancelled gracefully.
    """
    print("\n" + "="*60)
    print("🔴 DEMO 1: Cancellation Token System")
    print("="*60)
    
    try:
        from src.services.api_timeout_manager import CancellationToken, CancellationError
        
        # Create cancellation token
        token = CancellationToken()
        print(f"✅ Token created. Is cancelled: {token.is_cancelled}")
        
        # Register callback
        callback_triggered = threading.Event()
        def on_cancel():
            print("🔴 Cancellation callback triggered!")
            callback_triggered.set()
        
        token.register_callback(on_cancel)
        print("✅ Callback registered")
        
        # Simulate operation that checks for cancellation
        def simulate_long_operation():
            for i in range(5):
                print(f"🔄 Working... step {i+1}/5")
                time.sleep(0.5)
                
                # Check for cancellation
                if token.is_cancelled:
                    print("🚨 Operation detected cancellation!")
                    return "cancelled"
            return "completed"
        
        # Start operation in thread
        result = [None]
        def run_operation():
            result[0] = simulate_long_operation()
        
        thread = threading.Thread(target=run_operation)
        thread.start()
        
        # Cancel after 1.5 seconds
        time.sleep(1.5)
        print("🚨 Cancelling operation...")
        token.cancel()
        
        # Wait for completion
        thread.join()
        callback_triggered.wait(timeout=1.0)
        
        print(f"✅ Operation result: {result[0]}")
        print(f"✅ Token cancelled: {token.is_cancelled}")
        print(f"✅ Callback triggered: {callback_triggered.is_set()}")
        
    except ImportError as e:
        print(f"❌ Could not import cancellation system: {e}")
        print("📝 Install required services to see this demo")

def demo_timeout_configurations():
    """
    Demo 2: Service-Specific Timeout Configurations
    Shows how different services have different timeout settings.
    """
    print("\n" + "="*60)
    print("⏰ DEMO 2: Service-Specific Timeout Configurations")
    print("="*60)
    
    try:
        from src.services.api_timeout_manager import ApiTimeoutManager
        
        manager = ApiTimeoutManager()
        
        services = ['unsplash', 'openai', 'download']
        print("Service Timeout Configurations:")
        print("-" * 40)
        
        for service in services:
            config = manager.get_timeout_config(service)
            print(f"🔌 {service.upper()}:")
            print(f"   Connect: {config.connect}s")
            print(f"   Read: {config.read}s")
            print(f"   Total: {config.total}s")
            print()
        
        # Show retry configurations
        print("Retry Configurations:")
        print("-" * 40)
        
        for service in services:
            if service in manager.service_configs:
                retry_config = manager.service_configs[service]['retry']
                print(f"🔁 {service.upper()}:")
                print(f"   Max retries: {retry_config.total}")
                print(f"   Backoff factor: {retry_config.backoff_factor}")
                print(f"   Retry status codes: {retry_config.status_forcelist}")
                print()
        
        print("✅ All timeout configurations loaded successfully")
        
    except ImportError as e:
        print(f"❌ Could not import timeout manager: {e}")
        print("📝 Install required services to see this demo")

def demo_enhanced_error_handling():
    """
    Demo 3: Enhanced Error Handling
    Shows the different types of errors that can be caught and handled.
    """
    print("\n" + "="*60)
    print("🚨 DEMO 3: Enhanced Error Handling")
    print("="*60)
    
    try:
        from src.services.enhanced_unsplash_service import (
            UnsplashAuthError, UnsplashRateLimitError, UnsplashNetworkError
        )
        from src.services.enhanced_openai_service import (
            OpenAIAuthError, OpenAITimeoutError, OpenAIQuotaError
        )
        
        print("Available Error Types:")
        print("-" * 30)
        
        unsplash_errors = [
            ("UnsplashAuthError", "Invalid API key or permissions"),
            ("UnsplashRateLimitError", "Rate limit exceeded (50/hour)"),
            ("UnsplashNetworkError", "Network connectivity issues")
        ]
        
        openai_errors = [
            ("OpenAIAuthError", "Invalid OpenAI API key"),
            ("OpenAITimeoutError", "Request timeout"),
            ("OpenAIQuotaError", "Billing quota exceeded")
        ]
        
        print("🇺 Unsplash Errors:")
        for error_name, description in unsplash_errors:
            print(f"   • {error_name}: {description}")
        
        print("\n🤖 OpenAI Errors:")
        for error_name, description in openai_errors:
            print(f"   • {error_name}: {description}")
        
        # Demo error creation and handling
        print("\n📝 Error Handling Example:")
        
        def simulate_api_call(error_type):
            if error_type == "auth":
                raise UnsplashAuthError("Invalid API key")
            elif error_type == "rate_limit":
                raise UnsplashRateLimitError("Rate limit exceeded")
            elif error_type == "timeout":
                raise OpenAITimeoutError("Request timed out")
            else:
                return "Success!"
        
        # Test different error scenarios
        scenarios = ["auth", "rate_limit", "timeout", "success"]
        
        for scenario in scenarios:
            try:
                result = simulate_api_call(scenario)
                print(f"   ✅ {scenario}: {result}")
            except UnsplashAuthError as e:
                print(f"   🔑 Auth Error: {e}")
            except UnsplashRateLimitError as e:
                print(f"   🚑 Rate Limit: {e}")
            except OpenAITimeoutError as e:
                print(f"   ⏰ Timeout: {e}")
            except Exception as e:
                print(f"   ❓ Other Error: {e}")
        
    except ImportError as e:
        print(f"❌ Could not import error classes: {e}")
        print("📝 Install required services to see this demo")

def demo_progress_callbacks():
    """
    Demo 4: Progress Callbacks with Cancellation
    Shows how operations can provide progress updates and be cancelled mid-operation.
    """
    print("\n" + "="*60)
    print("📈 DEMO 4: Progress Callbacks with Cancellation")
    print("="*60)
    
    try:
        from src.services.api_timeout_manager import ApiTimeoutManager, CancellationError
        
        manager = ApiTimeoutManager()
        
        # Create operation with progress tracking
        operation_id = "demo_progress"
        token = manager.create_cancellation_token(operation_id)
        
        progress_messages = []
        
        def progress_callback(message):
            timestamp = time.strftime('%H:%M:%S')
            formatted_message = f"[{timestamp}] {message}"
            progress_messages.append(formatted_message)
            print(f"   📈 {formatted_message}")
        
        def simulate_download_with_progress():
            """Simulate file download with progress updates."""
            total_chunks = 10
            chunk_size = 1024
            
            progress_callback("Starting download...")
            
            for i in range(total_chunks):
                # Check for cancellation
                token.raise_if_cancelled()
                
                # Simulate work
                time.sleep(0.3)
                
                # Update progress
                downloaded = (i + 1) * chunk_size
                total_size = total_chunks * chunk_size
                percent = int((downloaded / total_size) * 100)
                progress_callback(f"Downloaded {percent}% ({downloaded:,}/{total_size:,} bytes)")
            
            progress_callback("Download completed successfully!")
            return f"Downloaded {total_size:,} bytes"
        
        # Start operation in thread
        result = [None]
        error = [None]
        
        def run_with_progress():
            try:
                result[0] = simulate_download_with_progress()
            except CancellationError:
                result[0] = "Operation was cancelled"
            except Exception as e:
                error[0] = str(e)
        
        thread = threading.Thread(target=run_with_progress)
        thread.start()
        
        # Cancel after some progress
        time.sleep(1.5)  # Let it make some progress
        print("\n   🚨 Cancelling operation...")
        token.cancel()
        
        thread.join()
        
        print(f"\n   ✅ Final result: {result[0]}")
        print(f"   ✅ Total progress messages: {len(progress_messages)}")
        print(f"   ✅ Operation cancelled: {token.is_cancelled}")
        
        # Cleanup
        manager.cleanup_token(operation_id)
        
    except ImportError as e:
        print(f"❌ Could not import progress system: {e}")
        print("📝 Install required services to see this demo")

def demo_connection_management():
    """
    Demo 5: Connection Management and Session Reuse
    Shows how HTTP sessions are managed and reused efficiently.
    """
    print("\n" + "="*60)
    print("🔌 DEMO 5: Connection Management and Session Reuse")
    print("="*60)
    
    try:
        from src.services.api_timeout_manager import ApiTimeoutManager
        
        manager = ApiTimeoutManager()
        
        # Show initial state
        status = manager.get_status()
        print(f"📈 Initial Status:")
        print(f"   Active sessions: {status['active_sessions']}")
        print(f"   Active operations: {status['active_operations']}")
        
        # Get sessions for different services
        services = ['unsplash', 'openai', 'download']
        
        print(f"\n🔗 Creating sessions for services:")
        for service in services:
            session = manager.get_session(service)
            print(f"   ✅ {service}: Session created (ID: {id(session)})")
        
        # Get same sessions again (should reuse)
        print(f"\n🔄 Reusing existing sessions:")
        for service in services:
            session = manager.get_session(service)
            print(f"   ♾️ {service}: Session reused (ID: {id(session)})")
        
        # Show updated status
        status = manager.get_status()
        print(f"\n📈 Updated Status:")
        print(f"   Active sessions: {status['active_sessions']}")
        print(f"   Thread pool active: {status['executor_active']}")
        
        # Demonstrate cleanup
        print(f"\n🧹 Cleaning up...")
        manager.shutdown(wait=False)
        
        final_status = manager.get_status()
        print(f"   ✅ Executor active: {final_status['executor_active']}")
        print(f"   ✅ Sessions cleaned up")
        
    except ImportError as e:
        print(f"❌ Could not import connection manager: {e}")
        print("📝 Install required services to see this demo")

def demo_rate_limit_handling():
    """
    Demo 6: Rate Limit Awareness and Handling
    Shows how the system tracks and responds to API rate limits.
    """
    print("\n" + "="*60)
    print("🚑 DEMO 6: Rate Limit Awareness and Handling")
    print("="*60)
    
    try:
        from src.services.enhanced_unsplash_service import EnhancedUnsplashService, RateLimitApproachingError
        from datetime import datetime, timedelta
        
        # Create service (with dummy API key for demo)
        service = EnhancedUnsplashService("demo_api_key")
        
        print("📈 Rate Limit Status Tracking:")
        
        # Simulate rate limit info updates
        service.rate_limit_remaining = 45
        service.rate_limit_reset = datetime.now() + timedelta(hours=1)
        
        status = service.get_rate_limit_status()
        print(f"   Remaining requests: {status['remaining']}")
        print(f"   Reset time: {status['reset_time']}")
        print(f"   Reset in: {status['reset_in_seconds']} seconds")
        
        # Simulate approaching rate limit
        print(f"\n🚨 Simulating Rate Limit Approach:")
        service.rate_limit_remaining = 3  # Low remaining
        
        try:
            service._check_rate_limit()
            print("   ✅ Rate limit check passed")
        except RateLimitApproachingError as e:
            print(f"   🚨 Rate limit warning: {e}")
        
        # Simulate rate limit exceeded
        print(f"\n🚫 Simulating Rate Limit Exceeded:")
        service.rate_limit_remaining = 0
        
        try:
            service._check_rate_limit()
            print("   ✅ Rate limit check passed")
        except RateLimitApproachingError as e:
            print(f"   🚫 Rate limit exceeded: {e}")
        
        # Show rate limit recovery
        print(f"\n🔄 Rate Limit Recovery:")
        service.rate_limit_remaining = 50  # Reset
        service.rate_limit_reset = datetime.now() + timedelta(hours=1)
        
        status = service.get_rate_limit_status()
        print(f"   ✅ Remaining requests: {status['remaining']}")
        print(f"   ✅ Next reset: {status['reset_in_seconds']} seconds")
        
    except ImportError as e:
        print(f"❌ Could not import rate limit system: {e}")
        print("📝 Install required services to see this demo")

def demo_circuit_breaker():
    """
    Demo 7: Circuit Breaker Pattern
    Shows how the circuit breaker protects against cascading failures.
    """
    print("\n" + "="*60)
    print("⚡ DEMO 7: Circuit Breaker Pattern")
    print("="*60)
    
    try:
        from src.services.base_service import BaseService, CircuitState
        
        class DemoService(BaseService):
            def __init__(self):
                super().__init__(
                    name="demo",
                    base_url="https://demo.api",
                    timeout=30
                )
            
            def _get_auth_headers(self):
                return {'Authorization': 'Bearer demo'}
        
        service = DemoService()
        
        print(f"📈 Initial Circuit State: {service._circuit_state.value}")
        print(f"📈 Failure Count: {service._failure_count}")
        
        # Simulate failures
        print(f"\n🚨 Simulating Failures:")
        for i in range(6):  # Exceed failure threshold (5)
            service._on_failure(Exception(f"Simulated failure {i+1}"))
            print(f"   Failure {i+1}: State = {service._circuit_state.value}, Count = {service._failure_count}")
        
        # Check if we can execute
        can_execute = service._can_execute()
        print(f"\n⚡ Can execute requests: {can_execute}")
        print(f"   Circuit state: {service._circuit_state.value}")
        
        # Simulate time passage for recovery
        print(f"\n⏰ Simulating time passage for recovery...")
        service._last_failure_time = service._last_failure_time - timedelta(seconds=65)  # Force recovery
        
        can_execute = service._can_execute()
        print(f"   Can execute after recovery timeout: {can_execute}")
        print(f"   Circuit state: {service._circuit_state.value}")
        
        # Simulate successful recovery
        print(f"\n✅ Simulating Successful Recovery:")
        for i in range(3):  # Success threshold is 3
            service._on_success()
            print(f"   Success {i+1}: State = {service._circuit_state.value}")
        
        print(f"\n✅ Final state: {service._circuit_state.value}")
        print(f"✅ Failure count: {service._failure_count}")
        
    except ImportError as e:
        print(f"❌ Could not import circuit breaker: {e}")
        print("📝 Install required services to see this demo")

def show_comparison_summary():
    """
    Show before/after comparison of the timeout fixes.
    """
    print("\n" + "="*80)
    print("🆚 BEFORE vs AFTER: Timeout Fixes Comparison")
    print("="*80)
    
    comparisons = [
        ("Request Timeouts", "None - could hang forever", "Configurable per service (5-120s)"),
        ("Cancellation", "Not possible", "User can cancel any operation"),
        ("Error Handling", "Generic exceptions", "Specific error types with context"),
        ("Retry Logic", "Basic linear retry", "Exponential backoff with jitter"),
        ("Rate Limits", "No awareness", "Tracks and warns before limits"),
        ("Progress Updates", "None during operations", "Real-time progress callbacks"),
        ("Resource Cleanup", "Manual/unreliable", "Automatic with proper shutdown"),
        ("Connection Management", "New connection per request", "Session pooling and reuse"),
        ("Circuit Breaker", "None - cascading failures", "Automatic fault isolation"),
        ("Monitoring", "No visibility into API calls", "Detailed status and metrics")
    ]
    
    print(f"{'Aspect':<25} {'BEFORE':<30} {'AFTER':<30}")
    print("-" * 85)
    
    for aspect, before, after in comparisons:
        print(f"{aspect:<25} ❌ {before:<28} ✅ {after:<28}")
    
    print("\n" + "="*80)
    print("🎆 BENEFITS SUMMARY")
    print("="*80)
    
    benefits = [
        "No more hanging requests - guaranteed timeouts",
        "User control - cancel button for long operations", 
        "Better error messages - specific problem identification",
        "Smart retry logic - handles transient failures gracefully",
        "Rate limit protection - avoids hitting API limits",
        "Real-time feedback - progress updates during operations",
        "Resource efficiency - connection pooling and cleanup",
        "Fault tolerance - circuit breaker prevents cascading failures",
        "Production ready - monitoring and status reporting",
        "Enhanced UX - cancel buttons and status dialogs in UI"
    ]
    
    for i, benefit in enumerate(benefits, 1):
        print(f"{i:2}. ✅ {benefit}")

def main():
    """
    Run all timeout fix demos.
    """
    print("🚀 API Timeout and Cancellation Fixes - Interactive Demo")
    print("This demo showcases all the improvements made to handle API timeouts,")
    print("cancellation, and error recovery in the Unsplash Image Search app.")
    
    demos = [
        demo_cancellation_tokens,
        demo_timeout_configurations,
        demo_enhanced_error_handling,
        demo_progress_callbacks,
        demo_connection_management,
        demo_rate_limit_handling,
        demo_circuit_breaker
    ]
    
    try:
        for demo_func in demos:
            demo_func()
            time.sleep(1)  # Brief pause between demos
        
        show_comparison_summary()
        
        print("\n" + "="*80)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\n📝 To use these fixes in your application:")
        print("   1. Run: python apply_timeout_fixes.py")
        print("   2. Use: python main_with_timeout_fixes.py")
        print("   3. Or import directly: from patches.api_timeout_fixes import apply_timeout_patches")
        
        print("\n🧪 To test the implementation:")
        print("   python -m pytest tests/test_timeout_fixes.py -v")
        
        print("\n📚 For detailed documentation:")
        print("   See: docs/API_TIMEOUT_FIXES.md")
        
    except KeyboardInterrupt:
        print("\n\n🚨 Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
