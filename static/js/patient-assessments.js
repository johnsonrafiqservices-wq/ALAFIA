/**
 * Patient Assessment Forms - Complete Reconstruction
 * Version: 3.1 - Follow-up Time Fields Active
 * Date: November 18, 2025
 * 
 * This file handles ALL assessment form submissions via AJAX
 * Including: Physiotherapy, Nutrition, and General assessments
 * 
 * v3.1 Features:
 * - Follow-up time selector fields (hour, minute, AM/PM) now active
 * - Automatic time conversion to 24-hour format
 * - Real-time time field updates
 */

console.log('🚀 Patient Assessment Module v3.1 Loaded - Follow-up Time Active');
console.log('⏰ Loaded at:', new Date().toISOString());

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Get CSRF token from cookies
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Clear validation errors from form
 */
function clearValidationErrors(form) {
    const invalidFields = form.querySelectorAll('.is-invalid');
    invalidFields.forEach(field => {
        field.classList.remove('is-invalid');
    });
    
    const errorMessages = form.querySelectorAll('.invalid-feedback');
    errorMessages.forEach(error => {
        error.remove();
    });
}

/**
 * Show field-specific error
 */
function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    field.classList.add('is-invalid');
    
    // Remove existing error
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback d-block';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

/**
 * Display multiple form errors
 */
function displayFormErrors(errors) {
    for (const [fieldName, errorMessages] of Object.entries(errors)) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            showFieldError(field.id, errorMessages.join(', '));
        }
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
    
    // Scroll to alert
    alertDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// =============================================================================
// PHYSIOTHERAPY ASSESSMENT
// =============================================================================

/**
 * Submit Physiotherapy Assessment Form via AJAX
 */
function submitPhysiotherapyAssessmentForm() {
    console.log('🏥 Submitting Physiotherapy Assessment - v3.0');
    
    const form = document.getElementById('physiotherapyAssessmentForm');
    if (!form) {
        console.error('❌ Physiotherapy form not found');
        return;
    }
    
    // Combine time fields before submission
    combineTimeFields(
        'id_physio_follow_up_hour',
        'id_physio_follow_up_minute',
        'id_physio_follow_up_period',
        'id_physio_follow_up_time'
    );
    
    const formData = new FormData(form);
    const csrftoken = getCookie('csrftoken');
    
    console.log('🔑 CSRF Token:', csrftoken ? 'Found' : 'Missing');
    
    // Clear previous errors
    clearValidationErrors(form);
    
    // Client-side validation
    const assessmentType = form.querySelector('[name="assessment_type"]')?.value;
    const chiefComplaint = form.querySelector('[name="chief_complaint"]')?.value?.trim();
    
    if (!assessmentType || !chiefComplaint) {
        if (!assessmentType) {
            showFieldError('id_physio_assessment_type', 'Assessment Type is required');
        }
        if (!chiefComplaint) {
            showFieldError('id_physio_chief_complaint', 'Chief Complaint is required');
        }
        showAlert('Please fill in all required fields.', 'warning');
        return;
    }
    
    // Submit via AJAX
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('✅ Physiotherapy assessment saved successfully');
            showAlert(data.message, 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('physiotherapyAssessmentModal'));
            if (modal) modal.hide();
            
            // Reload page after short delay
            setTimeout(() => location.reload(), 2000);
        } else {
            console.error('❌ Validation errors:', data.errors);
            if (data.errors) {
                displayFormErrors(data.errors);
            }
            showAlert(data.message || 'Please correct the errors.', 'danger');
        }
    })
    .catch(error => {
        console.error('❌ Error submitting form:', error);
        showAlert('An error occurred. Please try again.', 'danger');
    });
}

// =============================================================================
// NUTRITION ASSESSMENT
// =============================================================================

/**
 * Submit Nutrition Assessment Form via AJAX
 */
