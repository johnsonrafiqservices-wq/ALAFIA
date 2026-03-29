@echo off
cd /d "c:\Users\it.sm\Pictures\PhysioNutritionClinic"
python manage.py send_birthday_wishes >> logs\birthday_wishes.log 2>&1
