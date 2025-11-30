# Отчет по Лабораторной работе №2. Интеграционное тестирование

Выполнила Ходакова Мария Александровна

ИСУ 409800

Группа K3323

tg: @m_inf

### 1. Выбор проекта

Для выполнения лабораторной работы я выбрала проект FastAPI-CRUD-Todo. В проекте есть несколько взаимосвязанных модулей, что позволяет удобно продемонстрировать интеграционное тестирование.

В проекте используется SQLite и библиотека SQLAlchemy, значит, есть интеграция:
API - бизнес-логика - база данных - ответ.

Приложение работает с сущностью “задача” (ToDo) и поддерживает CRUD: создание, чтение, обновление и удаление.

### 2. Анализ взаимодействий

**Ключевые точки интеграции:**

1. API - HTTP-слой - routers

(В файле routers/todo.py определены HTTP-эндпоинты (для создания, получения, обновления, удаления задач))

Клиент делает HTTP-запрос на endpoint, запрос попадает в FastAPI-приложение, попадает в соответствующий роутер.

2. Router - Схемы данных (валидация и сериализация) - Pydantic-схемы

В проекте есть файл schemas.py, в котором описаны Pydantic-модели для входящих и исходящих данных. 

При получении запроса API данные валидируются спо схемам, при отдаче ответа сериализуются в нужный формат.

3. Схемы - ORM-модели - SQLAlchemy

   (модель - база данных)

В файле models.py описаны SQLAlchemy-модели, которые соответствуют структуре таблицы в базе данных.

Когда приходит запрос (после валидации), роутер / бизнес-логика создают/модифицируют/удаляют ORM-объекты - SQLAlchemy взаимодействует с SQLite: делает INSERT, UPDATE, DELETE, SELECT и т. д. Через сессию.

4. Database setup & connection (инициализация и сессии) - ORM - API

В файле database.py есть конфигурация подключения к SQLite, создание сессии, управление соединением с БД.

При обращении через API: получение сессии, выполнение операции через ORM, commit, возврат результата, сериализация и возврат клиенту.

**Критические части системы **

База данных (SQLite + SQLAlchemy-модели + сессии). Если неправильно настроено подключение, или неправильно описаны модели/схемы, то операции будут давать ошибку.

Схемы. Если входящие данные не соответствуют Pydantic-схемам, запросы будут отвергаться до обращения к БД.

routers (эндпоинты). Если маршрутизация или логика обработки запросов будет неправильной, API просто не будет работать или будет работать неверно.

Согласованность между схемами, моделями и API. Запросы, ORM-модели и схемы должны быть корректными по структуре данных, иначе интеграция даст сбой.

Обработка сессий и транзакций. Нужно корректно открывать/закрывать сессии, коммитить изменения, обрабатывать ошибки, иначе могут появиться утечки, несогласованности, неверные данные.

**Основные сценарии взаимодействия**

1. Создание новой задачи — API POST, база данных, возврат результата

Клиент отправляет POST запрос на endpoint создания задачи. Данные проходят валидацию (Pydantic), затем попадают в ORM-модель, сохраняются в базу (SQLite). Возвращается JSON-ответ с подробностями созданной задачи (id, текст, статус и тд).

2. Получение списка задач — API GET, DB SELECT, возврат списка

Клиент отправляет GET запрос на endpoint получить все задачи. ORM извлекает все записи из БД, сериализует их через схемы и возвращает JSON-массив задач.

3. Чтение задачи по id — API GET, DB SELECT, возврат результата

Клиент запрашивает задачу по конкретному id. ORM ищет запись, возвращает её, схема сериализует, клиент получает JSON.
Если задачи с таким id нет, то возвращается ошибка.

4. Обновление задачи — API PUT/PATCH, валидация, ORM, commit, возврат обновленной задачи

Клиент отправляет запрос на изменение полей задачи. Данные валидируются, ORM-модель обновляется, изменения сохраняются в бд, возвращается обновлённый объект.

5. Удаление задачи — API DELETE, ORM delete, commit, подтверждение удаления

Клиент делает DELETE запрос на удаление задачи по id. ORM удаляет запись из БД, коммит. Успех или ошибка, если задача не найдена.

6. Граничные сценарии

Попытка создать задачу с некорректными данными, ожидание ошибки валидации, и то, что в бд ничего не появилось.

Запрос к несуществующему id, ожидание корректного ответа и отсутствие данных.


### Тесты 

```
@mari-w-e ➜ /workspaces/test-po $ python -m pytest -q
......                                                         [100%]
6 passed in 0.54s
```


```
@mari-w-e ➜ /workspaces/test-po $ python -m pytest tests/test_integration_todo.py -v
======================== test session starts =========================
platform linux -- Python 3.12.1, pytest-9.0.1, pluggy-1.6.0 -- /home/codespace/.python/current/bin/python
cachedir: .pytest_cache
rootdir: /workspaces/test-po
plugins: anyio-4.11.0, asyncio-1.3.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 6 items                                                    

tests/test_integration_todo.py::test_create_todo PASSED        [ 16%]
tests/test_integration_todo.py::test_get_all_todos PASSED      [ 33%]
tests/test_integration_todo.py::test_get_single_todo PASSED    [ 50%]
tests/test_integration_todo.py::test_update_todo PASSED        [ 66%]
tests/test_integration_todo.py::test_delete_todo PASSED        [ 83%]
tests/test_integration_todo.py::test_get_nonexistent_todo PASSED [100%]

========================= 6 passed in 0.48s ==========================
```

```
@mari-w-e ➜ /workspaces/test-po $ python -m pytest --cov=. --cov-report=term-missing -v
======================== test session starts =========================
platform linux -- Python 3.12.1, pytest-9.0.1, pluggy-1.6.0 -- /home/codespace/.python/current/bin/python
cachedir: .pytest_cache
rootdir: /workspaces/test-po
plugins: anyio-4.11.0, cov-7.0.0, asyncio-1.3.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 6 items                                                    

tests/test_integration_todo.py::test_create_todo PASSED        [ 16%]
tests/test_integration_todo.py::test_get_all_todos PASSED      [ 33%]
tests/test_integration_todo.py::test_get_single_todo PASSED    [ 50%]
tests/test_integration_todo.py::test_update_todo PASSED        [ 66%]
tests/test_integration_todo.py::test_delete_todo PASSED        [ 83%]
tests/test_integration_todo.py::test_get_nonexistent_todo PASSED [100%]

=========================== tests coverage ===========================
__________ coverage: platform linux, python 3.12.1-final-0 ___________

Name                             Stmts   Miss  Cover   Missing
--------------------------------------------------------------
database/database.py                11      0   100%
main.py                              9      1    89%   12
models/models.py                     8      0   100%
routers/todo.py                     41      2    95%   35, 46
schemas/schemas.py                  14      0   100%
tests/test_integration_todo.py      41      0   100%
--------------------------------------------------------------
TOTAL                              124      3    98%
========================= 6 passed in 1.61s ==========================
```
