"""Minimal test to see if app can be created and run"""
import sys
import traceback

def main():
    try:
        print("Testing Flask app creation...")
        
        # Test 1: Import
        print("1. Importing create_app...")
        from app import create_app
        print("   ✓ Import successful")
        
        # Test 2: Create app
        print("2. Creating app instance...")
        app = create_app()
        print("   ✓ App created successfully")
        print(f"   App name: {app.name}")
        print(f"   Registered blueprints: {list(app.blueprints.keys())}")
        
        # Test 3: Test configuration
        print("3. Checking configuration...")
        print(f"   SECRET_KEY set: {bool(app.config.get('SECRET_KEY'))}")
        print(f"   DATABASE_URL: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        
        # Test 4: Try to bind to port
        print("4. Testing port binding...")
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('127.0.0.1', 5000))
            print("   ✓ Port 5000 is available")
            sock.close()
        except OSError as e:
            print(f"   ✗ Port 5000 is NOT available: {e}")
            sock.close()
            return
        
        # Test 5: Keep alive
        print("5. Starting server (will block)...")
        print("   Server starting on http://127.0.0.1:5000")
        print("   Press Ctrl+C to quit")
        
        # Use a simple blocking call
        from waitress import serve
        serve(app, host='127.0.0.1', port=5000, _quiet=False)
        
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
    except Exception as e:
        print(f"\n✗ ERROR: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
