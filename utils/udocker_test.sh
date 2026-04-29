#!/bin/bash

# ##################################################################
#
# kooker high level testing
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ##################################################################

# Codes
RED='\033[1;31m'
GREEN='\033[1;32m'
BLUE='\033[1;34m'
PURPLE='\033[1;36m'
NC='\033[0m'
ASSERT_STR="${BLUE}Assert:${NC}"
RUNNING_STR="${BLUE}Running:${NC}"
OK_STR="${GREEN}[OK]${NC}"
FAIL_STR="${RED}[FAIL]${NC}"
THIS_SCRIPT_NAME=$( basename "$0" )

# Variables for the tests
declare -a FAILED_TESTS
DEFAULT_UDIR=$HOME/.kooker-tests
TEST_UDIR=$HOME/.kooker-test-h45y7k9X
TAR_IMAGE="centos7.tar"
TAR_CONT="centos7-cont.tar"
TAR_IMAGE_URL="https://download.a.incd.pt/kooker_test/${TAR_IMAGE}"
TAR_CONT_URL="https://download.a.incd.pt/kooker_test/${TAR_CONT}"
DOCKER_IMG="ubuntu:22.04"
CONT="ubuntu"
export KOOKER_DIR=${DEFAULT_UDIR}

if [ -n "$1" ]
then
  KOOKER_CMD="$1"
else
  KOOKER_CMD=$(type -p kooker)
fi

if [ ! -x "$KOOKER_CMD" ]
then
  echo "ERROR kooker file not executable: $KOOKER_CMD"
  exit 1
fi

if [ -n "$2" ]
then
  PYTHON_CMD="$2"
fi

if [ -n "$PYTHON_CMD" -a ! -x "$PYTHON_CMD" ]
then
  echo "ERROR python interpreter not executable: $PYTHON_CMD"
  exit 1
fi

function print_ok
{
  printf "${OK_STR}"
}

function print_fail
{
  printf "${FAIL_STR}"
}

function clean
{
  if [ -d ${DEFAULT_UDIR} ]
  then
    echo "ERROR test directory exists, remove first: ${DEFAULT_UDIR}"
    exit 1
  fi
}

function result
{
  echo " "
  if [ $return == 0 ]; then
      print_ok; echo "    $STRING"
  else
      print_fail; echo "    $STRING"
      FAILED_TESTS+=("$STRING")
  fi
  echo "\____________________________________________________________________________________________________________________________________/"
  echo ""
  echo " ____________________________________________________________________________________________________________________________________ "
  echo "/                                                                                                                                    \ "
}

function result_inv
{
  echo " "
  if [ $return == 1 ]; then
      print_ok; echo "    $STRING"
  else
      print_fail; echo "    $STRING"
      FAILED_TESTS+=("$STRING")
  fi
  echo "\____________________________________________________________________________________________________________________________________/"
  echo ""
  echo " ____________________________________________________________________________________________________________________________________ "
  echo "/                                                                                                                                    \ "
}

function kooker
{
  $PYTHON_CMD $KOOKER_CMD $*
}

echo "================================================="
echo "* This script tests all kooker CLI and options *"
echo "* except the run command and vol. mount options *"
echo "================================================="

STRING="T001: kooker install"
clean
kooker install && ls ${DEFAULT_UDIR}/bin/proot-x86_64; return=$?
result

STRING="T002: kooker install --force"
kooker install --force && \
    ls ${DEFAULT_UDIR}/bin/proot-x86_64 >/dev/null 2>&1; return=$?
result

STRING="T003: kooker (with no options)"
kooker ; return=$?
result

STRING="T004: kooker help"
kooker help >/dev/null 2>&1 ; return=$?
result

STRING="T005: kooker -h"
kooker -h >/dev/null 2>&1 ; return=$?
result

STRING="T006: kooker showconf"
kooker showconf; return=$?
result

STRING="T007: kooker version"
kooker version; return=$?
result

STRING="T008: kooker -D version"
kooker -D version; return=$?
result

STRING="T009: kooker --quiet version"
kooker --quiet version; return=$?
result

STRING="T010: kooker -q version"
kooker -q version; return=$?
result

STRING="T011: kooker --debug version"
kooker --debug version; return=$?
result

STRING="T012: kooker -V"
kooker -V >/dev/null 2>&1 ; return=$?
result

STRING="T013: kooker --version"
kooker --version >/dev/null 2>&1 ; return=$?
result

STRING="T014: kooker search -a"
kooker search -a gromacs | grep ^gromacs; return=$?
result

STRING="T015: kooker pull ${DOCKER_IMG}"
kooker pull ${DOCKER_IMG}; return=$?
result

STRING="T016: kooker --insecure pull ${DOCKER_IMG}"
kooker --insecure pull ${DOCKER_IMG}; return=$?
result

STRING="T017: kooker verify ${DOCKER_IMG}"
kooker verify ${DOCKER_IMG}; return=$?
result
## TODO: Add test to check layers after pull

STRING="T018: kooker images"
kooker images; return=$?
result

STRING="T019: kooker inspect (image)"
kooker inspect ${DOCKER_IMG}; return=$?
result

STRING="T020: kooker -q create ${DOCKER_IMG}"
CONT_ID=`kooker -q create ${DOCKER_IMG}`; return=$?
result

STRING="T021: kooker create --name=${CONT} ${DOCKER_IMG}"
CONT_ID_NAME=`kooker create --name=${CONT} ${DOCKER_IMG}`; return=$?
result

STRING="T022: kooker ps"
kooker ps; return=$?
result

STRING="T023: kooker name ${CONT_ID}"
kooker name ${CONT_ID} conti; return=$?
kooker ps |grep conti
result

STRING="T024: kooker rmname"
kooker rmname conti; return=$?
kooker ps |grep ${CONT_ID}
result

