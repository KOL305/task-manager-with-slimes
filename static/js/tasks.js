var notes = [];
var cardID = 0;
//localStorage{} --> "Notes" --> notes[] --> {cardId: note}

//Bugs:
    //Delete Function Buggy
document.getElementById("page").addEventListener("load", loadData());

function addNote() {
    var note = {}
    note["heading"] = document.getElementById("heading").value;
    note["link"] = document.getElementById("link").value;
    note["description"] = document.getElementById("description").value;
    note["font"] = document.getElementById("font").value;
    note["bg-color"] = document.getElementById("bg-color").value;
    note["fg-color"] = document.getElementById("fg-color").value;
    createCard(note,cardID);
    notes.push(note);
    localStorage.setItem("Notes", JSON.stringify(notes));
    cardID++;

    alert("Note Updated");   
}

function createCard(note, cardID) {
    var noteDiv = document.createElement("div");
    noteDiv.classList.add("card");
    noteDiv.classList.add("text-left");
    noteDiv.style["background-color"] = note["bg-color"];
    noteDiv.setAttribute("id",cardID);

    var noteBodyDiv = document.createElement("div");
    noteBodyDiv.classList.add("card-body");

    var noteHeadingRow = document.createElement("div");
    noteHeadingRow.classList.add("row");

    var noteHeadingColOne = document.createElement("div");
    noteHeadingColOne.classList.add("col-11");

    var noteHeading = document.createElement("h1");
    noteHeading.classList.add("card-title");
    noteDiv.classList.add(note["font"]);
    noteHeading.style["color"] = note["fg-color"];
    noteHeading.textContent = note["heading"];
    

    var noteHeadingColTwo = document.createElement("div");
    noteHeadingColTwo.classList.add("col-1");

    var noteDeleteButton = document.createElement("button");
    noteDeleteButton.classList.add("btn");
    noteDeleteButton.classList.add("btn-danger");
    noteDeleteButton.setAttribute("onclick",`deleteCard(${cardID})`)

    var noteDeleteIcon = document.createElement("i");
    noteDeleteIcon.classList.add("fa");
    noteDeleteIcon.classList.add("fa-trash");

    var noteLink = document.createElement("a");
    noteLink.classList.add("card-link");
    noteLink.href = note["link"];
    noteLink.contentEditable = "false";
    noteLink.textContent = note["link"];
    noteLink.setAttribute("id",`link${cardID}`)

    var noteEditLinkButton = document.createElement("button");
    noteEditLinkButton.classList.add("btn");
    noteEditLinkButton.classList.add("bg-transparent");
    noteEditLinkButton.classList.add("bg-outline-light");
    noteEditLinkButton.classList.add("mx-1");
    noteEditLinkButton.setAttribute("onclick",`editLink('link${cardID}')`)

    var noteEditLinkIcon = document.createElement("i");
    noteEditLinkIcon.classList.add("fa");
    noteEditLinkIcon.classList.add("fa-pencil");

    var noteDescriptionDiv= document.createElement("div");
    noteDescriptionDiv.classList.add("card-text");
    noteDiv.classList.add(note["font"]);
    noteDescriptionDiv.style["color"] = note["fg-color"];

    var noteDescription = document.createElement("p");
    noteDescription.textContent = note["description"];


    noteHeadingColOne.append(noteHeading);

    noteDeleteButton.append(noteDeleteIcon);
    noteHeadingColTwo.append(noteDeleteButton);

    noteHeadingRow.append(noteHeadingColOne);
    noteHeadingRow.append(noteHeadingColTwo);

    noteEditLinkButton.append(noteEditLinkIcon);

    noteDescriptionDiv.append(noteDescription);

    noteBodyDiv.append(noteHeadingRow);
    noteBodyDiv.append(noteLink);
    noteBodyDiv.append(noteEditLinkButton);
    noteBodyDiv.append(noteDescriptionDiv);

    noteDiv.append(noteBodyDiv);


    var notesList = document.getElementById("notesList");
    notesList.prepend(noteDiv);
}

function deleteCard(deleteID) {
    var deletedNote = document.getElementById(deleteID);
    deletedNote.remove();
    notes.splice(deleteID,1);
    console.log(notes);
    cardID--;
    console.log(cardID);
    localStorage.setItem("Notes",JSON.stringify(notes));
}

function editLink(linkID) {
    var link = document.getElementById(linkID);
    let cardID = parseInt(linkID.substring(4,linkID.length));
    console.log(link.textContent)
    var newLink = document.getElementById(linkID).textContent;
    link.setAttribute("href", newLink);
    notes[cardID]["link"] = newLink;
    localStorage.setItem("Notes",JSON.stringify(notes));
    link.contentEditable = (link.contentEditable == "false")? "true":"false";
}

function loadData() {
    console.log("Hi");
    try {
        console.log("There is Data");
        
        notes = JSON.parse(localStorage.getItem("Notes"))
        for (let i=0; i<notes.length; i++) {
            createCard(notes[i],i);
            cardID++
        }
    }
    catch (e) {
        localStorage.setItem("Notes",JSON.stringify(notes));
        console.log("No Data");
    }
}