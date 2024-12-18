document.addEventListener("DOMContentLoaded", () => {
    const csrf = Cookies.get('csrftoken');
    document.body.style.backgroundColor =  document.querySelector("#bg-color").innerHTML;
    document.body.style.color =  document.querySelector("#text-color").innerHTML;
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
    document.querySelector("#delete-form").addEventListener("submit", e => {
        e.preventDefault();
        if(window.confirm("Вы уверены? Это действие нельзя отменить.")){
            fetch('delete', {
                method: "DELETE",
                headers: {'X-CSRFToken': csrf}
            })
            .then(() => window.location = "/")
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
                "allow_view_score": document.querySelector("#allow_view_score").checked
            })
        })
        document.querySelector("#setting").style.display = "none";
        if(!document.querySelector("#collect_email").checked){
            if(document.querySelector(".collect-email")) document.querySelector(".collect-email").parentNode.removeChild(document.querySelector(".collect-email"))
        }else{
            if(!document.querySelector(".collect-email")){
                let collect_email = document.createElement("div");
                collect_email.classList.add("collect-email")
                collect_email.innerHTML = `<h3 class="question-title">Email адрес <span class="require-star">*</span></h3>
                <input type="text" autoComplete="off" aria-label="Email адрес" disabled dir = "auto" class="require-email-edit"
                placeholder = "Email адрес" />
                <p class="collect-email-desc">Эта форма собирает адреса электронных почт.</p>`
                document.querySelector("#form-head").appendChild(collect_email)
            }
        }
        if(document.querySelector("#is_quiz").checked){
            if(!document.querySelector("#add-score")){
                let is_quiz = document.createElement('a')
                is_quiz.setAttribute("href", "score");
                is_quiz.setAttribute("id", "add-score");
                is_quiz.innerHTML = `<img src = "/static/Icon/score-form.png" id="add-score" class = "form-option-icon" title = "Добавить оценку" alt = "Score icon" />`;
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
    document.querySelectorAll(".textarea-adjust").forEach(tx => {
        tx.style.height = "auto";
        tx.style.height = (10 + tx.scrollHeight)+"px";
        tx.addEventListener('input', e => {
            tx.style.height = "auto";
            tx.style.height = (10 + tx.scrollHeight)+"px";
        })
    })
    if(document.querySelector("#delete-responses")){
        document.querySelector("#delete-responses").addEventListener("click", () => {
            if(window.confirm("Вы уверены? Это действие нельзя отменить.")){
                fetch('responses/delete', {
                    method: "DELETE",
                    headers: {'X-CSRFToken': csrf}
                })
                .then(() => {
                    let ele = document.createElement("div");
                    ele.classList.add('margin-top-bottom');
                    ele.classList.add('box');
                    ele.classList.add('question-box');
                    ele.innerHTML = '<h1 class="response-title">0 ответов</h1>';
                    document.querySelector("#responses").parentNode.replaceChild(ele, document.querySelector("#responses"))
                })
            }
        })
    }
})
document.addEventListener('DOMContentLoaded', function() {
    const saveSettingButton = document.querySelector('.btn-save-setting');

    function saveScrollPosition() {
        const scrollPosition = document.querySelector('.container').scrollTop;
        localStorage.setItem('scrollPosition', scrollPosition);
    }

    function restoreScrollPosition() {
        const scrollPosition = localStorage.getItem('scrollPosition');
        if (scrollPosition !== null) {
            document.querySelector('.container').scrollTop = scrollPosition;
            localStorage.removeItem('scrollPosition');
        }
    }

    restoreScrollPosition();

    if (saveSettingButton) {
        saveSettingButton.addEventListener('click', function() {
            saveScrollPosition();
            setTimeout(function() {
                location.reload();
            }, 100); 
        });
    }
});