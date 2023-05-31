# Mstock: Information System to Construct Portfolios under Risk

*Gabriel Zhang*

## Description

The project is about my graduate paper of bachelor.

Background: Beihang University/School of Economy and Management/Information Management and Information System

## Virtual Environment

Use the powershell commands in the root folder.

```powershell
python -m venv myvenv
.\\myvenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If that does not works, you can try

```powershell
pip install virtualenv
virtualenv myvenv --python=python3.9
```

## Initiate System

In the virtual environment,

```powershell
$env:FLASK_APP = "mstock"
$env:FLASK_DEBUG = 1
flask db init
flask shell
```

In the shell,

```python
>>>from app.initial import initial_database
>>>initial_database('your email', 'your password') ## use your own email address to create an administrator account
>>>quit()
```

Use the following command to run locally.

```powershell
flask run
```

Or you can use the command as follow to run in a Local Area Network.

```powershell
flask run --host=0.0.0.0 --port=5000
```

You can use a personal port number as long as it is valid.

Commands of Linux, MacOS, CMD didn't display here.

## Configuration

The default configuration is using a SQLite3 database.

If you have a PostgreSQL, you can use a development configuration.

```powershell
$env:FLASK_CONFIG = "production"
$env:DATABASE_URL = "postgresql://[username]:[password]@localhost:[portnumber]/[databasename]"
```

Example URL: "postgresql://postgres:123456@localhost:5432/mstcok"

Remember to create a database in your PostgreSQL
