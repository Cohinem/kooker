# Making a kooker release

* Verify that the version is updated.
* Update the `CHANGELOG.md`.
* build python binary dist to upload to test pypi:

```bash
python -m build --wheel .

python setup.py sdist bdist_wheel
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

* Test the new version.

```bash
pip install --index-url https://test.pypi.org/simple/ kooker
```

* If tests ok, upload to pypi, and check if you can install and run

```bash
twine upload dist/*
pip install kooker
kooker version
```

* Prepare a PR and check jenkins pipeline are ok, then approve

* Make an independent tarball of kooker

```bash
cd utils
./make_kookertar.sh
cd ..
```

* It produces kooker-x.y.z.tar.gz
* On github make a **new release** and upload this tarball, copy/paste text
  from other release.
