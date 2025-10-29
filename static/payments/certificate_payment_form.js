document.addEventListener('DOMContentLoaded', function() {
    // Add visual feedback when a card type is selected
    document.querySelectorAll('.card-option').forEach(option => {
        option.addEventListener('click', function() {
            // Remove selected class from all card options
            document.querySelectorAll('.card-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            
            // Add selected class to clicked option
            this.classList.add('selected');
            
            // Set the hidden input value
            document.getElementById('card_type').value = this.getAttribute('data-card-type');
        });
    });

    document.getElementById('certificate-payment-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Check if a card type has been selected
        const cardType = document.getElementById('card_type').value;
        if (!cardType) {
            alert('Please select a card type');
            return;
        }
        
        const payButton = document.getElementById('pay-button');
        const originalText = payButton.innerHTML;
        payButton.disabled = true;
        payButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
        
        const formData = new FormData(this);
        
        fetch(processCertificatePaymentUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                alert('Payment failed: ' + data.error);
                payButton.disabled = false;
                payButton.innerHTML = originalText;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during payment processing.');
            payButton.disabled = false;
            payButton.innerHTML = originalText;
        });
    });
});