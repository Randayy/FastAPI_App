# My FastAPI Application

Це додаток FastAPI, який демонструє поки , що простий ендпоінт для перевірки стану додатку.

## Як запустити цей додаток?

Щоб запустити додаток , виконайте наступні кроки:

1. **Клонуйте репозиторій**: Спочатку склонуйте цей репозиторій за допомогою Git:

    ```bash
    git clone https://github.com/Randayy/FastAPI_App.git
   

2. **Перейдіть у директорію проекту**: Перейдіть у директорію проекту:
   ```bash
    cd FastAPI_App
    
3. **Встановіть залежності**: Встановіть необхідні залежності за допомогою pip:

    ```bash
    pip install -r requirements.txt | pip3 install -r requirements.txt
    

4. **Запустіть додаток**: Запустіть додаток FastAPI за допомогою uvicorn:

    ```bash
    uvicorn app.main:app --reload
    

5. **Отримайте доступ до ендпоінту перевірки стану**: Як тільки сервер запуститься, ви зможете отримати доступ до ендпоінту перевірки стану у вашому веб-браузері або за допомогою інструментів, таких як cURL або Postman. За замовчуванням ендпоінт буде доступний за адресою [http://localhost:8000/](http://localhost:8000/).

Для запуску тесту перейдіть у директорію tests:

    cd tests

Запустіть тест:

    pytest

Отримаєте результат тесту
