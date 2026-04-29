# Reference card

kooker is user oriented tool to enable pulling and execution of docker
containers were docker is unavailable or cannot be used safely.

## 1. Configuration

The configuration of kooker has the following hierarchy:

1. The default configuration options are set in the `conf` dictionary in the `Config` class.
2. If a configuration file is present, it will override 1.
3. If environment variables are set they will override 2.
4. The presence of general kooker command line options, will override 3. .

## 2. Configuration files

The configuration files allow overriding of the kooker `Config` class
`conf` dictionary. Example of the `kooker.conf` syntax:

```ini
[DEFAULT]
dockerio_registry_url = https://myregistry.mydomain:5000
http_insecure = True
verbose_level = 5
```

kooker loads the following configuration files if they are present:

1. `/etc/kooker.conf`
2. `$HOME/.kooker/kooker.conf`: overrides the options set in 1.
3. `$KOOKER_DIR/kooker.conf` (if different from the above): overrides the options set in 2.
4. Configuration file set with the general CLI option `--config=`: overrides the options set in 3.

## 3. Environment variables

* `KOOKER_DIR`: root directory of kooker usually $HOME/.kooker
* `KOOKER_BIN`: location of kooker related executables
* `KOOKER_LIB`: location of kooker related libraries
* `KOOKER_DOC`: location of documentation and licenses
* `KOOKER_CONTAINERS`: location of container directory trees (not images)
* `KOOKER_TMP`: location of temporary directory
* `KOOKER_KEYSTORE`: location of keystore for repository login/logout
* `KOOKER_TARBALL`: location of installation tarball (file of URL)
* `KOOKER_LOGLEVEL`: logging level
* `KOOKER_REGISTRY`: override default registry default is Docker Hub.
* `KOOKER_INDEX`: override default index default is Docker Hub.
* `KOOKER_DEFAULT_EXECUTION_MODE`: change default execution mode
* `KOOKER_USE_CURL_EXECUTABLE`: pathname for curl executable
* `KOOKER_USE_PROOT_EXECUTABLE`: change pathname for proot executable
* `KOOKER_USE_RUNC_EXECUTABLE`: change pathname for runc executable
* `KOOKER_USE_SINGULARITY_EXECUTABLE`: change pathname for singularity executable
* `KOOKER_FAKECHROOT_SO`: change pathname for fakechroot sharable library
* `KOOKER_FAKECHROOT_EXPAND_SYMLINKS`: translate symbolic links in Fn modes
* `KOOKER_NOSYSCONF`: prevent loading of kooker system wide configuration

## 4. Verbosity

The verbosity level of kooker can be enforced. Removing banners and most
messages can be achieved by executing with `KOOKER_LOGLEVEL=2`:

* `KOOKER_LOGLEVEL` : set verbosity level from 0 to 5 (MIN to MAX verbosity)

Optionally invoke kooker with `--quiet` or `-q` to decrease verbosity.

```bash
kooker --quiet run <container>
```

## 5. Security

kooker does not require any type of privileges nor the deployment of
services by system administrators. It can be downloaded and executed
entirely by the end user. kooker runs under the identity of the user
invoking it.

Most kooker execution modes do not provide process isolation features
such as docker. Due to the lack of isolation kooker must not be run
by privileged users.

## 6. Troubleshooting

Invoke kooker with `-D` for debugging.

```bash
kooker -D run <container>
```

## 7. Documentation

For Python 3:

* <https://indigo-dc.github.io/kooker/>