function submitNutritionAssessmentForm() {
    console.log('🥗 Submitting Nutrition Assessment - v3.0');
    
    const form = document.getElementById('nutritionAssessmentForm');
    if (!form) {
        console.error('❌ Nutrition form not found');
        return;
    }
    
    // Combine time fields before submission
    combineTimeFields(
        'id_nutrition_follow_up_hour',
        'id_nutrition_follow_up_minute',
        'id_nutrition_follow_up_period',
        'id_nutrition_follow_up_time'
    );
    
    const formData = new FormData(form);
    const csrftoken = getCookie('csrftoken');
    
    console.log('🔑 CSRF Token:', csrftoken ? 'Found' : 'Missing');
    
    // Clear previous errors
    clearValidationErrors(form);
    
    // Client-side validation
    const assessmentType = form.querySelector('[name="assessment_type"]')?.value;
    const chiefComplaint = form.querySelector('[name="chief_complaint"]')?.value?.trim();
    
    if (!assessmentType || !chiefComplaint) {
        if (!assessmentType) {
            showFieldError('id_nutrition_assessment_type', 'Assessment Type is required');
        }
        if (!chiefComplaint) {
            showFieldError('id_nutrition_chief_complaint', 'Chief Complaint is required');
        }
        showAlert('Please fill in all required fields.', 'warning');
        return;
    }
    
    // Submit via AJAX
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('✅ Nutrition assessment saved successfully');
            showAlert(data.message, 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('nutritionAssessmentModal'));
            if (modal) modal.hide();
            
            // Reload page after short delay
            setTimeout(() => location.reload(), 2000);
        } else {
            console.error('❌ Validation errors:', data.errors);
            if (data.errors) {
                displayFormErrors(data.errors);
            }
            showAlert(data.message || 'Please correct the errors.', 'danger');
        }
    })
    .catch(error => {
        console.error('❌ Error submitting form:', error);
        showAlert('An error occurred. Please try again.', 'danger');
    });
}

// =============================================================================
// GENERAL ASSESSMENT
// =============================================================================

/**
 * Submit General Assessment Form via AJAX
 */
function submitGeneralAssessmentForm() {
    console.log('🏥 Submitting General Assessment - v3.0');
    
    const form = document.getElementById('generalAssessmentForm');
    if (!form) {
        console.error('❌ General assessment form not found');
        return;
    }
    
    // Combine time fields before submission
    combineTimeFields(
        'id_follow_up_hour',
        'id_follow_up_minute',
        'id_follow_up_period',
        'id_follow_up_time'
    );
    
    const formData = new FormData(form);
    const csrftoken = getCookie('csrftoken');
    
    console.log('🔑 CSRF Token:', csrftoken ? 'Found' : 'Missing');
    
    // Clear previous errors
    clearValidationErrors(form);
    
    // Client-side validation
    const assessmentType = form.querySelector('[name="assessment_type"]')?.value;
    const chiefComplaint = form.querySelector('[name="chief_complaint"]')?.value?.trim();
    
    if (!assessmentType || !chiefComplaint) {
        if (!assessmentType) {
            showFieldError('id_assessment_type', 'Assessment Type is required');
        }
        if (!chiefComplaint) {
            showFieldError('id_chief_complaint', 'Chief Complaint is required');
        }
        showAlert('Please fill in all required fields.', 'warning');
        return;
    }
    
    // Submit via AJAX
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('✅ General assessment saved successfully');
            showAlert(data.message, 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('generalAssessmentModal'));
            if (modal) modal.hide();
            
            // Reload page after short delay
            setTimeout(() => location.reload(), 2000);
        } else {
            console.error('❌ Validation errors:', data.errors);
            if (data.errors) {
                displayFormErrors(data.errors);
            }
            showAlert(data.message || 'Please correct the errors.', 'danger');
        }
    })
    .catch(error => {
        console.error('❌ Error submitting form:', error);
        showAlert('An error occurred. Please try again.', 'danger');
    });
}

// =============================================================================
// FOLLOW-UP FIELD HANDLERS
// =============================================================================

/**
 * Combine time selector values into hidden time field
 */
function combineTimeFields(hourId, minuteId, periodId, hiddenTimeId) {
    const hourSelect = document.getElementById(hourId);
    const minuteSelect = document.getElementById(minuteId);
    const periodSelect = document.getElementById(periodId);
    const hiddenTime = document.getElementById(hiddenTimeId);
    
    if (hourSelect && minuteSelect && periodSelect && hiddenTime) {
        const hour = hourSelect.value;
        const minute = minuteSelect.value;
        const period = periodSelect.value;
        
        if (hour && minute && period) {
            // Convert to 24-hour format
            let hour24 = parseInt(hour);
            if (period === 'PM' && hour24 !== 12) {
                hour24 += 12;
            } else if (period === 'AM' && hour24 === 12) {
                hour24 = 0;
            }
            
            // Format as HH:MM:SS
            const timeString = `${String(hour24).padStart(2, '0')}:${minute}:00`;
            hiddenTime.value = timeString;
            console.log(`🕐 Combined time: ${hour}:${minute} ${period} → ${timeString}`);
        }
    }
}

/**
 * Setup follow-up field handlers for all assessment forms
 */
