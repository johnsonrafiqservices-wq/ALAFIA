#!/usr/bin/env python
"""
Setup script for Django Jet Reboot installation
Run this script to install and configure Django Jet Reboot for the clinic system
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during {description}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("Django Jet Reboot Setup for PhysioNutrition Clinic")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("Error: Please run this script from the project root directory (where manage.py is located)")
        sys.exit(1)
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        print("Failed to install requirements. Please install manually:")
        print("pip install django-jet-reboot==1.3.7")
        return
    
    # Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        print("Warning: Failed to collect static files. You may need to run this manually later.")
    
    # Run migrations for Django Jet
    if not run_command("python manage.py migrate jet", "Running Jet migrations"):
        print("Warning: Failed to run Jet migrations. You may need to run this manually later.")
    
    if not run_command("python manage.py migrate dashboard", "Running Dashboard migrations"):
        print("Warning: Failed to run Dashboard migrations. You may need to run this manually later.")
    
    # Run all migrations
    if not run_command("python manage.py migrate", "Running all migrations"):
        print("Warning: Failed to run all migrations. You may need to run this manually later.")
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start your Django development server: python manage.py runserver")
    print("2. Visit http://127.0.0.1:8000/admin/ to see the new Django Jet Reboot interface")
    print("3. Log in with your admin credentials")
    print("\nFeatures available:")
    print("- Modern, responsive admin interface")
    print("- Custom dashboard with clinic-specific modules")
    print("- Multiple theme options")
    print("- Organized menu structure for clinic management")
    print("- Quick action links for common tasks")
    
    print("\nTo customize further:")
    print("- Edit clinic_system/dashboard.py to modify the dashboard")
    print("- Adjust JET_* settings in clinic_system/settings.py")
    print("- Change themes in the admin interface user preferences")

if __name__ == "__main__":
    main()
