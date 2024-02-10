
//-->Menu
var sideMenu = document.querySelector('#side_menu')
var ul = document.querySelector('#side_menu_ul')

var ul_visible = true

function hide_span(){
    if (ul_visible == true){
        ul.style.transition = '0s'
        ul.style.visibility = 'hidden'
        sideMenu.style.width = '0%'
        ul_visible = false
    }else{
        ul.style.visibility = 'visible'
        sideMenu.style.width = '60px'
        ul.style.transition = '0.5s ease'
        ul_visible = true
    }
}

//-->Index
function priorityColor() {
    const taskRows = document.querySelectorAll('.table_task_tr');

    taskRows.forEach(row => {
        const priority = row.querySelector('.td_priority');

        // Use textContent para obter o texto visível dentro da célula
        if (priority.textContent.trim() === '1') {
            priority.style.backgroundColor = 'yellow';
        }else if(priority.textContent.trim() === '2'){
            priority.style.backgroundColor = 'orange';
        }else if(priority.textContent.trim() === '3'){
            priority.style.backgroundColor = 'red';
        }
    });
}

//remaining time
function updateRemainingTime() {
    const taskRows = document.querySelectorAll('.table_task_tr');

    taskRows.forEach(row => {
        const startTimeText = row.querySelector('.table_datetime_start').textContent;
        const endTimeText = row.querySelector('.table_datetime_ending').textContent;

        // Formatando as datas no formato ISO 8601 (AAAA-MM-DDTHH:MM:SS)
        const startTimeISO = startTimeText.replace(/(\d{2})\/(\d{2})\/(\d{2}) (\d{2}):(\d{2})/, '20$3-$2-$1T$4:$5:00');
        const endTimeISO = endTimeText.replace(/(\d{2})\/(\d{2})\/(\d{2}) (\d{2}):(\d{2})/, '20$3-$2-$1T$4:$5:00');

        // Convertendo as datas formatadas para o formato aceito pelo JavaScript
        const startTime = Date.parse(startTimeISO);
        const endTime = Date.parse(endTimeISO);
        const now = Date.now();

        const remainingTimeCell = row.querySelector('.remaining_time_td');

        if (isNaN(startTime) || isNaN(endTime)) {
            remainingTimeCell.textContent = " ";
        } else if (now < startTime) {
            remainingTimeCell.textContent = "não começou";
        } else if (now > endTime) {
            remainingTimeCell.textContent = "acabou";
        } else {
            const timeRemaining = endTime - now;
            const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));

            remainingTimeCell.textContent = days + "d " + hours + "h " + minutes + "m ";
        }
    });
}

window.addEventListener('load', function() {
    // Quando o evento 'load' ocorrer, chame a função priorityColor
    priorityColor();
});

updateRemainingTime();

// Atualizar o tempo restante a cada segundo
setInterval(updateRemainingTime, 1000);