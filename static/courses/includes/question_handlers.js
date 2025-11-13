/**
 * Question Handlers Module
 * Contains functions for handling different types of questions in the lesson editor
 */

// Essay Question Handler
function handleEssayQuestion() {
    // Essay questions don't need special handling as they don't have answers
    console.log('Handling essay question');
}

// Single Choice Question Handler
function handleSingleChoiceQuestion() {
    // Handle add new answer for new single choice question
    document.addEventListener('click', function(e) {
        if (e.target.id === 'add-new-single-choice-answer') {
            const container = document.getElementById('new-single-choice-answers-container');
            if (container) {
                const newItem = document.createElement('div');
                newItem.className = 'answer-item mb-2';
                newItem.innerHTML = `
                    <div class="input-group">
                        <input type="text" name="new_answer_text[]" class="form-control" placeholder="Answer text" required>
                        <div class="input-group-text">
                            <input type="radio" name="new_correct_answer" value="0"> Correct
                        </div>
                        <button class="btn btn-outline-danger remove-answer" type="button">Remove</button>
                    </div>
                `;
                container.appendChild(newItem);
            }
        } 
        // Handle add new answer for existing single choice questions
        else if (e.target.id && e.target.id.startsWith('add-single-choice-answer-')) {
            const questionId = e.target.getAttribute('data-question-id');
            const container = document.getElementById(`single-choice-answers-container-${questionId}`);
            if (container) {
                const newItem = document.createElement('div');
                newItem.className = 'answer-item mb-2';
                newItem.innerHTML = `
                    <div class="input-group">
                        <input type="text" name="new_answer_text_${questionId}[]" class="form-control" placeholder="Answer text" required>
                        <div class="input-group-text">
                            <input type="radio" name="new_correct_answer_${questionId}" value="0"> Correct
                        </div>
                        <button class="btn btn-outline-danger remove-answer" type="button">Remove</button>
                    </div>
                `;
                container.appendChild(newItem);
            }
        }
    });
    
    // Handle radio button changes for single choice questions to ensure only one correct answer
    document.addEventListener('change', function(e) {
        // Handle new single choice question
        if (e.target.name === 'new_correct_answer' && e.target.checked) {
            const container = e.target.closest('#new-single-choice-answers-container');
            if (container) {
                const radios = container.querySelectorAll('input[name="new_correct_answer"]');
                radios.forEach(radio => {
                    if (radio !== e.target) {
                        radio.checked = false;
                    }
                });
            }
        }
        // Handle existing single choice questions
        else if (e.target.name && e.target.name.startsWith('new_correct_answer_') && e.target.checked) {
            const questionId = e.target.name.split('_')[3]; // Extract question ID
            const container = e.target.closest(`#single-choice-answers-container-${questionId}`);
            if (container) {
                const radios = container.querySelectorAll(`input[name="new_correct_answer_${questionId}"]`);
                radios.forEach(radio => {
                    if (radio !== e.target) {
                        radio.checked = false;
                    }
                });
            }
        }
        // Handle existing single choice question edit mode
        else if (e.target.name && e.target.name.startsWith('correct_answer') && e.target.checked) {
            const questionId = e.target.name.split('_')[2]; // Extract question ID
            const container = e.target.closest(`#single-choice-answers-container-${questionId}`);
            if (container) {
                const radios = container.querySelectorAll(`input[name="correct_answer"]`);
                radios.forEach(radio => {
                    if (radio !== e.target) {
                        radio.checked = false;
                    }
                });
            }
        }
    });
}

// Multiple Choice Question Handler
function handleMultipleChoiceQuestion() {
    // Handle add new answer for new multiple choice question
    document.addEventListener('click', function(e) {
        if (e.target.id === 'add-new-multiple-choice-answer') {
            const container = document.getElementById('new-multiple-choice-answers-container');
            if (container) {
                const newItem = document.createElement('div');
                newItem.className = 'answer-item mb-2';
                newItem.innerHTML = `
                    <div class="input-group">
                        <input type="text" name="new_answer_text[]" class="form-control" placeholder="Answer text" required>
                        <div class="input-group-text">
                            <input type="checkbox" name="new_answer_correct[]" value="0"> Correct
                        </div>
                        <button class="btn btn-outline-danger remove-answer" type="button">Remove</button>
                    </div>
                `;
                container.appendChild(newItem);
            }
        } 
        // Handle add new answer for existing multiple choice questions
        else if (e.target.id && e.target.id.startsWith('add-multiple-choice-answer-')) {
            const questionId = e.target.getAttribute('data-question-id');
            const container = document.getElementById(`multiple-choice-answers-container-${questionId}`);
            if (container) {
                const newItem = document.createElement('div');
                newItem.className = 'answer-item mb-2';
                newItem.innerHTML = `
                    <div class="input-group">
                        <input type="text" name="new_answer_text_${questionId}[]" class="form-control" placeholder="Answer text" required>
                        <div class="input-group-text">
                            <input type="checkbox" name="new_answer_correct_${questionId}[]"> Correct
                        </div>
                        <button class="btn btn-outline-danger remove-answer" type="button">Remove</button>
                    </div>
                `;
                container.appendChild(newItem);
            }
        }
    });
}

// General question handlers
function handleRemoveAnswer() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-answer')) {
            e.target.closest('.answer-item').remove();
        }
    });
}

// Initialize handlers based on question type
function initializeQuestionHandlersByType(questionType) {
    switch(questionType) {
        case 'essay':
            handleEssayQuestion();
            break;
        case 'single':
            handleSingleChoiceQuestion();
            break;
        case 'multiple':
            handleMultipleChoiceQuestion();
            break;
        default:
            // Initialize all handlers if no specific type
            handleEssayQuestion();
            handleSingleChoiceQuestion();
            handleMultipleChoiceQuestion();
            break;
    }
    handleRemoveAnswer();
}

// Initialize all question handlers
function initializeQuestionHandlers() {
    // Check if we're in a modal context
    const modal = document.querySelector('.modal.show');
    if (modal && modal.hasAttribute('data-question-type')) {
        const questionType = modal.getAttribute('data-question-type');
        initializeQuestionHandlersByType(questionType);
    } else {
        // Initialize all handlers
        initializeQuestionHandlersByType();
    }
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        handleEssayQuestion,
        handleSingleChoiceQuestion,
        handleMultipleChoiceQuestion,
        handleRemoveAnswer,
        initializeQuestionHandlers
    };
}