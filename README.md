
# CABLE API

The Cable API is an API created specifically to build simple one to one chat applications. 




## API Reference

#### Recieve JWT tokens

```http
  POST /api/token/
```
A request dictionary containing the users authentication credentials must be sent to this enpoint. The endpoint returns a dictionary containing JWT access and refresh tokens.

#### Refresh access token

```http
  POST /api/token/
```
A request dictionary containing the users a refresh token must be sent ot this endpoint. The endpoint returns a new pair of JWT access and refresh tokens.

#### Get users

```http
  GET /api/users/
```
Returns a list of user objects.

#### Post users

```http
  POST /api/users/
```
A request dictionary containing the users credentials must be sent to this endpoint. The enpoint creates are new user using the credentials and sends back the user object as response.

#### Get user

```http
  GET /api/users/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id of item to fetch |

Returns the queried user object.

#### Patch user

```http
  PATCH /api/users/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id of item to fetch |

A request dictionary containing values to update must be sent to this endpoint. The endpoint updates the fields sent to it in the user object it has queried and returns the updated user object.

#### Delete user

```http
  DELETE /api/users/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id of item to fetch |

Deletes the queried object.

#### Get chats

```http
  GET /api/chats/
```
Returns a list of chat objects.

#### Post chats

```http
  POST /api/chats/
```
A request dictionary containing the email addres of the user the chat is being created with must be sent to this endpoint. The enpoint creates are new chat using the email and returns the  new chat object as response.

#### Get chat

```http
  GET /api/chats/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id of item to fetch |

Returns the queried chat object.

#### Patch chat

```http
  PATCH /api/chats/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id of item to fetch |

A request dictionary containing values to update must be sent to this endpoint. The endpoint updates the fields sent to it in the chat object it has queried and returns the updated chat object.

#### Delete chat

```http
  DELETE /api/chats/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id of item to fetch |

Deletes the queried object.

#### Get messages

```http
  GET /api/messages/
```
Returns a list of message objects.

#### Post messages

```http
  POST /api/messages/
```
A request dictionary containing the content of the that message is being created with must be sent to this endpoint. The enpoint creates are new message using the  new message object as response.

#### Get message

```http
  GET /api/messages/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id of item to fetch |

Returns the queried message object.

#### Patch message

```http
  PATCH /api/messages/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id of item to fetch |

A request dictionary containing values to update must be sent to this endpoint. The endpoint updates the fields sent to it in the message object it has queried and returns the updated message object.

#### Delete message

```http
  DELETE /api/messages/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id of item to fetch |

Deletes the queried object.









## Development Environment setup

- Clone this git repository
  ```bash
  git clone https://github.com/Anubhav-Sen/cable_api.git
  ```
- Create a virtual environment
  ```bash
  python -m venv venv
  ```
- Activate the virtual environment
  ```bash
  source venv/scripts/activate
  ```
- Install dependencies from requirements.txt
  ```bash
  pip install -r requirements.txt
  ```
- Replace the DATABASES variable in setting.py with
  ```bash
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3', 
      }
    }
    ```
- Run migrations
  ```bash
  python manage.py migrate
  ```
- Finally run the development server
  ```bash
  python manage.py runserver
  ```
