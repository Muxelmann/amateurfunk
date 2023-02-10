function answer(rootElement, url, level, topic, id) {
    answers = rootElement.getElementsByClassName('answer');

    let xhr = new XMLHttpRequest();
    xhr.open('POST', url);

    xhr.setRequestHeader('Accept', 'application/json');
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onload = () => {
        response = JSON.parse(xhr.responseText);
        if (response['received']) {
            rootElement.removeAttribute('onclick');
            for (let i = 0; i < answers.length; i++) {
                answers[i].classList.add(answers[i].hasAttribute('correct') ? 'correct' : 'wrong');
            }
        } else {
            console.log("Something went wrong!");
        }
    };
    
    correct = false;
    for (let i = 0; i < answers.length; i++) {
        if (answers[i].matches(':hover')) {
            correct = answers[i].hasAttribute('correct');
            break;
        }
    }
    let data = {
        'level': level,
        'topic': topic,
        'id': id,
        'correct': correct
    };
    xhr.send(JSON.stringify(data));
}