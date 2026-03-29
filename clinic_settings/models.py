from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class ClinicSettings(models.Model):
    """
    Singleton model to store clinic-wide settings like logo and name.
    Only one instance should exist.
    """
    clinic_name = models.CharField(
        max_length=200,
        default="Alafia Point Wellness Clinic",
        help_text="The name of your clinic"
    )
    logo = models.ImageField(
        upload_to='clinic_logos/',
        blank=True,
        null=True,
        help_text="Upload your clinic logo (recommended size: 200x80px)"
    )
    address = models.TextField(
        blank=True,
        help_text="Clinic address"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Clinic phone number"
    )
    email = models.EmailField(
        blank=True,
        help_text="Clinic email address"
    )
    website = models.URLField(
        blank=True,
        help_text="Clinic website URL"
    )
    
    # Theme Customization Fields
    # Color validator for hex colors
    color_validator = RegexValidator(
        regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        message='Enter a valid hex color code (e.g., #1B5E96)'
    )
    
    # Primary Colors
    primary_color = models.CharField(
        max_length=7,
        default='#1B5E96',
        validators=[color_validator],
        help_text='Primary brand color (default: #1B5E96)'
    )
    primary_dark = models.CharField(
        max_length=7,
        default='#154a7a',
        validators=[color_validator],
        help_text='Dark variant of primary color'
    )
    primary_light = models.CharField(
        max_length=7,
        default='#e6f1fa',
        validators=[color_validator],
        help_text='Light variant of primary color'
    )
    
    # Success Colors
    success_color = models.CharField(
        max_length=7,
        default='#2E8B57',
        validators=[color_validator],
        help_text='Success/positive action color'
    )
    success_dark = models.CharField(
        max_length=7,
        default='#236b43',
        validators=[color_validator],
        help_text='Dark variant of success color'
    )
    success_light = models.CharField(
        max_length=7,
        default='#e8f5f0',
        validators=[color_validator],
        help_text='Light variant of success color'
    )
    
    # Accent Colors
    accent_color = models.CharField(
        max_length=7,
        default='#00A86B',
        validators=[color_validator],
        help_text='Accent/highlight color'
    )
    accent_dark = models.CharField(
        max_length=7,
        default='#008554',
        validators=[color_validator],
        help_text='Dark variant of accent color'
    )
    accent_light = models.CharField(
        max_length=7,
        default='#e6f9f3',
        validators=[color_validator],
        help_text='Light variant of accent color'
    )
    
    # Warning Colors
    warning_color = models.CharField(
        max_length=7,
        default='#FF8C00',
        validators=[color_validator],
        help_text='Warning/caution color'
    )
    warning_dark = models.CharField(
        max_length=7,
        default='#e67e00',
        validators=[color_validator],
        help_text='Dark variant of warning color'
    )
    warning_light = models.CharField(
        max_length=7,
        default='#fff4e6',
        validators=[color_validator],
        help_text='Light variant of warning color'
    )
    
    # Danger Colors
    danger_color = models.CharField(
        max_length=7,
        default='#dc2626',
        validators=[color_validator],
        help_text='Danger/error color'
    )
    danger_dark = models.CharField(
        max_length=7,
        default='#b91c1c',
        validators=[color_validator],
        help_text='Dark variant of danger color'
    )
    danger_light = models.CharField(
        max_length=7,
        default='#fecaca',
        validators=[color_validator],
        help_text='Light variant of danger color'
    )
    
    # Info Colors
    info_color = models.CharField(
        max_length=7,
        default='#0891b2',
        validators=[color_validator],
        help_text='Info/informational color'
    )
    info_dark = models.CharField(
        max_length=7,
        default='#0e7490',
        validators=[color_validator],
        help_text='Dark variant of info color'
    )
    info_light = models.CharField(
        max_length=7,
        default='#cffafe',
        validators=[color_validator],
        help_text='Light variant of info color'
    )
    
    # Secondary/Neutral Colors
    secondary_color = models.CharField(
        max_length=7,
        default='#64748b',
        validators=[color_validator],
        help_text='Secondary/neutral color'
    )
    secondary_dark = models.CharField(
        max_length=7,
        default='#475569',
        validators=[color_validator],
        help_text='Dark variant of secondary color'
    )
    secondary_light = models.CharField(
        max_length=7,
        default='#f1f5f9',
        validators=[color_validator],
        help_text='Light variant of secondary color'
    )
    
    # Base Colors
    dark_color = models.CharField(
        max_length=7,
        default='#1e293b',
        validators=[color_validator],
        help_text='Dark text/background color'
    )
    light_color = models.CharField(
        max_length=7,
        default='#f8fafc',
        validators=[color_validator],
        help_text='Light background color'
    )
    border_color = models.CharField(
        max_length=7,
        default='#e2e8f0',
        validators=[color_validator],
        help_text='Border color'
    )
    
    # Text Colors
    text_primary = models.CharField(
        max_length=7,
        default='#1e293b',
        validators=[color_validator],
        help_text='Primary text color'
    )
    text_secondary = models.CharField(
        max_length=7,
        default='#64748b',
        validators=[color_validator],
        help_text='Secondary text color'
    )
    text_muted = models.CharField(
        max_length=7,
        default='#94a3b8',
        validators=[color_validator],
        help_text='Muted text color'
    )
    
    # Background Colors
    bg_primary = models.CharField(
        max_length=7,
        default='#ffffff',
        validators=[color_validator],
        help_text='Primary background color'
    )
    bg_secondary = models.CharField(
        max_length=7,
        default='#f8fafc',
        validators=[color_validator],
        help_text='Secondary background color'
    )
    bg_tertiary = models.CharField(
        max_length=7,
        default='#f1f5f9',
        validators=[color_validator],
        help_text='Tertiary background color'
    )
    
    # Chart Colors (for graphs and visualizations)
    chart_color_1 = models.CharField(
        max_length=7,
        default='#1B5E96',
        validators=[color_validator],
        help_text='Chart color 1'
    )
    chart_color_2 = models.CharField(
        max_length=7,
        default='#2E8B57',
        validators=[color_validator],
        help_text='Chart color 2'
    )
    chart_color_3 = models.CharField(
        max_length=7,
        default='#00A86B',
        validators=[color_validator],
        help_text='Chart color 3'
    )
    chart_color_4 = models.CharField(
        max_length=7,
        default='#FF8C00',
        validators=[color_validator],
        help_text='Chart color 4'
    )
    chart_color_5 = models.CharField(
        max_length=7,
        default='#0891b2',
        validators=[color_validator],
        help_text='Chart color 5'
    )
    chart_color_6 = models.CharField(
        max_length=7,
        default='#dc2626',
        validators=[color_validator],
        help_text='Chart color 6'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Clinic Settings"
        verbose_name_plural = "Clinic Settings"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and ClinicSettings.objects.exists():
            raise ValidationError('Only one ClinicSettings instance is allowed.')
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get or create the clinic settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

    def __str__(self):
        return f"Settings for {self.clinic_name}"
