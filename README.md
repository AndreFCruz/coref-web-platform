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

## Citation

This repository contains code used for the following publication ([link](https://ieeexplore.ieee.org/abstract/document/8554705)):
```bibtex
@INPROCEEDINGS{8554705,
    author={A. F. Cruz and G. Rocha and H. L. Cardoso},
    booktitle={2018 Fifth International Conference on Social Networks Analysis, Management and Security (SNAMS)},
    title={Exploring Spanish Corpora for Portuguese Coreference Resolution},
    year={2018},
    volume={},
    number={},
    pages={290-295},
    keywords={Task analysis;Training;Natural language processing;Measurement;Social network services;Security;Feature extraction},
    doi={10.1109/SNAMS.2018.8554705},
    ISSN={},
    month={Oct},
}
```
