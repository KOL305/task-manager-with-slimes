document.getElementById("page").addEventListener("load", loadData());
cardID = 0;

function loadData() {
    var tasks = JSON.parse('{{tasks|tojson}}');
    tasks.forEach(function (task){
        createCard(task, cardID);
        cardID++;
    })
}

function createCard(task, cardID) {
    var taskDiv = document.createElement("div"); // Creates container for task
    taskDiv.classList.add("card"); // div styling
    taskDiv.style['background-color'] = '#FFEEB0';
    taskDiv.style["border"] = "2px solid"; // sets border color based on difficulty
    if (task["difficultyBar"] == 0) {
    taskDiv.style["border-color"] = 'green';
    }
    else if (task["difficultyBar"] == 1) {
        taskDiv.style["border-color"] = 'lightgreen';
    }
    else if (task["difficultyBar"] == 2) {
    taskDiv.style["border-color"] = 'yellow';
    }
    else if (task["difficultyBar"] == 3) {
        taskDiv.style["border-color"] = 'orange';
    }
    else if (task["difficultyBar"] == 4) {
        taskDiv.style["border-color"] = 'red';
    }
    taskDiv.setAttribute("id",cardID); // sets div id

    var taskBodyDiv = document.createElement("div"); // creates div for task content
    taskBodyDiv.classList.add("card-body"); // div styling

    var TaskTitleRow = document.createElement("div");
    TaskTitleRow.classList.add("row");

    var TaskTitleColOne = document.createElement("div");
    TaskTitleColOne.classList.add("col-11");

    var TaskTitle = document.createElement("h1");
    TaskTitle.classList.add("card-title");
    TaskTitle.textContent = task["title"];
}