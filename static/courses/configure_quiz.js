document.addEventListener('DOMContentLoaded', function() {
    // Add new answer in add question modal
    document.getElementById('add-new-answer').addEventListener('click', function() {
        const container = document.getElementById('new-answers-container');
        const newItem = document.createElement('div');
        newItem.className = 'answer-item mb-2';
        newItem.innerHTML = `
            <div class="input-group">
                <input type="text" name="new_answer_text[]" class="form-control" placeholder="Answer text">
                <div class="input-group-text">
                    <input type="checkbox" name="new_answer_correct[]"> Correct
                </div>
                <button class="btn btn-outline-danger remove-answer" type="button">Remove</button>
            </div>
        `;
        container.appendChild(newItem);
    });
    
    // Add new answer in edit question modals
    document.querySelectorAll('.add-answer').forEach(button => {
        button.addEventListener('click', function() {
            const questionId = this.getAttribute('data-question-id');
            const container = document.getElementById(`answers-container-${questionId}`);
            const newItem = document.createElement('div');
            newItem.className = 'answer-item mb-2';
            newItem.innerHTML = `
                <div class="input-group">
                    <input type="text" name="new_answer_text_${questionId}[]" class="form-control" placeholder="Answer text">
                    <div class="input-group-text">
                        <input type="checkbox" name="new_answer_correct_${questionId}[]"> Correct
                    </div>
                    <button class="btn btn-outline-danger remove-answer" type="button">Remove</button>
                </div>
            `;
            container.appendChild(newItem);
        });
    });
    
    // Remove answer functionality
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-answer')) {
            e.target.closest('.answer-item').remove();
        }
    });
});