# Frontend, WebUI
Веб-интерфейс (написан с использованием bootstrap и jQuery) общается с сервером с помощью ajax запросов, исользуя json API.

# Backend
Серверная часть написана на python (tornado). Сервер реализует интерфейс доступа к разработаным класификаторам по средствам json API.

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
          "rawImg1": base64encodedImg
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
          "array": [{"userId": userId, "proba": probability}, ...]
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