function setupFollowUpHandlers() {
    console.log('⚙️ Setting up follow-up handlers');
    
    // Physiotherapy Assessment
    const physioCheckbox = document.getElementById('id_physio_follow_up_required');
    const physioDate = document.getElementById('id_physio_follow_up_date');
    const physioHour = document.getElementById('id_physio_follow_up_hour');
    const physioMinute = document.getElementById('id_physio_follow_up_minute');
    const physioPeriod = document.getElementById('id_physio_follow_up_period');
    const physioNotes = document.getElementById('id_physio_follow_up_notes');
    
    if (physioCheckbox) {
        physioCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            if (physioDate) physioDate.disabled = !isChecked;
            if (physioHour) physioHour.disabled = !isChecked;
            if (physioMinute) physioMinute.disabled = !isChecked;
            if (physioPeriod) physioPeriod.disabled = !isChecked;
            if (physioNotes) physioNotes.disabled = !isChecked;
            
            if (!isChecked) {
                if (physioDate) physioDate.value = '';
                if (physioHour) physioHour.selectedIndex = 0;
                if (physioMinute) physioMinute.selectedIndex = 0;
                if (physioPeriod) physioPeriod.selectedIndex = 0;
                if (physioNotes) physioNotes.value = '';
            }
        });
        
        // Add time field change listeners
        if (physioHour) {
            physioHour.addEventListener('change', function() {
                combineTimeFields('id_physio_follow_up_hour', 'id_physio_follow_up_minute', 'id_physio_follow_up_period', 'id_physio_follow_up_time');
            });
        }
        if (physioMinute) {
            physioMinute.addEventListener('change', function() {
                combineTimeFields('id_physio_follow_up_hour', 'id_physio_follow_up_minute', 'id_physio_follow_up_period', 'id_physio_follow_up_time');
            });
        }
        if (physioPeriod) {
            physioPeriod.addEventListener('change', function() {
                combineTimeFields('id_physio_follow_up_hour', 'id_physio_follow_up_minute', 'id_physio_follow_up_period', 'id_physio_follow_up_time');
            });
        }
        
        // Initialize state
        if (physioDate) physioDate.disabled = !physioCheckbox.checked;
        if (physioHour) physioHour.disabled = !physioCheckbox.checked;
        if (physioMinute) physioMinute.disabled = !physioCheckbox.checked;
        if (physioPeriod) physioPeriod.disabled = !physioCheckbox.checked;
        if (physioNotes) physioNotes.disabled = !physioCheckbox.checked;
    }
    
    // Nutrition Assessment
    const nutritionCheckbox = document.getElementById('id_nutrition_follow_up_required');
    const nutritionDate = document.getElementById('id_nutrition_follow_up_date');
    const nutritionHour = document.getElementById('id_nutrition_follow_up_hour');
    const nutritionMinute = document.getElementById('id_nutrition_follow_up_minute');
    const nutritionPeriod = document.getElementById('id_nutrition_follow_up_period');
    const nutritionInstructions = document.getElementById('id_nutrition_follow_up_instructions');
    
    if (nutritionCheckbox) {
        nutritionCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            if (nutritionDate) nutritionDate.disabled = !isChecked;
            if (nutritionHour) nutritionHour.disabled = !isChecked;
            if (nutritionMinute) nutritionMinute.disabled = !isChecked;
            if (nutritionPeriod) nutritionPeriod.disabled = !isChecked;
            if (nutritionInstructions) nutritionInstructions.disabled = !isChecked;
            
            if (!isChecked) {
                if (nutritionDate) nutritionDate.value = '';
                if (nutritionHour) nutritionHour.selectedIndex = 0;
                if (nutritionMinute) nutritionMinute.selectedIndex = 0;
                if (nutritionPeriod) nutritionPeriod.selectedIndex = 0;
                if (nutritionInstructions) nutritionInstructions.value = '';
            }
        });
        
        // Add time field change listeners
        if (nutritionHour) {
            nutritionHour.addEventListener('change', function() {
                combineTimeFields('id_nutrition_follow_up_hour', 'id_nutrition_follow_up_minute', 'id_nutrition_follow_up_period', 'id_nutrition_follow_up_time');
            });
        }
        if (nutritionMinute) {
            nutritionMinute.addEventListener('change', function() {
                combineTimeFields('id_nutrition_follow_up_hour', 'id_nutrition_follow_up_minute', 'id_nutrition_follow_up_period', 'id_nutrition_follow_up_time');
            });
        }
        if (nutritionPeriod) {
            nutritionPeriod.addEventListener('change', function() {
                combineTimeFields('id_nutrition_follow_up_hour', 'id_nutrition_follow_up_minute', 'id_nutrition_follow_up_period', 'id_nutrition_follow_up_time');
            });
        }
        
        // Initialize state
        if (nutritionDate) nutritionDate.disabled = !nutritionCheckbox.checked;
        if (nutritionHour) nutritionHour.disabled = !nutritionCheckbox.checked;
        if (nutritionMinute) nutritionMinute.disabled = !nutritionCheckbox.checked;
        if (nutritionPeriod) nutritionPeriod.disabled = !nutritionCheckbox.checked;
        if (nutritionInstructions) nutritionInstructions.disabled = !nutritionCheckbox.checked;
    }
    
    // General Assessment
    const generalCheckbox = document.getElementById('id_follow_up_required');
    const generalDate = document.getElementById('id_follow_up_date');
    const generalHour = document.getElementById('id_follow_up_hour');
    const generalMinute = document.getElementById('id_follow_up_minute');
    const generalPeriod = document.getElementById('id_follow_up_period');
    const generalInstructions = document.getElementById('id_follow_up_instructions');
    
    if (generalCheckbox) {
        generalCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            if (generalDate) generalDate.disabled = !isChecked;
            if (generalHour) generalHour.disabled = !isChecked;
            if (generalMinute) generalMinute.disabled = !isChecked;
            if (generalPeriod) generalPeriod.disabled = !isChecked;
            if (generalInstructions) generalInstructions.disabled = !isChecked;
            
            if (!isChecked) {
                if (generalDate) generalDate.value = '';
                if (generalHour) generalHour.selectedIndex = 0;
                if (generalMinute) generalMinute.selectedIndex = 0;
                if (generalPeriod) generalPeriod.selectedIndex = 0;
                if (generalInstructions) generalInstructions.value = '';
            }
        });
        
        // Add time field change listeners
        if (generalHour) {
            generalHour.addEventListener('change', function() {
                combineTimeFields('id_follow_up_hour', 'id_follow_up_minute', 'id_follow_up_period', 'id_follow_up_time');
            });
        }
        if (generalMinute) {
            generalMinute.addEventListener('change', function() {
                combineTimeFields('id_follow_up_hour', 'id_follow_up_minute', 'id_follow_up_period', 'id_follow_up_time');
            });
        }
        if (generalPeriod) {
            generalPeriod.addEventListener('change', function() {
                combineTimeFields('id_follow_up_hour', 'id_follow_up_minute', 'id_follow_up_period', 'id_follow_up_time');
            });
        }
        
        // Initialize state
        if (generalDate) generalDate.disabled = !generalCheckbox.checked;
        if (generalHour) generalHour.disabled = !generalCheckbox.checked;
        if (generalMinute) generalMinute.disabled = !generalCheckbox.checked;
        if (generalPeriod) generalPeriod.disabled = !generalCheckbox.checked;
        if (generalInstructions) generalInstructions.disabled = !generalCheckbox.checked;
    }
}

