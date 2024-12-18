document.addEventListener("DOMContentLoaded", () => {
    const csrf = Cookies.get('csrftoken');
    document.body.style.backgroundColor =  document.querySelector("#bg-color").innerHTML;
    document.body.style.color =  document.querySelector("#text-color").innerHTML;
    document.querySelectorAll(".txt-clr").forEach(element => {
        element.style.color = document.querySelector("#text-color").innerHTML;
    })
    document.querySelectorAll(".input-form-title").forEach(title => {
        title.addEventListener("input", function(){
            fetch(`edit_title`, {
                method: "POST",
                headers: {'X-CSRFToken': csrf},
                body: JSON.stringify({
                    "title": this.value
                })

            })
            document.title = `${this.value} - Google Forms CLONE`
            document.querySelectorAll(".input-form-title").forEach(ele => {
                ele.value = this.value;
            })
        })
    })
    document.querySelector("#input-form-description").addEventListener("input", function(){
        fetch('edit_description', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({
                "description": this.value
            })
        })
    })
    document.querySelectorAll(".textarea-adjust").forEach(tx => {
        tx.style.height = "auto";
        tx.style.height = (10 + tx.scrollHeight)+"px";
        tx.addEventListener('input', e => {
            tx.style.height = "auto";
            tx.style.height = (10 + tx.scrollHeight)+"px";
        })
    })
    document.querySelector("#customize-theme-btn").addEventListener('click', () => {
        document.querySelector("#customize-theme").style.display = "block";
        document.querySelector("#close-customize-theme").addEventListener('click', () => {
            document.querySelector("#customize-theme").style.display = "none";
        })
        window.onclick = e => {
            if(e.target == document.querySelector("#customize-theme")) document.querySelector("#customize-theme").style.display = "none";
        }
    })
    document.querySelector("#input-bg-color").addEventListener("input", function(){
        document.body.style.backgroundColor = this.value;
        fetch('edit_background_color', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({
                "bgColor": this.value
            })
        })
    })
    document.querySelector("#input-text-color").addEventListener("input", function(){
        document.querySelectorAll(".txt-clr").forEach(element => {
            element.style.color = this.value;
        })
        fetch('edit_text_color', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({
                "textColor": this.value
            })
        })
    })
    document.querySelectorAll(".open-setting").forEach(ele => {
        ele.addEventListener('click', () => {
            document.querySelector("#setting").style.display = "block";
        })
        document.querySelector("#close-setting").addEventListener('click', () => {
            document.querySelector("#setting").style.display = "none";
        })
        window.onclick = e => {
            if(e.target == document.querySelector("#setting")) document.querySelector("#setting").style.display = "none";
        }
    })
    document.querySelectorAll("#send-form-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelector("#send-form").style.display = "block";
        })
        document.querySelector("#close-send-form").addEventListener("click", () => {
            document.querySelector("#send-form").style.display = "none";
        })
        window.onclick = e => {
            if(e.target == document.querySelector("#send-form")) document.querySelector("#send-form").style.display = "none";
        }
    })
    document.querySelectorAll("[copy-btn]").forEach(btn => {
        btn.addEventListener("click", () => {
            var url = document.getElementById("copy-url");
            navigator.clipboard.writeText(url.value).then(() => {
                document.querySelector("#send-form").style.display = "none";
            }).catch(err => {
                console.error('Failed to copy: ', err);
            });
        });
    });
    document.querySelectorAll("[copy-code-btn]").forEach(btn => {
        btn.addEventListener("click", () => {
            var url = document.getElementById("copy-code-url");
            navigator.clipboard.writeText(url.value).then(() => {
                document.querySelector("#send-form").style.display = "none";
            }).catch(err => {
                console.error('Failed to copy: ', err);
            });
        });
    });
    document.querySelector("#setting-form").addEventListener("submit", e => {
        e.preventDefault();
        fetch('edit_setting', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({
                "collect_email": document.querySelector("#collect_email").checked,
                "is_quiz": document.querySelector("#is_quiz").checked,
                "authenticated_responder": document.querySelector("#authenticated_responder").checked,
                "confirmation_message": document.querySelector("#comfirmation_message").value,
                "edit_after_submit": document.querySelector("#edit_after_submit").checked,
                "allow_view_score": document.querySelector("#allow_view_score").checked,
            })
        })
        document.querySelector("#setting").style.display = "none";
        if(!document.querySelector("#collect_email").checked){
            if(document.querySelector(".collect-email")) document.querySelector(".collect-email").parentNode.removeChild(document.querySelector(".collect-email"))
        }else{
            if(!document.querySelector(".collect-email")){
                let collect_email = document.createElement("div");
                collect_email.classList.add("collect-email")
                collect_email.innerHTML = `<h3 class="question-title">Email address <span class="require-star">*</span></h3>
                <input type="text" autoComplete="off" aria-label="Valid email address" disabled dir = "auto" class="require-email-edit"
                placeholder = "Valid email address" />
                <p class="collect-email-desc">This form is collecting email addresses. <span class="open-setting">Change settings</span></p>`
                document.querySelector("#form-head").appendChild(collect_email)
            }
        }
        if(document.querySelector("#is_quiz").checked){
            if(!document.querySelector("#add-score")){
                let is_quiz = document.createElement('a')
                is_quiz.setAttribute("href", "score");
                is_quiz.setAttribute("id", "add-score");
                document.querySelector(".question-options").appendChild(is_quiz)
            }
            if(!document.querySelector(".score")){
                let quiz_nav = document.createElement("span");
                quiz_nav.classList.add("col-4");
                quiz_nav.classList.add("navigation");
                quiz_nav.classList.add('score');
                quiz_nav.innerHTML =   `<a href = "score" class="link">Оценка</a>`;
                [...document.querySelector(".form-navigation").children].forEach(element => {
                    element.classList.remove("col-6")
                    element.classList.add('col-4')
                })
                document.querySelector(".form-navigation").insertBefore(quiz_nav, document.querySelector(".form-navigation").childNodes[2])
            }
        }else{
            if(document.querySelector("#add-score")) document.querySelector("#add-score").parentNode.removeChild(document.querySelector("#add-score"))
            if(document.querySelector(".score")){
                [...document.querySelector(".form-navigation").children].forEach(element => {
                    element.classList.remove("col-4")
                    element.classList.add('col-6')
                })
                document.querySelector(".score").parentNode.removeChild(document.querySelector(".score"))
            }
        }
    })
    document.querySelector("#delete-form").addEventListener("submit", e => {
        e.preventDefault();
        if(window.confirm("Are you sure? This action CANNOT be undone.")){
            fetch('delete', {
                method: "DELETE",
                headers: {'X-CSRFToken': csrf}
            })
            .then(() => window.location = "/")
        }
    })
    const editQuestion = () => {
        document.querySelectorAll(".input-question").forEach(question => {
            question.addEventListener('input', function(){
                let question_type;
                let required;
                let is_list;
                let is_skip;
                document.querySelectorAll(".input-question-type").forEach(qp => {
                    if(qp.dataset.id === this.dataset.id) question_type = qp.value
                })
                document.querySelectorAll('.required-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) required = rc.checked;
                })
                document.querySelectorAll('.islist-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_list = rc.checked;
                })
                document.querySelectorAll('.isskip-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_skip = rc.checked;
                })
                fetch('edit_question', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        id: this.dataset.id,
                        question: this.value,
                        question_type: question_type,
                        required: required,
                        is_list: is_list,
                        is_skip: is_skip
                    })
                })
            })
        })
    }
    editQuestion();
    
    const editRequire = () => {
        document.querySelectorAll(".required-checkbox").forEach(checkbox => {
            checkbox.addEventListener('input', function(){
                let question;
                let question_type;
                let is_list;
                let is_skip;
                document.querySelectorAll(".input-question-type").forEach(qp => {
                    if(qp.dataset.id === this.dataset.id) question_type = qp.value
                })
                document.querySelectorAll('.input-question').forEach(q => {
                    if(q.dataset.id === this.dataset.id) question = q.value
                })
                document.querySelectorAll('.islist-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_list = rc.checked;
                })
                document.querySelectorAll('.isskip-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_skip = rc.checked;
                })
                fetch('edit_question', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        id: this.dataset.id,
                        question: question,
                        question_type: question_type,
                        required: this.checked,
                        is_list: is_list,
                        is_skip: is_skip
                    })
                })
            })
        })
    }
    editRequire()
    const editList = () => {
        document.querySelectorAll(".islist-checkbox").forEach(checkbox => {
            checkbox.addEventListener('input', function(){
                let question;
                let question_type;
                let required;
                let is_skip;
                document.querySelectorAll(".input-question-type").forEach(qp => {
                    if(qp.dataset.id === this.dataset.id) question_type = qp.value;
                });
                document.querySelectorAll('.input-question').forEach(q => {
                    if(q.dataset.id === this.dataset.id) question = q.value;
                });
                document.querySelectorAll('.required-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) required = rc.checked;
                })
                document.querySelectorAll('.isskip-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_skip = rc.checked;
                })
                fetch('edit_question', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        id: this.dataset.id,
                        question: question,
                        question_type: question_type,
                        is_list: this.checked,
                        required: required,
                        is_skip: is_skip
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Edit question response:', data);
                })
                .catch(error => {
                    console.error('Error editing question:', error);
                });
            });
        });
    };
    editList();
    const editSkip = () => {
        document.querySelectorAll(".isskip-checkbox").forEach(checkbox => {
            checkbox.addEventListener('input', function(){
                let question;
                let question_type;
                let required;
                let is_list;
                document.querySelectorAll(".input-question-type").forEach(qp => {
                    if(qp.dataset.id === this.dataset.id) question_type = qp.value;
                });
                document.querySelectorAll('.input-question').forEach(q => {
                    if(q.dataset.id === this.dataset.id) question = q.value;
                });
                document.querySelectorAll('.required-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) required = rc.checked;
                })
                document.querySelectorAll('.islist-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_list = rc.checked;
                })
                fetch('edit_question', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        id: this.dataset.id,
                        question: question,
                        question_type: question_type,
                        is_skip: this.checked,
                        required: required,
                        is_list: is_list
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Edit question response:', data);
                })
                .catch(error => {
                    console.error('Error editing question:', error);
                });
            });
        });
    };
    editSkip();
    const editChoice = () => {
        document.querySelectorAll(".edit-choice").forEach(choice => {
            choice.addEventListener("input", function(){
                fetch('edit_choice', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        "id": this.dataset.id,
                        "choice": this.value
                    })
                })
            })
        })
    }
    editChoice()
    const removeOption = () => {
        document.querySelectorAll(".remove-option").forEach(ele => {
            ele.addEventListener("click",function(){
                fetch('remove_choice', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        "id": this.dataset.id
                    })
                })
                .then(() => {
                    this.parentNode.parentNode.removeChild(this.parentNode)
                })
            })
        })
    }
    removeOption()
    const addOption = () => {
        document.querySelectorAll(".add-option").forEach(question =>{
            question.addEventListener("click", function(){
                fetch('add_choice', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        "question": this.dataset.question
                    })
                })
                .then(response => response.json())
                .then(result => {
                    let element = document.createElement("div");
                    element.classList.add('choice');
                    if(this.dataset.type === "multiple choice"){
                        element.innerHTML = `<input type="radio" id="${result["id"]}" disabled>
                        <label for="${result["id"]}">
                            <input type="text" value="${result["choice"]}" class="edit-choice" data-id="${result["id"]}">
                        </label>
                        <span class="remove-option" title = "Remove" data-id="${result["id"]}">&times;</span>`;
                    }else if(this.dataset.type === "checkbox"){
                        element.innerHTML = `<input type="checkbox" id="${result["id"]}" disabled>
                        <label for="${result["id"]}">
                            <input type="text" value="${result["choice"]}" class="edit-choice" data-id="${result["id"]}">
                        </label>
                        <span class="remove-option" title = "Remove" data-id="${result["id"]}">&times;</span>`;
                    }
                    document.querySelectorAll(".choices").forEach(choices => {
                        if(choices.dataset.id === this.dataset.question){
                            choices.insertBefore(element, choices.childNodes[choices.childNodes.length -2]);
                            editChoice()
                            removeOption()
                        }
                    });
                })
            })
        })
    }
    addOption()
    const deleteQuestion = () => {
        document.querySelectorAll(".delete-question").forEach(question => {
            question.addEventListener("click", function() {
                const questionId = this.dataset.id;  // Получаем ID вопроса
                fetch(`delete_question/${questionId}`, {
                    method: "DELETE",
                    headers: {
                        'X-CSRFToken': csrf,
                    }
                })
                .then(response => {
                    if (response.ok) {  // Проверяем успешность ответа сервера
                        // Ищем вопрос по его data-id и удаляем
                        const questionElement = document.querySelector(`.question[data-id='${questionId}']`);
                        if (questionElement) {
                            questionElement.remove();
                        }
                    } else {
                        console.error('Ошибка удаления вопроса');
                    }
                })
                .catch(error => {
                    console.error('Ошибка зпроса:', error);
                });
            });
        });
    };
    
    deleteQuestion();
    const changeType = () => {
        document.querySelectorAll(".input-question-type").forEach(ele => {
            ele.addEventListener('input', function(){
                const scrollPosition = document.querySelector('.container').scrollTop;
                localStorage.setItem('scrollPosition', scrollPosition);

                let required;
                let question;
                let is_list;
                let is_skip;
                let max_value = 1;

                document.querySelectorAll('.required-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) required = rc.checked;
                });
                document.querySelectorAll('.input-question').forEach(q => {
                    if(q.dataset.id === this.dataset.id) question = q.value;
                });
                document.querySelectorAll('.islist-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_list = rc.checked;
                })
                document.querySelectorAll('.isskip-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_skip = rc.checked;
                })
                fetch('edit_question', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        id: this.dataset.id,
                        question: question,
                        question_type: this.value,
                        required: required,
                        is_list: is_list,
                        is_skip: is_skip,
                        is_negative: false
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(() => {
                    if (this.value === 'range slider') {
                        return fetch(`/update_max_value/${this.dataset.id}/`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrf,
                            },
                            body: JSON.stringify({ max_value: max_value })
                        });
                    }
                })
                .then(response => {
                    if (response && !response.ok) {
                        throw new Error('Error updating max value');
                    }
                    location.reload();
                })
                .catch(error => {
                    console.error('Error:', error);
                    localStorage.removeItem('scrollPosition');
                    alert('Произошла ошибка при изменении типа вопроса. Пожалуйста, попробуйте еще раз.');
                });
            });
        });
    };
    changeType();
    document.querySelector("#add-question").addEventListener("click", () => {
        fetch('add_question', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(result => {
            let ele = document.createElement('div')
            ele.classList.add('margin-top-bottom');
            ele.classList.add('box');
            ele.classList.add('question-box');
            ele.classList.add('question');
            ele.setAttribute("data-id", result["question"].id)
            
            fetch(`/update_max_value/${result["question"].id}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf,
                },
                body: JSON.stringify({ max_value: 1 })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Initial max value set successfully:', data);
            })
            .catch(error => {
                console.error('Error setting initial max value:', error);
            });

            ele.innerHTML = `
            <div class="drag-handle">⋮⋮</div>
            <input type="text" data-id="${result["question"].id}" class="question-title edit-on-click input-question" value="${result["question"].question}">
            <select class="question-type-select input-question-type" data-id="${result["question"].id}" data-origin_type = "${result["question"].question_type}">
                <option value="title">Заголовок</option>
                <option value="short">Строка</option>
                <option value="paragraph">Абзац</option>
                <option value="multiple choice" selected>Один вариант</option>
                <option value="checkbox">Мультивыбор</option>
                <option value="range slider">Ползунок</option>
            </select>
            ${result["question"].question_type !== "title" ? 
                `<div class="choices" data-id="${result["question"].id}">
                    <div class="choice">
                        <input type="radio" id="${result["choices"].id}" disabled>
                        <label for="${result["choices"].id}">
                            <input type="text" value="${result["choices"].choice}" class="edit-choice" data-id="${result["choices"].id}">
                        </label>
                        <span class="remove-option" title="Удалить" data-id="${result["choices"].id}">&times;</span>
                    </div>
                    <div class="choice">
                        <label for="add-choice" class="add-option" id="add-option" data-question="${result["question"].id}" 
                        data-type="${result["question"].question_type}">Добавить вариант</label>
                    </div>
                </div>`
                : ''}
            <div class="choice-option">
                <label class="toggle-switch" for="required-${result["question"].id}">
                    <input type="checkbox" class="required-checkbox" id="required-${result["question"].id}" data-id="${result["question"].id}">
                    <span class="toggle-slider"></span>
                </label>
                <label for="required-${result["question"].id}" class="required">Обязателен*</label>
                <label class="toggle-switch" for="isskip-${result["question"].id}">
                    <input type="checkbox" class="isskip-checkbox" id="isskip-${result["question"].id}" data-id="${result["question"].id}">
                    <span class="toggle-slider"></span>
                </label>
                <label for="isskip-${result["question"].id}" class="required">Необязателен для статистики</label>
                <label class="toggle-switch" for="list-${result["question"].id}">
                    <input type="checkbox" class="is_list-checkbox" id="list-${result["question"].id}" data-id="${result["question"].id}">
                    <span class="toggle-slider"></span>
                </label>
                <label for="list-${result["question"].id}" class="is_list">Список</label>
                <div class="float-right">
                    <a class="question-option-icon delete-question" title="Удалить поле" data-id="${result["question"].id}">
                        <i class="bi bi-trash-fill delete-question delete-question-icon"></i>
                    </a>
                </div>
            </div>`;
            
            document.querySelector(".container").appendChild(ele);
            initMaxValueHandlers();

            const newMaxValueInput = ele.querySelector('input[id="input-max-value"]');
            if (newMaxValueInput) {
                newMaxValueInput.addEventListener('input', function() {
                    const questionId = this.getAttribute('data-id');
                    const newValue = this.value;

                    fetch(`/update_max_value/${questionId}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrf,
                        },
                        body: JSON.stringify({ max_value: newValue }),
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log('Max value updated successfully:', data);
                    })
                    .catch(error => {
                        console.error('Error updating max value:', error);
                    });
                });
            }

            editChoice();
            removeOption();
            changeType();
            editQuestion();
            editRequire();
            editList();
            editSkip();
            addOption();
            deleteQuestion();
        })
    })

    const initMaxValueHandlers = () => {
        document.querySelectorAll('input[id="input-max-value"]').forEach(input => {
            input.addEventListener('change', function() {
                const questionId = this.getAttribute('data-id');
                const newValue = parseInt(this.value);
                
                if (isNaN(newValue) || newValue <= 0) {
                    console.error('Invalid max value');
                    return;
                }

                const slider = this.closest('.answers').querySelector('.slider');
                
                fetch(`/update_max_value/${questionId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrf,
                    },
                    body: JSON.stringify({ max_value: newValue })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Max value updated successfully:', data);
                    if (slider) {
                        slider.max = newValue;
                        slider.value = Math.min(slider.value, newValue);
                    }
                })
                .catch(error => {
                    console.error('Error updating max value:', error);
                    this.value = this.defaultValue;
                });
            });
        });
    };
    initMaxValueHandlers();

    document.addEventListener('DOMContentLoaded', function() {
        const savedScrollPosition = localStorage.getItem('scrollPosition');
        if (savedScrollPosition) {
            document.querySelector('.container').scrollTop = parseInt(savedScrollPosition);
            localStorage.removeItem('scrollPosition');
        }
    });

    const editNegative = () => {
        document.querySelectorAll(".isnegative-checkbox").forEach(checkbox => {
            checkbox.addEventListener('input', function(){
                let question;
                let question_type;
                let required;
                let is_list;
                let is_skip;
                
                document.querySelectorAll(".input-question-type").forEach(qp => {
                    if(qp.dataset.id === this.dataset.id) question_type = qp.value;
                });
                document.querySelectorAll('.input-question').forEach(q => {
                    if(q.dataset.id === this.dataset.id) question = q.value;
                });
                document.querySelectorAll('.required-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) required = rc.checked;
                });
                document.querySelectorAll('.isskip-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_skip = rc.checked;
                });
                
                fetch('edit_question', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        id: this.dataset.id,
                        question: question,
                        question_type: question_type,
                        is_negative: this.checked,
                        required: required,
                        is_skip: is_skip,
                        is_list: false
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .catch(error => {
                    console.error('Error editing question:', error);
                });
            });
        });
    };
    
    editNegative();
})