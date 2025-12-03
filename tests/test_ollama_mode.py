#!/usr/bin/env python3
"""
Prosty test wywołania Ollama z automatycznym wyborem trybu.
"""

import sys
import os

# Dodaj katalog scripts do PATH (bo test jest teraz w tests/)
scripts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')
sys.path.insert(0, scripts_path)

from run_ollama_with_mode import get_mode, get_settings_for_mode, call_ollama_streaming


def main():
    print("=" * 60)
    print("🧪 TEST AUTOMATYCZNEGO WYBORU TRYBU OLLAMA")
    print("=" * 60)
    print()
    
    # 1. Wykryj i wyświetl tryb
    mode = get_mode()
    settings = get_settings_for_mode(mode)
    
    print(f"\n⚙️  Ustawienia dla trybu '{mode}':")
    print(f"   • Model: {settings['model']}")
    print(f"   • Max tokens: {settings['max_tokens']}")
    print(f"   • Temperature: {settings['temperature']}")
    print()
    
    # 2. Prosty test
    test_prompts = [
        "Powiedz 'Działa!' jeśli mnie rozumiesz.",
        "Jaka jest stolica Polski?",
        "Policz do 5."
    ]
    
    print("📋 Testy:")
    print()
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n[Test {i}/{len(test_prompts)}]")
        print(f"❓ Pytanie: {prompt}")
        print(f"💬 Odpowiedź: ", end="")
        
        try:
            response = call_ollama_streaming(prompt, settings)
            print(f"\n✅ Test {i} zakończony")
        except KeyboardInterrupt:
            print("\n\n⏸️  Przerwano przez użytkownika")
            break
        except Exception as e:
            print(f"\n❌ Błąd: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Testy zakończone!")
    print("=" * 60)


if __name__ == "__main__":
    main()
