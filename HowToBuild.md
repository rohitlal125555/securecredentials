# Steps to build from source

1. Clone the repository 

```bash
git clone https://github.com/rohitlal125555/securecredentials.git
```

2. Make sure you have latest version of build library.

```bash
pip install --upgrade build
```

3. Build the package 


```bash
python -m build
```

4. Install the package

```bash
pip install dist/securecredentials-x.x.x-py3-none-any.whl
```


# How to upload to PYPI

1. Make sure you have the latest version of twine.

```bash
pip install --upgrade twine
```

2. Check the build files.

```bash
twine check dist/*
```

3. Push the new build to PYPI. 

```bash
twine upload --repository securecredentials dist/*
```
