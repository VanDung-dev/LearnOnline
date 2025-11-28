function validateRequiredCourseForm(event) {
    event.preventDefault();
    const form = event.target.form;
    const price = parseFloat(form.querySelector('#id_price').value) || 0;
    const certificatePrice = parseFloat(form.querySelector('#id_certificate_price').value) || 0;
    const category = form.querySelector('#id_category').value;
    
    // Check if category is selected
    if (!category) {
        alert("Category is required.");
        return;
    }
    
    // Check if both prices are zero
    if (price === 0 && certificatePrice === 0) {
        alert("Either Course Price or Certificate Price must be greater than 0.");
        return;
    }
    
    // If all validations pass, submit the form
    form.submit();
}
