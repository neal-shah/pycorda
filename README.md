# PyCorda

Access node and vault data for analytics using pandas DataFrames. Currently only works with H2 database. 
We'll be adding other DBs shortly and possibly support for queryable states.

## PyCorda.com
Access docs on PyCorda.com (coming soon)

## Requirements

1. Currently supports 64-bit versions of Python 3 and JVMs only
2. Drop a database driver jar into your project folder naming it db-driver.jar

## Supported Databases
In theory every database with a suitable JDBC driver should work. It is confirmed to work with the following databases:
- H2
- PostgreSQL

## Example

```python
import pycorda as pyc

url = 'jdbc:h2:tcp://localhost:52504/node'
username = 'sa'
password = ''
node = pyc.Node(url, username, password)
print(node.get_node_infos())
node.close()
```

## Installation

To get started using the PyCorda library, install it with

```bash
pip install pycorda
```

If there is a H2 server running with tcp connections allowed,
then you can connect to a database located at the JDBC url with:

```python
from pycorda import Node
node = Node(url, username, password)
```

An h2.jar file is required in your projects local folder. If your H2 jar file is elsewhere in your filesystem, try this. This needs to be done only once:

```python
from pycorda import Node
node = Node(url, username, password, path_to_jar)
```
Accepted JDBC urls are in the format jdbc:h2:tcp://hostname:portnumber/path_to_database.

## Managing Database Drivers Jars

An db-driver.jar file stored locally in the project folder is required. DBTools allows you to pull
a jar programmatically. You'll need to do this once, so either manually or programmatically is fine
as long as the db-driver.jar file is there.

By default, the H2 database driver will be downloaded to the project folder, as below:

```python
import pycorda as pyc
h2 = pyc.DBTools()
ver = h2.get_latest_version()
print(ver)
h2.download_jar() # downloads latest h2 jar and stores in local folder as db-driver.jar
```
For PostgreSQL:
```python
import pycorda as pyc
pg = pyc.DBTools("pg")
ver = pg.get_latest_version()
print(ver)
pg.download_jar() # downloads latest pg jar and stores in local folder as db-driver.jar
```