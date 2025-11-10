"""
Test script for Phase 1 - Provider Abstraction Layer
Run this to verify all providers are loaded correctly
"""
import asyncio
import sys

print("=" * 60)
print("PHASE 1 TEST - Provider Abstraction Layer")
print("=" * 60)
print()

# Test 1: Configuration Loading
print("Test 1: Loading Configuration...")
try:
    from backend.config.settings import settings
    print(f"✓ App Name: {settings.app_name}")
    print(f"✓ Database URL: {settings.database_url}")
    print(f"✓ OpenAI Key exists: {bool(settings.openai_api_key)}")
    print(f"✓ Gemini Key exists: {bool(settings.gemini_api_key)}")
    print(f"✓ Tavily Key exists: {bool(settings.tavily_api_key)}")
    print()
except Exception as e:
    print(f"❌ Configuration loading failed: {e}")
    sys.exit(1)

# Test 2: Model Factory
print("Test 2: Loading Model Factory...")
try:
    from backend.core.model_factory import model_factory
    print()
except Exception as e:
    print(f"❌ Model factory failed: {e}")
    sys.exit(1)

# Test 3: List Available Providers
print("Test 3: Checking Available Providers...")
try:
    providers = model_factory.get_available_providers()
    print(f"✓ Available providers: {providers}")
    
    if not providers:
        print("⚠️  No providers loaded. Make sure you've added API keys to .env file!")
        print("   Edit .env and add your OPENAI_API_KEY and/or GEMINI_API_KEY")
    print()
except Exception as e:
    print(f"❌ Provider check failed: {e}")
    sys.exit(1)

# Test 4: List All Models
print("Test 4: Listing All Models...")
try:
    all_models = model_factory.get_all_models()
    
    for provider_name, models in all_models.items():
        print(f"\n{provider_name.upper()} Models:")
        for model in models:
            print(f"  ✓ {model.display_name} ({model.name})")
            print(f"    Context: {model.context_window:,} tokens")
            print(f"    Vision: {model.supports_vision}")
            print(f"    Tools: {model.supports_tools}")
            print(f"    Cost: ${model.cost_per_1m_input_tokens:.2f} / ${model.cost_per_1m_output_tokens:.2f} per 1M tokens")
    
    if not all_models:
        print("⚠️  No models available. Add API keys to .env file!")
    print()
except Exception as e:
    print(f"❌ Model listing failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Token Counting
print("Test 5: Testing Token Counting...")
try:
    if 'openai' in model_factory.get_available_providers():
        openai_provider = model_factory.get_provider('openai')
        test_messages = [
            {"role": "user", "content": "Hello! How are you?"}
        ]
        token_count = openai_provider.count_tokens(test_messages, "gpt-3.5-turbo")
        print(f"✓ Token count for test message: {token_count} tokens")
    else:
        print("⚠️  OpenAI provider not available, skipping token test")
    print()
except Exception as e:
    print(f"⚠️  Token counting test failed (non-critical): {e}")
    print()

# Test 6: Cost Calculation
print("Test 6: Testing Cost Calculation...")
try:
    if 'openai' in model_factory.get_available_providers():
        model_info = model_factory.get_model_info('openai', 'gpt-4o-mini')
        if model_info:
            cost = model_info.calculate_cost(1000, 500)
            print(f"✓ Cost for 1000 input + 500 output tokens: ${cost:.6f}")
    print()
except Exception as e:
    print(f"⚠️  Cost calculation test failed: {e}")
    print()

# Summary
print("=" * 60)
print("PHASE 1 TEST SUMMARY")
print("=" * 60)
print()

providers = model_factory.get_available_providers()
all_models = model_factory.get_all_models()
total_models = sum(len(models) for models in all_models.values())

if providers:
    print(f"✅ SUCCESS! Phase 1 is working!")
    print(f"   - {len(providers)} provider(s) loaded")
    print(f"   - {total_models} model(s) available")
    print()
    print("Next steps:")
    print("  1. Make sure your API keys are in .env file")
    print("  2. Proceed to Phase 2 (Database & Chat Management)")
    print("  3. Follow PROJECT_PLAN.md - Phase 2, Task 2.1")
else:
    print("⚠️  Phase 1 code works, but no providers loaded!")
    print()
    print("ACTION REQUIRED:")
    print("  1. Edit the .env file in your project root")
    print("  2. Add your API keys:")
    print("     OPENAI_API_KEY=sk-proj-...")
    print("     GEMINI_API_KEY=AIza...")
    print("  3. Run this test again: python test_phase1.py")

print()
print("=" * 60)

