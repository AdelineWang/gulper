# gulper

## Installation

First install system dependencies

```
$ bash dependencies.sh
```

Then python dependencies

```
# pip install -U -r requirements.txt
```

Decrypt the config file

```
$ python3 config_packer.py decrypt config.conf.enc > config.conf
```

and finally, run!

```
$ source ~/.bashrc # since your shell probably sucks
$ python3 api.py
```
