var form = document.forms.namedItem("dataupload");
var selectedData = null;
var selectedMethod = 1;
var selectedModel = null;

form.addEventListener('submit', function (ev) {
    var oOutput = document.getElementById("dataList");
    var oData = new FormData(form);
    var req = new XMLHttpRequest();
    req.open("POST", "upload", true);
    req.onload = function (oEvent) {
        if (req.status == 200) {
            var li = document.createElement('li');
            var deleteButton = document.createElement('button');
            deleteButton.className = "btn btn-danger pull-right";
            deleteButton.innerHTML = "Удалить";
            li.className = "list-group-item";
            result = req.responseText;
            var resultJson = JSON.parse(result);
            li.innerHTML = resultJson["name"];
            li.appendChild(deleteButton);
            oOutput.appendChild(li);
        } else if (req.status == 201) {

        } else if (req.status == 300) {
            alert("Поддерживаются только .parquet файлы.");
        } else {
            oOutput.innerHTML = "Error " + req.status + " occurred when trying to upload your file.<br \/>";
        }
    };
    req.send(oData);
    ev.preventDefault();
}, false);

document.getElementById("dataList").addEventListener("click", function (e) {
    if (e.target && e.target.matches("li")) {
        if (selectedData)
            selectedData.classList.remove("active");
        selectedData = e.target;
        selectedData.classList.add("active");
    }
    else if (e.target && e.target.matches("button")) {
        var deleteData = e.target.parentElement;
        var req = new XMLHttpRequest();
        req.open("DELETE", "deletedata", true);
        req.onload = function () {
            if (req.status == 200) {
                var oOutput = document.getElementById("dataList");
                oOutput.removeChild(deleteData);
                deleteData = null;
            }
            else
                alert("Файл не найден! (или что-то поломалось)")
        };
        var jsonQuery = {};
        jsonQuery["name"] = getDataFileNameFromElement(deleteData);
        var jsonData = JSON.stringify(jsonQuery);
        req.send(jsonData);
    }
});

document.getElementById("modelList").addEventListener("click", function (e) {
    if (e.target && e.target.matches("li")) {
        if (selectedModel)
            selectedModel.classList.remove("active");
        selectedModel = e.target;
        selectedModel.classList.add("active");
    }
    else if (e.target && e.target.matches("button")) {
        var deletedModel = e.target.parentElement;
        var req = new XMLHttpRequest();
        req.open("DELETE", "deletemodel", true);
        req.onload = function () {
            if (req.status == 200) {
                var oOutput = document.getElementById("modelList");
                oOutput.removeChild(deletedModel);
                deletedModel = null;
            }
            else
                alert("Модель не найдена!")
        };
        var jsonQuery = {};
        jsonQuery["method"] = selectedMethod;
        jsonQuery["name"] = getDataFileNameFromElement(deletedModel);
        var jsonData = JSON.stringify(jsonQuery);
        req.send(jsonData);
    }
});

document.getElementById("testMethod").addEventListener("click", function (e) {
    if (selectedData) {
        sampleSize = document.getElementById("sampleSizeInput").value;
        if (+sampleSize === parseInt(sampleSize, 10)) {
            var req = new XMLHttpRequest();
            req.open("POST", "testmethod", true);
            req.onload = function () {
                if (req.status == 200) {
                    var jsonData = JSON.parse(req.responseText);
                    var output = document.getElementById("outputDiv");
                    renderJson(jsonData, output);
                }
                else
                    alert("Файл не найден! (или что-то поломалось)")
            };
            var jsonQuery = {};
            jsonQuery["method"] = selectedMethod;
            jsonQuery["data"] = getDataFileNameFromElement(selectedData);
            jsonQuery["sampleSize"] = sampleSize;
            var jsonData = JSON.stringify(jsonQuery);
            req.send(jsonData);
        }
        else
            alert("Неверно указан sample size! " + sampleSize);
    }
    else
        alert("Файл не выбран!")
});

