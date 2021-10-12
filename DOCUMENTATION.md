## Get all questions <br />

`GET` `/questions/` <br />

### Success Response

```
{
    "success": true,
    "data": [
        {
            "id": 1,
            "text": "question 1",
            "qtype": "question type 1",
            "stype": "survey type 1"
        },
        {
            "id": 2,
            "text": "question 2",
            "qtype": "question type 2",
            "stype": "survey type 2"
        },
        {
            "id": 3,
            "text": "question 3",
            "qtype": "question type 3",
            "stype": "survey type 3"
        }
    ]
}
```

## Create a question

`POST` `/questions/` <br />

### Request

```
{
    "text": "question text",
    "qtype": "question type",
    "stype": "survey type"

}
```

### Success Response

```
{
    "success": true,
    "data": [
        {
            "text": "question text",
            "qtype": "question type",
            "stype": "survey type"
        }

    ]
}
```

## Get all survey responses

`GET` `/responses/` <br />

### Success Response

```
{
    "success": true,
    "data": [
        {
            "id": 1,
            "description": "Supplies requested",
            "response_id": 1,
            "answer_text": "clothes",
            "question_id": 1,
            "time_of_submit": "19-Apr-2021 (02:36:50.   417520)",
            "addressed": false
        },
        {
            "id": 2,
            "description": "Location of request",
            ...
        }
    ]
}
```

## Create a survey response

`POST` `/responses/` <br />

### Request

```
{
    "description": "Supplies requested",
    "response_id": 1,
    "answer_text": "clothes",
    "question_id": 1
}
```

### Success Response

```
{
    "success": true,
    "data": {
        "id": 1,
        "description": "Supplies requested",
        "response_id": 1,
        "answer_text": "clothes",
        "question_id": 1,
        "time_of_submit": "19-Apr-2021 (02:36:50.417520)",
        "addressed": false
    }
}
```

## Get all counts of answers for certain question

`GET` `/responses/ct/{question_id}` <br />

### Success response

```
{
    "success": true,
    "data": {
            "answer_text1": 1,
            "answer_text2": 4,
            "answer_text3": 2,
    }
}
```

## Mark response as addressed

`POST` `/addressed/{survey_id}/` <br />

### Success response

```
{
    "success": true,
    "data": {
        "id": 0,
        "description": "Supplies requested",
        "response_id": 2,
        "answer_text": "clothes",
        "question_id": 1,
        "time_of_submit": "19-Apr-2021 (02:36:50.417520)",
        "addressed": true
    }
}
```

## Filter for response_ids by age range, zipcode, or dates

`POST` `/filter/` <br />

### Request

Note: not all the parameters have to be nonempty, simply do not include a parameter if there is no filter needed for certain parameters, date must also be in format of `%Y-%m-%d`

```
{
    "age": "question text",
    "zipcode": "question type",
    "start_date": "2021-03-19",
    "end_date": "2021-04-19"
}
```

### Success response

```
{
    "success": true,
    "data": [
        "1",
        "3",
        ...
    ]
}
```
