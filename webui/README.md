# Frontend, WebUI
Веб-интерфейс (написан с использованием bootstrap и jQuery) общается с сервером с помощью ajax запросов, исользуя json API.

# Backend
Серверная часть написана на python (tornado). Сервер реализует интерфейс доступа к разработаным класификаторам по средствам json API.

# Динамическая вёрстка ответа из Json
Методы trainmodel и predict возрващают Json объект со следующим форматом:
```
body =  {
          "html": html,
          "script": javascript,
          "data":	{
						"data_1": arbitraryDataDependingOnMethod,
						...
						"data_N": arbitraryDataDependingOnMethod
					}
        }
```
На фронтенде используется функция renderJson для отображения полученой информации:
```
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
```
В функции script, определяемой в функции-обёртки необходимо определить функцию renderResult(), которая может использовать следующие объекты:
- переменную контейнер container для отрисовки в неё информации;
- хранилище scriptData, содержащее информацию из поля "data" json-объекта, переданного с сервера;

## Примеры функций script:
### Отрисовка графика тестирования модели headers:
HTML:
```
<img id='resultGraph' src=''/>
```
Скрипт:
```
function renderResult() { 
	var rawImg1 = scriptData['rawImg1']; 
	$('#resultGraph').attr('src','data:image/gif;base64,'+rawImg1)
;}
```
Хранилище:
```
data: {
	"rawImg1": base64encodedImage
}
```
### Отрисовка результата предсказания для модели headers:
HTML - пустой.
Скрипт:
```
function renderResult() {
	var ul = document.createElement('ul');
	ul.className = 'list-group';
	container.appendChild(ul);
	arr = jsonData['array'];
	for (var entry in arr) {
		var li = document.createElement('li');
		li.className = 'list-group-item';
		li.innerHTML = arr[entry]["userId"] + " " + arr[entry]['proba'];
		ul.appendChild(li);
	}
}
```
Хранилище - пустое (но оно должно быть!).
# Json API
## testmethod
### Request
url: /testmethod
```
body =  {
          "method": methodId,
          "data": dataFileName,
          "sampleSize": sampleSize
        }
```
### Response
```
body =  {
          "html": html,
          "script": javascript,
          "data":	{
						"data_1": arbitraryDataDependingOnMethod,
						...
						"data_N": arbitraryDataDependingOnMethod
					}
        }
```

## trainmodel
### Request
url: /testmethod
```
body =  {
          "method": methodId,
          "data": dataFileName,
          "sampleSize": sampleSize,
          "name": modelName
        }
```
### Response
Response code 200 - new model was created.

Response code 201 - old model was rewritten.
```
body =  {
          "name": modelFileName,
        }
```

## predict
### Request
url: /testmethod
```
body =  {
          "method": methodId,
          "data": dataFileName,
          "name": modelName,
          "query": pandasQueryStrin
        }
```
### Response
Response code 200 - success.
```
body =  {
			"array": [{"userId": userId, "proba": probability} ... ]
			"html": html,
			"script": javascript,
			"data":	{
						"data_1": arbitraryDataDependingOnMethod,
						...
						"data_N": arbitraryDataDependingOnMethod
					}
        }
```

## deletedata
### Request
url: /testmethod
```
body =  {
          "name": dataFileName
        }
```
### Response
Response code 200 - deleted.

Response code 404 - not found.

## deletemodel
### Request
url: /testmethod
```
body =  {
          "method": methodId,
          "name": modelFileName
        }
```
### Response
Response code 200 - deleted.

Response code 404 - not found.