document.getElementById("trainModel").addEventListener("click", function (e) {
    if (selectedData) {
        sampleSize = document.getElementById("sampleSizeInput").value;
        if (+sampleSize === parseInt(sampleSize, 10)) {
            var req = new XMLHttpRequest();
            var name = document.getElementById("modelName").value
            req.open("POST", "trainmodel", true);
            req.onload = function () {
                if (req.status == 200) {
                    var jsonData = JSON.parse(req.responseText);
                    var oOutput = document.getElementById("modelList");
                    var li = document.createElement('li');
                    var deleteButton = document.createElement('button');
                    deleteButton.className = "btn btn-danger pull-right";
                    deleteButton.innerHTML = "Удалить";
                    li.className = "list-group-item";
                    li.innerHTML = jsonData["name"];
                    li.appendChild(deleteButton);
                    oOutput.appendChild(li);
                } else if (req.status == 201) {

                } else
                    alert("Файл не найден! (или что-то поломалось)")
            };
            var jsonQuery = {};
            jsonQuery["method"] = selectedMethod;
            jsonQuery["data"] = getDataFileNameFromElement(selectedData);
            jsonQuery["sampleSize"] = sampleSize;
            jsonQuery["name"] = name;
            var jsonData = JSON.stringify(jsonQuery);
            req.send(jsonData);
        }
        else
            alert("Неверно указан sample size! " + sampleSize);
    }
    else
        alert("Файл не выбран!")
});

document.getElementById("predictWithModel").addEventListener("click", function (e) {
    if (selectedData && selectedModel) {
        var req = new XMLHttpRequest();
        req.open("POST", "predict", true);
        req.onload = function () {
            if (req.status == 200) {
                var jsonData = JSON.parse(req.responseText);
                var output = document.getElementById("outputDiv");
                renderJson(jsonData, output);
            }
            else
                alert("что-то поломалось")
        };
        var jsonQuery = {};
        jsonQuery["method"] = selectedMethod;
        jsonQuery["data"] = getDataFileNameFromElement(selectedData);
        jsonQuery["name"] = getDataFileNameFromElement(selectedModel);
        jsonQuery["query"] = document.getElementById("dataQuery").value;
        var jsonData = JSON.stringify(jsonQuery);
        req.send(jsonData);
    }
    else
        alert("Выберете данные и модель!")
});

function getDataFileNameFromElement(liElem) {
    return liElem.querySelector(".list-group-item-filename").innerHTML;
}

function selectMethod(method) {
    dropdown = document.getElementById("dropdownMenuButton")
    switch (method) {
        case 1:
            dropdown.innerHTML = "Анализ HTTP заголовков";
            selectedMethod = 1;
            break;
        case 2:
            dropdown.innerHTML = "Анализ логинов";
            selectedMethod = 2;
            break;
    }
}

function renderJson(jsonData, container) {
    while (container.firstChild) { // clear container
        container.removeChild(container.firstChild);
    }
    html = jsonData['html'];
    script = jsonData['script'];
    scriptData = jsonData['data'];
    container.innerHTML = html;
    eval(script);
    renderResult();
}

// pull system stats
var numberSent = 0;
var numberRecieved = 0;
var sendNextTimeout = 1000;

function executeQuery() {
    var req = new XMLHttpRequest();
    req.open("GET", "sysstats", true);
    req.onload = function () {
        if (req.status == 200) {
            statsOutput = document.getElementById("systemStats");
            var jsonData = JSON.parse(req.responseText);
            var keys = Object.keys(jsonData);
            var datastring = "";
            for (var i = 0; i < keys.length; i++) {
                var key = keys[i];
                datastring = datastring + key + " " + jsonData[key] + "\n";
            }
            statsOutput.innerHTML = datastring;
            numberRecieved++;
        }
    };
    req.send();
    numberSent++;
    if (numberRecieved >= (numberSent - 1)) {
        sendNextTimeout -= 100;
    }
    else
        sendNextTimeout += 100;
    setTimeout(executeQuery, sendNextTimeout);
}

executeQuery(); // start pulling info about server stats
