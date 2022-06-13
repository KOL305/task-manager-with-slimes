var tasks = [];
var cardID = 0;
//localStorage{} --> "tasks" --> tasks[] --> {cardId: task}

//Bugs:
    //Delete Function Buggy
document.getElementById("page").addEventListener("load", loadData());

function addTask() {
    var task = {}
    task["title"] = document.getElementById("title").value;
    task["description"] = document.getElementById("description").value;
    task["duetime"] = document.getElementById("duetime").value;
    task["difficulty"] = document.getElementById("difficultyBar").value;
    createCard(task,cardID);
    tasks.push(task);
    localStorage.setItem("tasks", JSON.stringify(tasks));
    cardID++;

    alert("Task Updated");   
}

function createCard(task, cardID) {
    var taskDiv = document.createElement("div"); // Creates container for task
    taskDiv.classList.add("card"); // div styling
    taskDiv.classList.add("text-left");
    taskDiv.style["border"] = "2px solid black"; // sets border color based on difficulty
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
    // taskDiv.classList.add(task["font"]); -- change font?
    TaskTitle.textContent = task["title"];
    

    var TaskTitleColTwo = document.createElement("div"); // creates div to contain delete/complete
    TaskTitleColTwo.classList.add("col-1");

    var taskDeleteButton = document.createElement("button"); // delete task button
    taskDeleteButton.classList.add("btn");
    taskDeleteButton.classList.add("btn-danger");
    taskDeleteButton.setAttribute("onclick",`deleteCard(${cardID})`)

    var taskDeleteIcon = document.createElement("i");
    taskDeleteIcon.classList.add("fa");
    taskDeleteIcon.classList.add("fa-trash");

    var taskLink = document.createElement("a");
    taskLink.classList.add("card-link");
    taskLink.href = task["link"];
    taskLink.contentEditable = "false";
    taskLink.textContent = task["link"];
    taskLink.setAttribute("id",`link${cardID}`)

    var taskEditLinkButton = document.createElement("button");
    taskEditLinkButton.classList.add("btn");
    taskEditLinkButton.classList.add("bg-transparent");
    taskEditLinkButton.classList.add("bg-outline-light");
    taskEditLinkButton.classList.add("mx-1");
    taskEditLinkButton.setAttribute("onclick",`editLink('link${cardID}')`)

    var taskEditLinkIcon = document.createElement("i");
    taskEditLinkIcon.classList.add("fa");
    taskEditLinkIcon.classList.add("fa-pencil");

    var taskDescriptionDiv= document.createElement("div");
    taskDescriptionDiv.classList.add("card-text");
    taskDiv.classList.add(task["font"]);
    taskDescriptionDiv.style["color"] = task["fg-color"];

    var taskDescription = document.createElement("p");
    taskDescription.textContent = task["description"];


    TaskTitleColOne.append(TaskTitle);

    taskDeleteButton.append(taskDeleteIcon);
    TaskTitleColTwo.append(taskDeleteButton);

    TaskTitleRow.append(TaskTitleColOne);
    TaskTitleRow.append(TaskTitleColTwo);

    taskEditLinkButton.append(taskEditLinkIcon);

    taskDescriptionDiv.append(taskDescription);

    taskBodyDiv.append(TaskTitleRow);
    taskBodyDiv.append(taskLink);
    taskBodyDiv.append(taskEditLinkButton);
    taskBodyDiv.append(taskDescriptionDiv);

    taskDiv.append(taskBodyDiv);


    var tasksList = document.getElementById("tasksList");
    tasksList.prepend(taskDiv);
}

function deleteCard(deleteID) {
    var deletedTask = document.getElementById(deleteID);
    deletedTask.remove();
    tasks.splice(deleteID,1);
    console.log(tasks);
    cardID--;
    console.log(cardID);
    localStorage.setItem("Tasks",JSON.stringify(tasks));
}

function editLink(linkID) {
    var link = document.getElementById(linkID);
    let cardID = parseInt(linkID.substring(4,linkID.length));
    console.log(link.textContent)
    var newLink = document.getElementById(linkID).textContent;
    link.setAttribute("href", newLink);
    tasks[cardID]["link"] = newLink;
    localStorage.setItem("Tasks",JSON.stringify(tasks));
    link.contentEditable = (link.contentEditable == "false")? "true":"false";
}

function loadData() {
    console.log("Hi");
    try {
        console.log("There is Data");
        
        tasks = JSON.parse(localStorage.getItem("Tasks"))
        for (let i=0; i<tasks.length; i++) {
            createCard(tasks[i],i);
            cardID++
        }
    }
    catch (e) {
        localStorage.setItem("Tasks",JSON.stringify(tasks));
        console.log("No Data");
    }
}