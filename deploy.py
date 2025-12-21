"""
Deployment script for FinGPT Analyst
"""

import subprocess
import sys
import os

def install_requirements():
    """Install all required packages from requirements.txt"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def check_environment_variables():
    """Check if required environment variables are set"""
    required_vars = ["GOOGLE_API_KEY"]
    optional_vars = ["SERPER_API_KEY", "EXA_API_KEY"]
    
    print("Checking environment variables...")
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        print(f"❌ Missing required environment variables: {missing_required}")
        print("Please set these variables before running the application.")
        return False
    
    print("✅ All required environment variables are set!")
    
    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_optional:
        print(f"⚠ Note: Optional environment variables not set: {missing_optional}")
        print("Some features may be limited without these.")
    
    return True

def run_app():
    """Run the Streamlit application"""
    try:
        subprocess.run(["streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running the application: {e}")
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install requirements first.")

def main():
    """Main deployment function"""
    print("🚀 FinGPT Analyst Deployment Script")
    print("=" * 40)
    
    # Check if running in deployment mode
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        print("Installing requirements...")
        if install_requirements():
            print("\n🎉 Installation complete!")
            print("Next steps:")
            print("1. Set your environment variables (especially GOOGLE_API_KEY)")
            print("2. Run 'python deploy.py' to start the application")
    elif len(sys.argv) > 1 and sys.argv[1] == "check-env":
        check_environment_variables()
    else:
        if check_environment_variables():
            print("\n🚀 Starting FinGPT Analyst...")
            run_app()

if __name__ == "__main__":
    main()