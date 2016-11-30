# UEP_DM
A Python wrapper to access UEP data-mining server

# Quick start
```
$ git clone https://github.com/openbudgets/uep_dm.git
$ cd uep_dm
uep_dm $ source venv/bin/activate
(venv) uep_dm $ pip3 install .
```

# Run test
```
uep_dm $ make test
```

# Generate documentation
```
uep_dm $ ./make_docu
```
Documentation is located at docs/html/

# Access UEP data-mining endpoint within iPython

```
$ iPython

In [1]: import uep_dm
In [2]: uep_dm.send_request_to_UEP_server("./Data/esif.csv")
```
You shall see data-mining results from UEP server as follows:
```
create task response code:201
task_state:in_progress
task_state:in_progress
task_state:in_progress
task_state:solved
{'rules': [{'a': 3,
            'b': 1,
            'c': 0,
            'd': 25,
            'id': 2428330,
            'selected': '0',
            'text': 'competitiveness_of_smes_5((55;60]) → '
                    'technical_assistance_5((55;60])'},
            ...
            ],
   'task': {'id': 7240,
          'importState': 'done',
          'miner': 4997,
          'name': 'Test Miner',
          'rulesCount': 226,
          'rulesOrder': 'default',
          'state': 'solved',
          'type': 'cloud'}}
```