// =============================================================================
// INITIALIZATION
// =============================================================================

// Setup when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAssessments);
} else {
    initializeAssessments();
}

function initializeAssessments() {
    console.log('🎬 Initializing Assessment System v3.1 - Follow-up Time Active');
    
    // Make functions globally available
    window.submitPhysiotherapyAssessmentForm = submitPhysiotherapyAssessmentForm;
    window.submitNutritionAssessmentForm = submitNutritionAssessmentForm;
    window.submitGeneralAssessmentForm = submitGeneralAssessmentForm;
    window.getCookie = getCookie;
    
    console.log('✅ Functions registered on window object');
    console.log('   - submitPhysiotherapyAssessmentForm:', typeof window.submitPhysiotherapyAssessmentForm);
    console.log('   - submitNutritionAssessmentForm:', typeof window.submitNutritionAssessmentForm);
    console.log('   - submitGeneralAssessmentForm:', typeof window.submitGeneralAssessmentForm);
    
    // Setup follow-up handlers
    setupFollowUpHandlers();
    
    // Setup modal event listeners
    const physioModal = document.getElementById('physiotherapyAssessmentModal');
    if (physioModal) {
        physioModal.addEventListener('shown.bs.modal', setupFollowUpHandlers);
    }
    
    const nutritionModal = document.getElementById('nutritionAssessmentModal');
    if (nutritionModal) {
        nutritionModal.addEventListener('shown.bs.modal', setupFollowUpHandlers);
    }
    
    const generalModal = document.getElementById('generalAssessmentModal');
    if (generalModal) {
        generalModal.addEventListener('shown.bs.modal', setupFollowUpHandlers);
    }
    
    console.log('🎉 Assessment System Ready!');
}
