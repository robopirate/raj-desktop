try:
    import engine
    print("Syntax OK")
except SyntaxError as e:
    print(f"Syntax ERROR: {e}")
except Exception as e:
    print(f"Import OK (runtime error: {e})")
