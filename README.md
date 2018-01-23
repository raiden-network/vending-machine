#
### Prerequisites

 * Python 3.6
 * [pip](https://pip.pypa.io/en/stable/)

### Setup

```
virtualenv -p python3 env
. env/bin/activate
pip install -r requirements.txt
```

### Usage

- from `root/contracts`:

```sh

# compilation
populus compile

# tests
pytest
pytest -p no:warnings -s

# Recommended for speed:
pip install pytest-xdist
pytest -p no:warnings -s -n NUM_OF_CPUs

```