STRING="T025: kooker inspect (container ${CONT_ID})"
kooker inspect ${CONT_ID}; return=$?
result

STRING="T026: kooker clone --name=myclone ${CONT_ID}"
kooker clone --name=myclone ${CONT_ID}; return=$?
result

STRING="T027: kooker export -o myexportcont.tar ${CONT_ID}"
chmod -R u+x ${DEFAULT_UDIR}/containers/${CONT_ID}/ROOT
kooker export -o myexportcont.tar ${CONT_ID}; return=$?
result

STRING="T028: kooker rm ${CONT_ID}"
kooker rm ${CONT_ID}; return=$?
result

STRING="T029: kooker setup ${CONT}"
kooker setup ${CONT}; return=$?
result

rm -Rf "${TEST_UDIR}" > /dev/null 2>&1

STRING="T030: kooker mkrepo ${TEST_UDIR}"
kooker mkrepo ${TEST_UDIR}; return=$?
result

STRING="T031: kooker --repo=${TEST_UDIR} pull ${DOCKER_IMG}"
kooker --repo=${TEST_UDIR} pull ${DOCKER_IMG}; return=$?
result

STRING="T032: kooker --repo=${TEST_UDIR} verify ${DOCKER_IMG}"
kooker --repo=${TEST_UDIR} verify ${DOCKER_IMG}; return=$?
result

STRING="T033: KOOKER_DIR=${TEST_UDIR} kooker verify ${DOCKER_IMG}"
KOOKER_DIR=${TEST_UDIR} kooker verify ${DOCKER_IMG}; return=$?
result

rm -f ${TAR_IMAGE} > /dev/null 2>&1
echo "Download a docker tar img file ${TAR_IMAGE_URL}"
wget --no-check-certificate ${TAR_IMAGE_URL}
echo "|______________________________________________________________________________|"

STRING="T034: kooker load -i ${TAR_IMAGE}"
kooker load -i ${TAR_IMAGE}; return=$?
result

STRING="T035: kooker protect ${CONT} (container)"
kooker protect ${CONT}; return=$?
result

STRING="T036: kooker rm ${CONT} (try to remove protected container)"
kooker rm ${CONT}; return=$?
result_inv

STRING="T037: kooker unprotect ${CONT} (container)"
kooker unprotect ${CONT}; return=$?
result

STRING="T038: kooker rm ${CONT} (try to remove unprotected container)"
kooker rm ${CONT}; return=$?
result

rm -f ${TAR_CONT} > /dev/null 2>&1
echo "Download a docker tar container file ${TAR_CONT_URL}"
wget --no-check-certificate ${TAR_CONT_URL}
echo "|______________________________________________________________________________|"

STRING="T039: kooker import ${TAR_CONT} mycentos1:latest"
kooker import ${TAR_CONT} mycentos1:latest; return=$?
result

STRING="T040: kooker import --tocontainer --name=mycont ${TAR_CONT}"
kooker import --tocontainer --name=mycont ${TAR_CONT}; return=$?
result

STRING="T041: kooker import --clone --name=clone_cont ${TAR_CONT}"
kooker import --clone --name=clone_cont ${TAR_CONT}; return=$?
result

STRING="T042: kooker rmi ${DOCKER_IMG}"
kooker rmi ${DOCKER_IMG}; return=$?
result

STRING="T043: kooker ps -m"
kooker ps -m; return=$?
result

STRING="T044: kooker ps -s -m"
kooker ps -s -m; return=$?
result

STRING="T045: kooker images -l"
kooker images -l; return=$?
result

STRING="T046: kooker pull docker.io/python:3-slim <REGRESSION test for issue #359>"
kooker pull docker.io/python:3-slim; return=$?
result

STRING="T047: kooker create --name=py3slim docker.io/python:3-slim <REGRESSION test for issue #359>"
kooker create --name=py3slim docker.io/python:3-slim; return=$?
result

STRING="T048: kooker run py3slim python3 --version <REGRESSION test for issue #359>"
kooker run py3slim python3 --version; return=$?
result

STRING="T049: kooker pull public.ecr.aws/docker/library/redis <REGRESSION test for issue #168>"
kooker pull public.ecr.aws/docker/library/redis; return=$?
result

STRING="T050: kooker create --name=redis public.ecr.aws/docker/library/redis <REGRESSION test for issue #168>"
kooker create --name=redis public.ecr.aws/docker/library/redis; return=$?
result

STRING="T051: kooker run redis redis-server --version <REGRESSION test for issue #168>"
kooker run redis redis-server --version; return=$?
result

STRING="T052: kooker login --username=username --password=password"
kooker login --username=username --password=password; return=$?
result

STRING="T053: kooker logout -a"
kooker logout -a; return=$?
result

# Cleanup files containers and images used in the tests
echo "Clean up files containers and images used in the tests"
rm -rf myexportcont.tar "${TEST_UDIR}" "${TAR_IMAGE}" "${TAR_CONT}" > /dev/null 2>&1
kooker rm mycont
kooker rm clone_cont
kooker rm myclone
kooker rm py3slim
kooker rm redis
kooker rmi mycentos1
kooker rmi centos:7
kooker rmi docker.io/python:3-slim
kooker rmi public.ecr.aws/docker/library/redis
echo "|______________________________________________________________________________|"

# Report failed tests
if [ "${#FAILED_TESTS[*]}" -le 0 ]
then
    printf "${OK_STR}    All tests passed\n"
    exit 0
fi

printf "${FAIL_STR}    The following tests have failed:\n"
for (( i=0; i<${#FAILED_TESTS[@]}; i++ ))
do
    printf "${FAIL_STR}    ${FAILED_TESTS[$i]}\n"
done
exit 1
