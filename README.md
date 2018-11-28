# coref-web-platform
Site for testing a coreference resolution system on a user-friendly web interface.

![Screenshot](https://user-images.githubusercontent.com/13498941/44929735-ee7f2180-ad53-11e8-9ffc-6fb635cd091b.png)

## Requirements
Code was written in Python3.5.5, and you must use a Python3.5.x version to load the Tensorflow model.

It's advised to use a [virtualenv](https://virtualenv.pypa.io/en/stable/).

### Polyglot
[Polyglot](https://polyglot.readthedocs.io/en/latest/index.html) depends on _numpy_ and _libicu-dev_.

On Linux use:
```
sudo apt-get install python-numpy libicu-dev
```

On macOS use:
```
brew install icu4c

CFLAGS="-I/usr/local/opt/icu4c/include -std=c++11" LDFLAGS=-L/usr/local/opt/icu4c/lib pip install pyicu
```

### Remaining python packages
```
pip install -r requirements.txt
```
