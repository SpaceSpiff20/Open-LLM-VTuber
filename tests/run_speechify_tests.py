#!/usr/bin/env python3
"""
Test runner for Speechify TTS migration.

This script runs comprehensive tests to verify that the Speechify TTS migration
was successful and all functionality works correctly.
"""

import os
import sys
import subprocess
import unittest
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def run_unit_tests():
    """Run unit tests for Speechify TTS."""
    print("🧪 Running Speechify TTS unit tests...")
    
    # Import and run the test suite
    from test_speechify_tts import TestSpeechifyTTS
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSpeechifyTTS)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_integration_tests():
    """Run integration tests for Speechify TTS (requires API key)."""
    print("🔗 Running Speechify TTS integration tests...")
    
    # Check if API key is available
    api_key = os.getenv("SPEECHIFY_API_KEY")
    if not api_key:
        print("⚠️  SPEECHIFY_API_KEY environment variable not set. Skipping integration tests.")
        return True
    
    # Import and run integration tests
    from test_speechify_tts import TestSpeechifyTTSIntegration
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSpeechifyTTSIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def test_imports():
    """Test that all required modules can be imported."""
    print("📦 Testing imports...")
    
    try:
        from open_llm_vtuber.tts.speechify_tts import TTSEngine
        print("✅ Speechify TTS module imported successfully")
        
        from open_llm_vtuber.tts.tts_factory import TTSFactory
        print("✅ TTS Factory imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_factory_integration():
    """Test that Speechify TTS is properly integrated into the factory."""
    print("🏭 Testing TTS Factory integration...")
    
    try:
        from open_llm_vtuber.tts.tts_factory import TTSFactory
        
        # Test that the factory can create a Speechify TTS engine
        tts_engine = TTSFactory.get_tts_engine(
            "speechify_tts",
            api_key="test_key",
            voice_id="scott",
            model="simba-english"
        )
        
        print("✅ TTS Factory can create Speechify TTS engine")
        return True
    except Exception as e:
        print(f"❌ Factory integration test failed: {e}")
        return False


def test_config_validation():
    """Test that the configuration structure is valid."""
    print("⚙️  Testing configuration validation...")
    
    try:
        import yaml
        
        # Test English config
        with open("../config_templates/conf.default.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        # Check that speechify_tts section exists
        if 'character_config' in config and 'tts_config' in config['character_config']:
            tts_config = config['character_config']['tts_config']
            if 'speechify_tts' in tts_config:
                print("✅ English config contains speechify_tts section")
            else:
                print("❌ English config missing speechify_tts section")
                return False
        else:
            print("❌ English config structure is invalid")
            return False
        
        # Test Chinese config
        with open("../config_templates/conf.ZH.default.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        if 'character_config' in config and 'tts_config' in config['character_config']:
            tts_config = config['character_config']['tts_config']
            if 'speechify_tts' in tts_config:
                print("✅ Chinese config contains speechify_tts section")
            else:
                print("❌ Chinese config missing speechify_tts section")
                return False
        else:
            print("❌ Chinese config structure is invalid")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


def test_dependencies():
    """Test that all required dependencies are available."""
    print("📚 Testing dependencies...")
    
    try:
        import speechify
        print("✅ speechify-api package is available")
        
        from speechify import Speechify
        from speechify.tts import GetSpeechOptionsRequest
        print("✅ Speechify classes can be imported")
        
        return True
    except ImportError as e:
        print(f"❌ Dependency test failed: {e}")
        return False


def run_code_quality_checks():
    """Run code quality checks."""
    print("🔍 Running code quality checks...")
    
    try:
        # Run ruff format check
        result = subprocess.run(
            ["uv", "run", "ruff", "format", "--check", "../src/open_llm_vtuber/tts/speechify_tts.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Code formatting is correct")
        else:
            print("❌ Code formatting issues found")
            print(result.stdout)
            return False
        
        # Run ruff lint check
        result = subprocess.run(
            ["uv", "run", "ruff", "check", "../src/open_llm_vtuber/tts/speechify_tts.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Code linting passed")
        else:
            print("❌ Code linting issues found")
            print(result.stdout)
            return False
        
        return True
    except Exception as e:
        print(f"❌ Code quality check failed: {e}")
        return False


def main():
    """Main test runner function."""
    print("🚀 Starting Speechify TTS Migration Test Suite")
    print("=" * 50)
    
    # Change to the tests directory
    os.chdir(os.path.dirname(__file__))
    
    # Run all tests
    tests = [
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("Configuration", test_config_validation),
        ("Factory Integration", test_factory_integration),
        ("Code Quality", run_code_quality_checks),
        ("Unit Tests", run_unit_tests),
        ("Integration Tests", run_integration_tests),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} Test")
        print("-" * 30)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Speechify TTS migration is successful.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 