"""
Launcher script for Sargam Transcriber GUI
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui_app import main
    
    if __name__ == "__main__":
        print("🎵 Starting Sargam Transcriber Pro...")
        main()
        
except ImportError as e:
    print(f"❌ Error: Missing dependencies!")
    print(f"Please install required packages:")
    print(f"pip install -r requirements.txt")
    print(f"\nError details: {e}")
    input("Press Enter to exit...")
except Exception as e:
    print(f"❌ Error starting application: {e}")
    input("Press Enter to exit...")
