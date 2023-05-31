# Mstock

*Gabriel Zhang*

## 说明

本项目为作者毕业设计项目

北京航空航天大学 经济管理学院 信息管理与信息系统 2019级

## 虚拟环境

在根目录下打开powershell并使用以下命令进入虚拟环境

```powershell
python -m venv myvenv
.\\myvenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

如果出现任何由Python版本导致的问题，可以尝试使用Python3.9版本

```powershell
pip install virtualenv
virtualenv myvenv --python=python3.9
```

## 系统初始化

在虚拟环境中，使用以下命令

```powershell
$env:FLASK_APP = "mstock"
$env:FLASK_DEBUG = 1
flask db init
flask shell
```

在shell中，使用以下命令初始化数据库

```python
>>>from app.initial import initial_database
>>>initial_database('your email', 'your password') ## use your own email address to create an administrator account
>>>quit()
```

使用以下命令使得系统在本地运行

```powershell
flask run
```

使用以下命令使得系统在设备所在的局域网中运行

```powershell
flask run --host=0.0.0.0 --port=5000
```

可以把端口号更换为任意合法的端口号

Linux, MacOS或CMD中使用的命令未在此处展示，您可以利用网络资源查找以上三个平台中的对应命令

## Configuration

默认配置使用SQLite3数据库

如果您拥有PostgreSQL数据库，您也可以使用以下命令应用该数据库

```powershell
$env:FLASK_CONFIG = "production"
$env:DATABASE_URL = "postgresql://[username]:[password]@localhost:[portnumber]/[databasename]"
```

示例URL: "postgresql://postgres:123456@localhost:5432/mstcok"

您需要在PostgreSQL中事先创建对应的数据库
