# How to compile/build the SecureCredentials module

1. Clone the repository 

```bash
git clone https://github.com/rohitlal125555/securecredentials.git
```

2. Make sure you have latest version of build library.

```bash
pip install --upgrade build
pip install twine
```

3. Build the package 


```bash
python -m build
```

4. (Optional) Check the build files.

```bash
twine check dist/*
```

5. (Optional) Push the new build to PYPI. 

```bash
twine upload --repository securecredentials dist/*
```
