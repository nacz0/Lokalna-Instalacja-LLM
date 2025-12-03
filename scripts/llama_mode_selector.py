def get_settings_for_mode(mode):
    if mode == "light":
        return {
            "model": "phi3:mini",
            "max_tokens": 256,
            "temperature": 0.3
        }

    elif mode == "balanced":
        return {
            "model": "llama3:latest",
            "max_tokens": 512,
            "temperature": 0.5
        }

    elif mode == "advanced":
        return {
            "model": "llama3.1:latest",
            "max_tokens": 1024,
            "temperature": 0.7
        }
