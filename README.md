# RecommendU-web
π― [FE/BE] λ§μΆ€ν ν©κ²© μκΈ°μκ°μ μΆμ² μλΉμ€ RecommendU

## π  Stack
### Frontend
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=JavaScript&logoColor=white"> <img src="https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=HTML5&logoColor=white"> <img src="https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=CSS3&logoColor=white">

### Backend
<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=Python&logoColor=white"> <img src="https://img.shields.io/badge/Django-092E20?style=flat-square&logo=Django&logoColor=white"> <img src="https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=MySQL&logoColor=white">

## π Database Schema Diagram
![image](https://user-images.githubusercontent.com/46878756/217413934-be4973f7-1273-43ea-beb1-4ea817d8219a.png)

## β Core Functions
### μ¬μ©μ λΆλΆ
  - νμκ°μ λ° λ‘κ·ΈμΈ κΈ°λ₯ κ΅¬ν (λΉλ°λ²νΈ μνΈν μ μ₯)
  - Django Authentication Systemμ μ¬μ©ν μ¬μ©μ μΈμ¦
  - νμμ λ³΄ μμ  κΈ°λ₯ κ΅¬ν
### μκΈ°μκ°μ λΆλΆ
  - μ¬μ©μκ° μλ ₯ν μ λ³΄μ λ°λΌμ νμ΅ λͺ¨λΈμ ν΅ν΄ inference ν΄μ£Όλ API κ΅¬ν
  - μκΈ°μκ°μμ λν `μ’μμ`, `μ«μ΄μ`, `μ€ν¬λ©` μ²΄ν¬ κΈ°λ₯ κ΅¬ν
  - μ¬μ©μ λ³ λ§μ΄ νμ΄μ§ μ€ν¬λ©ν μκΈ°μκ°μ λ³΄μ¬μ£ΌκΈ° κ΅¬ν
### λ‘κ·Έ λΆλΆ
  - λ΅λ³μ μ μΈν μ¬μ©μκ° μλ ₯ν μ λ³΄(νμ¬,μ§λ¬΄,μ§λ¬Έ)λ₯Ό μ μ₯νλ λ‘κ·Έ(`recommendlog`) κ΅¬ν
  - μΆμ²λ μκΈ°μκ°μλ₯Ό λλ μ λ μ μ₯λλ λ‘κ·Έ(`answerlog`) κ΅¬ν
  - `μ’μμ`, `μ«μ΄μ` λ²νΌμ λλ μ λ μ μ₯λλ λ‘κ·Έ(`evallog`) κ΅¬ν
### ML μλ² μ°κ²° λΆλΆ
  - νμ΅μ νμν λ°μ΄ν°λ₯Ό λ³΄λ΄μ£Όλ API κ΅¬ν
  - νμ΅ λͺ¨λΈμ λ°λ API κ΅¬ν
  
## π Structure
```
|-- accounts
|   |-- __init__.py
|   |-- admin.py
|   |-- apps.py
|   |-- forms.py
|   |-- models.py
|   |-- serializers.py
|   |-- templates
|   |   `-- accounts
|   |       |-- login.html
|   |       |-- mypage.html
|   |       `-- signup.html
|   |-- tests.py
|   |-- urls.py
|   `-- views.py
|-- inference
|   |-- predict.py
|   |-- preprocess.py
|   `-- similarity.py
|-- logs
|   |-- __init__.py
|   |-- admin.py
|   |-- apps.py
|   |-- models.py
|   |-- serializers.py
|   |-- tests.py
|   |-- urls.py
|   `-- views.py
|-- manage.py
|-- recommendu
|   |-- __init__.py
|   |-- asgi.py
|   |-- settings.py
|   |-- urls.py
|   `-- wsgi.py
|-- requirements.txt
|-- services
|   |-- __init__.py
|   |-- admin.py
|   |-- apps.py
|   |-- dbinit
|   |   |-- initiation.py
|   |-- models.py
|   |-- serializers.py
|   |-- templates
|   |   `-- services
|   |       `-- main.html
|   |-- tests.py
|   |-- urls.py
|   `-- views.py
|-- static
|   |-- css
|   |   `-- style.css
|   |-- images
|   `-- js
|       `-- index.js
`-- templates
    |-- base.html
   
```

## Usage
