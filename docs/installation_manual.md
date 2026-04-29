# Installation and configuration manual

In most cases the end user can download and execute kooker without
system administrator intervention. kooker itself is written in Python, but
also uses external binaries and libraries to provide a chroot like
environment where containers are executed in user space. These tools do not
require any privileges and constitute the kooker tools and libraries for
engines that is downloaded and installed by kooker itself.

Redistribution, commercial use and code changes must regard all licenses
shipped with kooker. For more information see
[section 6 External tools and libraries](#6-external-tools-and-libraries).

## 1. Dependencies

The kooker dependencies are minimal and should be supported by most Linux installations.
kooker requires:

* Python 3 or alternatively Python >= 2.7
* pycurl or alternatively the curl command
* python hashlib or alternatively the openssl command
* tar
* find
* chmod
* chgrp
* ldconfig (only used by the Fn execution modes)

## 2. Installation

### 2.1. Install from a released version

Download a release tarball from <https://github.com/indigo-dc/kooker/releases>:

```bash
wget https://github.com/indigo-dc/kooker/releases/download/1.3.17/kooker-1.3.17.tar.gz
tar zxvf kooker-1.3.17.tar.gz
export PATH=`pwd`/kooker-1.3.17/kooker:$PATH
```

Alternatively use `curl` instead of `wget` as follows:

```bash
curl -L https://github.com/indigo-dc/kooker/releases/download/1.3.17/kooker-1.3.17.tar.gz \
  > kooker-1.3.17.tar.gz
tar zxvf kooker-1.3.17.tar.gz
export PATH=`pwd`/kooker-1.3.17/kooker:$PATH
```

kooker executes containers using external tools and libraries that
are enhanced and packaged for use with kooker. For more information see
[section 6 External tools and libraries](#6-external-tools-and-libraries).
Therefore to complete the installation invoke `kooker install` to download
and install the required tools and libraries.

```bash
kooker install
```

### 2.2. Install from the GitHub repositories

To install the latest stable code from the github `master` branch:

```bash
git clone --depth=1 https://github.com/indigo-dc/kooker.git
(cd kooker/kooker; ln -s maincmd.py kooker)
export PATH=`pwd`/kooker/kooker:$PATH
```

Alternatively, install the latest development code from the github `dev-v1.4` branch:

```bash
git clone -b dev-v1.4 --depth=1 https://github.com/indigo-dc/kooker.git
(cd kooker/kooker; ln -s maincmd.py kooker)
export PATH=`pwd`/kooker/kooker:$PATH
```

Alternatively, install the latest development code from the github `devel3` branch:

```bash
git clone -b devel3 --depth=1 https://github.com/indigo-dc/kooker.git
(cd kooker/kooker; ln -s maincmd.py kooker)
export PATH=`pwd`/kooker/kooker:$PATH
```

kooker executes containers using external tools and libraries that
are enhanced and packaged for use with kooker. For more information see
[section 6 External tools and libraries](#6-external-tools-and-libraries).
Therefore to complete the installation invoke `kooker install` to download
and install the required tools and libraries.

```bash
kooker install
```

### 2.3. Install from PyPI using pip

For installation with pip it is advisable to setup a Python3 virtual environment
before proceeding, see
[Creating a virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment).

```bash
python3 -m venv kookervenv
source kookervenv/bin/activate
pip install kooker
```

The kooker command will be `kookervenv/bin/kooker`.

kooker executes containers using external tools and libraries that
are enhanced and packaged for use with kooker. For more information see
[section 6 External tools and libraries](#6-external-tools-and-libraries).
Therefore to complete the installation invoke `kooker install` to download
and install the required tools and libraries.

```bash
kooker install
```

### 2.4. Install without outbound network access

When the installation is attempted without having outbound network connectivity,
the installation of the binary tools and libraries with `kooker install` will
fail the download step. The solution is to fetch the the tarball in advance
and then install the tools and libraries directly from the tarball file.

The tarballs containing the tools and libraries are available at <https://github.com/jorge-lip/kooker-builds>.

First, download a tarball file using:

```bash
curl -L https://github.com/jorge-lip/kooker-builds/raw/master/tarballs/kooker-englib-1.2.8.tar.gz > kooker-englib-1.2.8.tar.gz
```

Second, transfer the kooker code plus the tarball containing the tools and
libraries to the target destination host.

Finally perform the `kooker install` step using the transferred tarball file.

```bash
export KOOKER_TARBALL=kooker-englib-1.2.8.tar.gz
kooker install
```

The environment variable `KOOKER_TARBALL` can also point to an URL to fetch
the tarball from a specific or alternate location. To fetch from multiple
possible locations for redundancy the environment variable `KOOKER_TARBALL`
can contain multiple URLs separated by a blank.

```bash
export KOOKER_TARBALL="https://... https://... http://..."
kooker install
```

### 2.5. Force the re-installation of the tools and libraries

To force download and re-installation of the kooker tools and libraries.
Invoke `kooker install` with the flag `--force`:

```bash
kooker install --force
```

## 3. Configuration

The configuration of kooker has the following hierarchy:

1. The default configuration options are set in the `conf` dictionary in the `Config` class.
2. If a configuration file is present ([section 4. Configuration files](#4-configuration-files)),
   it will override 1.
3. If environment variables are set ([section 5. Environment variables](#5-environment-variables)),
   they will override 2.
4. The presence of general kooker command line options, will override 3.

### 3.1. Directories

With the default configuration, kooker creates files and subdirectories under
`$HOME/.kooker` these are:

* `doc`: documentation and licenses.
* `bin`: executables to support the execution engines.
* `lib`: libraries, namely the fakechroot libraries to support the **F** execution mode.
* `repos`: container image repositories.
* `layers`: the layers and metadata for the container images.
* `containers`: created containers.
* `keystore.github`: authentication to access repositories (created on demand).

Both installed files, as well as the containers to be downloaded or created
with kooker, will be installed by default under `$HOME/.kooker`.

A default configuration file is available at
[kooker.conf](https://github.com/indigo-dc/kooker/blob/master/etc/kooker.conf)
it can be copied to your kooker directory as `$HOME/.kooker/kooker.conf` and
customized.

## 4. Configuration files

The configuration files allow overriding of the kooker `Config` class
`conf` dictionary. Example of the `kooker.conf` syntax:

```ini
dockerio_registry_url = "https://myregistry.mydomain:5000"
http_insecure = True
verbose_level = 5
```

kooker loads the following configuration files if they are present:

1. `/etc/kooker.conf`
2. `$HOME/.kooker/kooker.conf`: overrides the options set in 1.
3. `$KOOKER_DIR/kooker.conf` (if different from the above): overrides the options set in 2.
4. Configuration file set with the general CLI option `--config=`: overrides the options set in 3.

## 5. Environment variables

The following environment variables can be used to customize the installation.
The location of the kooker directories can be changed via the environment
variables:

* `KOOKER_DIR`: root directory of kooker usually $HOME/.kooker
* `KOOKER_BIN`: location of kooker related executables
* `KOOKER_LIB`: location of kooker related libraries
* `KOOKER_DOC`: location of documentation and licenses
* `KOOKER_REPOS` images metadata and links to layers
* `KOOKER_LAYERS`: the common location for image layers data
* `KOOKER_CONTAINERS`: location of container directory trees (not images)
* `KOOKER_TMP`: location of temporary directory
* `KOOKER_KEYSTORE`: location of keystore for login/logout credentials
* `KOOKER_TARBALL`: location of installation tarball (file of URL)
* `KOOKER_NOSYSCONF`: do not read system wide config files in /etc

The Docker index and registry can be overridden via the environment variables.

* `KOOKER_INDEX=https://...`
* `KOOKER_REGISTRY=https://...`

The verbosity level of kooker can be enforced. Removing banners and most
messages can be achieved by executing with `KOOKER_LOGLEVEL=2`.

* `KOOKER_LOGLEVEL`: set verbosity level from 0 to 5 (MIN to MAX verbosity)

Forcing the use of a given curl executable instead of pycurl can be
specified with:

* `KOOKER_USE_CURL_EXECUTABLE`: pathname to the location of curl executable

The fakechroot execution modes (Fn modes), the translation of symbolic links
to the actual links can be controlled by the environment variable
`KOOKER_FAKECHROOT_EXPAND_SYMLINKS`. The default value is
`none` which will select automatically the mode to be used, `false` if mounts are
not performed or if the mount points pathname for the host and container
are equal (e.g `-v /home:/home`), `true` otherwise (e.g `-v /data:/home`).

* `KOOKER_FAKECHROOT_EXPAND_SYMLINKS`: true, false, none

The location of some executables used by the execution modes can be enforced with
the environment variables described below together with the default behavior.
A value of `KOOKER` will force the usage of the executables provided by the
kooker installation.

A full pathname can be used to force selection of a specific executable (or library)
from the host or from the kooker installation.

* `KOOKER_USE_PROOT_EXECUTABLE`: path to proot, default is proot from kooker.
* `KOOKER_USE_RUNC_EXECUTABLE`: path to runc, default is search the host and
  if not found use runc from kooker.
* `KOOKER_USE_SINGULARITY_EXECUTABLE`: path to singularity, default is search
  the host.
* `KOOKER_FAKECHROOT_SO`: path to a fakechroot library, default is search
  in kooker under `$HOME/.kooker/lib`.
* `KOOKER_DEFAULT_EXECUTION_MODE`: default execution mode can be P1, P2, F1,
  S1, R1, R2 or R3.

Several executables and libraries are shipped with kooker. For instance
the executable for the Rn modes can be selected to be either `runc` or
`crun`. This can be accomplished by setting `KOOKER_USE_RUNC_EXECUTABLE`
to the path of the desired executable. If `runsc` is available in the
host it can also be selected in this manner.

```
# Forcing the use of crun instead of runc
export KOOKER_USE_RUNC_EXECUTABLE=$HOME/.kooker/bin/crun-x86_64
export KOOKER_DEFAULT_EXECUTION_MODE=R1
kooker run <mycontainerid>
```

## 6. External tools and libraries

### 6.1. Source code repositories

kooker uses external tools and libraries to execute the created containers.
The source code for the kooker tools and libraries is taken from several repositories.
The **F** modes need heavily modified Fakechroot libraries and also a modified Patchelf
both specifically improved to work with kooker. The Fakechroot for musl is a port
of the Fakechroot library for the musl libc performed by the kooker development team.
The **P** modes need a modified PRoot that includes fixes and enhancements to work with
kooker. The **R** modes use the original runc and crun software with small changes for
static compilation. The following table highlights the repositories used by kooker
containing the modified source code and the original repositories.

| Mode  | Engine           | Repository used by kooker                                 | Original repository
|-------|:-----------------|:-----------------------------------------------------------|:-----------------------------------------
| **P** | PRoot            | <https://github.com/jorge-lip/proot-kooker>               | <https://github.com/proot-me/proot>
| **F** | Fakechroot glibc | <https://github.com/jorge-lip/libfakechroot-glibc-kooker> | <https://github.com/dex4er/fakechroot>
| **F** | Fakechroot musl  | <https://github.com/jorge-lip/libfakechroot-musl-kooker>  | <https://github.com/dex4er/fakechroot>
| **F** | Patchelf         | <https://github.com/jorge-lip/patchelf-kooker>            | <https://github.com/NixOS/patchelf>
| **R** | runc             | THE ORIGINAL REPOSITORY IS USED                            | <https://github.com/opencontainers/runc>
| **R** | crun             | THE ORIGINAL REPOSITORY IS USED                            | <https://github.com/containers/crun>

### 6.2. Software Licenses

Redistribution, commercial use and code changes must regard all licenses shipped with kooker.
These include the [kooker license](https://github.com/indigo-dc/kooker/blob/master/LICENSE)
and the individual licenses of the external tools and libraries packaged for use with kooker.

| Mode  | Engine           | License
|-------|:-----------------|:----------------------------------------------------------------------------
| **P** | PRoot            | [GPL v2](https://github.com/jorge-lip/proot-kooker/blob/master/COPYING)
| **F** | Fakechroot glibc | [LGPL v2.1](https://github.com/jorge-lip/libfakechroot-glibc-kooker/blob/master/LICENSE)
| **F** | Fakechroot musl  | [LGPL v2.1](https://github.com/jorge-lip/libfakechroot-musl-kooker/blob/master/LICENSE)
| **F** | Patchelf         | [GPL v3](https://github.com/jorge-lip/patchelf-kooker/blob/master/COPYING)
| **R** | runc             | [Apache v2.0](https://github.com/opencontainers/runc/blob/master/LICENSE)
| **R** | crun             | [GPL v2](https://github.com/containers/crun/blob/master/COPYING)

### 6.3. Binaries

As mentioned in the previous sections the compiled binaries can be installed
with `kooker install`. Optionally they can be downloaded from the repository
containing the binary builds at: <https://github.com/jorge-lip/kooker-builds>

The executables are provided statically compiled for use across systems.
The shared libraries that support the **F** modes need to match the libc
within the container and are provided for several Linux distributions.
See `$HOME/.kooker/lib` for the supported distributions and corresponding
versions. The tools are also delivered for several architectures.

| Mode  | Supported architecture                       |
|-------|:---------------------------------------------|
| **P** | x86_64, i386, aarch64 and arm                |
| **F** | x86_64, aarch64, ppc64le                     |
| **R** | x86_64  aarch64                              |
| **S** | uses the binaries present in the host system |

### 6.3. Compiling

kooker already provides executables and libraries for the engines. These
are statically compiled to be used across different Linux distributions.
In some cases these executables may not work and may require recompilation.
Use the repositories in section 6.2 if you which to compile the executables
or libraries. Notice that the git repositories that are specific of kooker
have branches or tags like `KOOKER-x` where `x` is a number. Use the branch
or tag with the highest number.

A notable case are the fakechroot libraries used in the Fn modes that need
to match the libc in the container. This means that a libfakechroot.so must
be produced for each different distribution release and intended architecture.
Two implementations of the `libc` are supported `glibc` and `musl`, choose
the one that matches the distribution inside the container. Once compiled the
selection of the library can be forced by setting the environment variable
`KOOKER_FAKECHROOT_SO`.

```
kooker setup --execmode=F3 <mycontainerid>
KOOKER_FAKECHROOT_SO=$HOME/mylibfakechroot.so  kooker run <mycontainerid>
```

The latest binary tarball can be produced from the source code using:

```bash
git clone -b devel3 https://github.com/indigo-dc/kooker
cd kooker/utils
./build_tarball.sh
```

## 7. Central installation

kooker can be installed and made available system wide from a central location
such as a shared read-only directory tree or file-system. The following guidelines
should be followed when installing kooker in a central shared location or in a
read only file system.

### 7.1. Install executables and libraries centrally

The executables and libraries can be installed with any of the methods described
in section 2 of this manual. The directory tree should contain the following
subdirectories: `bin`,  `containers`,  `layers`,  `lib`,  `repos`. For the
binaries and libraries the only directories required are `bin` and `lib`.

The kooker tool should be installed as shown in section 2.1:

```bash
cd /sw
wget https://github.com/indigo-dc/kooker/releases/download/1.3.17/kooker-1.3.17.tar.gz
tar zxvf kooker-1.3.17.tar.gz
```

Directing users to the central kooker installation can be done using the
environment variables described in section 5, or through the configuration files
described in section 6. The recommended approach is to set environment
variables at the user level as in the example where the assumed central location
will be under `/sw/kooker`:

```bash
export KOOKER_BIN=/sw/kooker/bin
export KOOKER_LIB=/sw/kooker/lib
export PATH=$PATH:$KOOKER_BIN:/sw/kooker
```

Note that the command `kooker` will be in `/sw/kooker` with all the python
directory structure, while `/sw/kooker/bin` has all execution engines.

Make sure that the file protections are adequate namely that the files are
not modifiable by others.

### 7.2. Images and layers in central installations

The repository of pulled images can also be placed in a different location
than the user home directory `$HOME/.kooker`. Notice that if the target
location is not writable then the users will be unable to pull new images,
which may be fine if these images are managed centrally by someone else.
Make sure that the file protections are adequate to the intended purpose.

From the images in the common location the users can then create containers
whose content will be placed in the user home directory under `$HOME/.kooker`.
This can be accomplished by redirecting the directories `layers` and  `repos`
to a common location. The users will need to set the following environment
variables. Therefore assuming that the common location will be `/sw/kooker`:

```bash
export KOOKER_REPOS=/sw/kooker/repos
export KOOKER_LAYERS=/sw/kooker/layers
```

### 7.3. Containers in central installations

If a container is extracted to the common location, it is possible to
point kooker to execute the container from that location. Making
kooker pointing at different `containers` directory such as for example
`/sw/kooker/containers` can be accomplished with:

```bash
export KOOKER_CONTAINERS=/sw/kooker/containers
```

Assuming that the container is to be created under `/sw/kooker/containers`
it can be extracted with:

```bash
export KOOKER_CONTAINERS=/sw/kooker/containers
kooker --allow-root pull  centos:centos7
kooker --allow-root create  --name=myContainerId  centos:centos7
kooker --allow-root run  -v /tmp myContainerId
```

Notice the `--allow-root` should only be used when running
from the root user. However depending on the execution mode and several other
factors the limitations described in the next sections apply.

#### 7.3.1. Selection of execution mode for central installations

The selection of the execution mode requires writing in the `containers`
directory, therefore if the container is in a read-only location the
execution mode cannot be changed. If a container is to be executed in a mode
other than the default then this must be set in advance. This must be done
by someone with write access. A table summarizing the execution modes
and their implications:

|Mode| Engine      | Execution from readonly location
|----|:------------|:------------------------------------------
| P1 | PRoot       | OK
| P2 | PRoot       | OK
| F1 | Fakechroot  | OK
| F2 | Fakechroot  | OK
| F3 | Fakechroot  | OK see restrictions in section 7.3.1.2.
| F4 | Fakechroot  | NOT SUPPORTED REQUIRES WRITE ACCESS
| R1 | runc / crun | OK requires kooker version above v1.1.7
| R2 | runc / crun | OK see restrictions in section 7.3.1.3.
| R3 | runc / crun | OK see restrictions in section 7.3.1.3.
| S1 | Singularity | OK

Changing the execution mode can be accomplished with the following kooker
command where `<MODE>` is one of the supported modes in column one.

```bash
kooker --allow-root setup --execmode=<MODE> myContainerId
```

Notice the `--allow-root` should only be used when running
from the root user.

If the same container is to be provided for execution using more
than one execution mode (e.g. to be executed with P1 and F3), then
make copies of the initial container and setup each one of them with
the intended mode. The command `kooker clone` can be used to create
copies of existing containers.

##### 7.3.1.1. Mode F4 is not supported

The mode F4 is not suitable for readonly containers as it is meant to
support the dynamic creation of new executables and libraries inside of
the container, which cannot happen if the container is readonly. Use the
mode F3 instead of F4.

##### 7.3.1.2. Mode F3 restrictions

The F3 mode (and also F4) perform changes to the container executables
and libraries, in particular they change the pathnames in ELF headers
making them pointing at the container location. This means that the
pathname to the container must be always the same across all the
hosts that may share the common location. Therefore if the original
location pathname is `/sw/kooker/containers` then all hosts must
also mount it at the same exact path `/sw/kooker/containers`.

##### 7.3.1.3. Modes R1, R2 and R3 general restrictions

These modes make use of runc or crun and require that user namespaces
are enabled in the kernel. Older distributions may either not have
support for namespaces (e.g. CentOS 6) or may have the support for
user namespaces disabled at the system level (e.g. CentOS 7). More
recent releases of Linux distributions do have support for user
namespaces (e.g. CentOS 8 and CentOS 9).

For Centos 7 there are steps that system administrators may perform
to enable user namespaces, such as:

```bash
sudo echo "user.max_user_namespaces=10000" >> /etc/sysctl.conf
```

##### 7.3.1.4. Modes R2 and R3 specific restrictions

Central installation from readonly location using any of the R modes
requires kooker above v1.1.7.
These modes require the creation of a mount point inside the container
that is transparently created when the container is first executed,
therefore (as recommended for all other modes) the container
must be executed once by someone with write access prior to making it
available to the users. Furthermore these execution modes are nested
they use P1 or P2 inside the R engine, the Pn modes require a tmp
directory that is writable. Therefore it is recommended to mount the
host `/tmp` in the container `/tmp` like this:

```bash
kooker --allow-root run  -v /tmp myContainerId
```

Or alternatively:

```bash
export PROOT_TMP_DIR=/<path-to-host-writable-directory>
kooker --allow-root run  -v /<path-to-host-writable-directory>  myContainerId
```

Notice the `--allow-root` should only be used when running from the root user.

#### 7.3.2. Mount directories and files in central installations

Making host files and directories visible inside the container requires
creating the corresponding mount points. The creation of mount-points
requires write access to the container. Therefore if a container is in
a read-only location these files and directories must be created in
advance.

Notice that some default mount points are required and automatically
created by kooker itself, therefore the container should be executed
by the administrator to ensure that the required files and directories
are created. Furthermore if additional mount points are required to
access data or other user files from the host, such mount points
must also be created by the administrator by executing the container
with the adequate volume pathnames. The example shows how to setup
the default mount points and in addition create a new mount point
named `/data`.

```bash
kooker --allow-root run -v /home:/data  myContainerId
```

Notice the `--allow-root` should only be used when running
from the root user.

Notice that once `/data` is setup the end users can mount other
directories in `/data` at runtime, meaning that users are not
restricted to mount only the `/home` directory as the mapping
is defined at run time.

#### 7.3.3. Protection of container files and directories

For the container to be executed by other users the files and
directories within the container must be readable. When kooker
is installed in the user home directory all files belong to
the user and are therefore readable by him. If a common location
is shared by several users the file protections will likely
need to be adjusted. Consider carefully your security policies
and requirements when changing the file protections.

The following example assumes making all files readable to
anyone and making all files (and directories) that have the
executable bit to be also *executable* by anyone.

```bash
export mycdir=$(kooker --allow-root inspect -p myContainerId)
chmod -R uog+r $mycdir
find $mycdir -executable -exec chmod oug+x {} \;
```

Notice the `--allow-root` should only be used when running
from the root user.

### 7.4. Using a common directory for executables and containers

If the common directory is used both for executables and containers
then the following environment variables can be used:

```bash
export KOOKER_DIR=/sw/kooker
export PATH=$PATH:$KOOKER_DIR:$KOOKER_DIR/bin
```

## 8. Uninstall

kooker does not provide an uninstall command. kooker can be uninstalled
by simply removing the created files and directories. The recommended
approach is as follows:

1. Fix permissions for all created containers
   `for id in $(kooker ps | cut -f1 -d" " | grep -v CONTAINER); do kooker setup --fixperm $id; done`
2. Remove all created containers
   `for id in $(kooker ps | cut -f1 -d" " | grep -v CONTAINER); do kooker rm -f $id; done`
3. Remove the *kooker directory tree* usually under `$HOME/.kooker`
   `cd $HOME ; rm -Rf .kooker`
4. Remove the kooker Python code

The *kooker directory tree* contains the external executables, libraries,
documentation, container images and container file system trees. By removing
it all created containers will be also removed. Changing the file permissions
might be required prior to deletion especially for the container file system
trees in the `containers` subdirectory.

## 9. Quality assurance

The kooker software quality assurance follows the Common Software
Quality Assurance Baseline Criteria for Research Projects
DOI: <http://hdl.handle.net/10261/160086.> available at
<https://indigo-dc.github.io/sqa-baseline/>.

kooker uses the Jenkins Pipeline Library
<https://github.com/indigo-dc/jenkins-pipeline-library>
to implement Jenkins CI/CD pipelines for quality assurance.

### 9.1. Functional and integration tests

High level functional and integration tests used for quality assurance are available
in <https://github.com/indigo-dc/kooker/tree/master/utils>.
These tests are also suitable to be executed by end-users to verify the installation.
After cloning the kooker repository with `git` the `bash` scripts
can be executed using:

```bash
cd utils
./kooker_test.sh
./kooker_test-run.sh
```

If the `.kooker` directory already exists these tests will not execute as they require
a clean environment. In this case proceed as follows:

1. rename the directory `$HOME/.kooker`, as in `mv $HOME/.kooker $HOME/.kooker.ORIG`
2. execute the tests
3. remove the `$HOME/.kooker` created by the tests
4. restore the original `.kooker` directory as in `mv $HOME/.kooker.ORIG $HOME/.kooker`

### 9.2. Unit and security tests

The unit tests used in the software quality assurance pipelines are available at
<https://github.com/indigo-dc/kooker/tree/master/tests/unit>.
The tests can be executed after creating a virtualenv and installing the development
requirements in [requirements-dev.txt](https://github.com/indigo-dc/kooker/blob/master/requirements-dev.txt)
These tests are meant to be executed by the automated quality assurance pipelines.

```bash
virtualenv -p python3 ud3
source ud3/bin/activate
git clone https://github.com/indigo-dc/kooker.git
cd kooker
pip install -r requirements-dev.txt
```

The unit tests coverage can be executed using:

```bash
nosetests -v --with-coverage --cover-package=kooker tests/unit
```

Other tests configured in `tox.ini`, can be executed as well, such as linting
(code style checking) and static security tests:

```bash
pylint --rcfile=pylintrc --disable=R,C kooker
bandit -r kooker -f html -o bandit.html
```
