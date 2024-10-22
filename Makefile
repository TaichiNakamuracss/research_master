.PHONY: clean clean-model clean-pyc docs help init-docker create-container start-container jupyter test lint profile clean clean-data clean-docker clean-container clean-image
.DEFAULT_GOAL := help

###########################################################################################################
## SCRIPTS
###########################################################################################################

define PRINT_HELP_PYSCRIPT
import os, re, sys

if os.environ['TARGET']:
    target = os.environ['TARGET']
    is_in_target = False
    for line in sys.stdin:
        match = re.match(r'^(?P<target>{}):(?P<dependencies>.*)?## (?P<description>.*)$$'.format(target).format(target), line)
        if match:
            print("target: %-20s" % (match.group("target")))
            if "dependencies" in match.groupdict().keys():
                print("dependencies: %-20s" % (match.group("dependencies")))
            if "description" in match.groupdict().keys():
                print("description: %-20s" % (match.group("description")))
            is_in_target = True
        elif is_in_target == True:
            match = re.match(r'^\t(.+)', line)
            if match:
                command = match.groups()
                print("command: %s" % (command))
            else:
                is_in_target = False
else:
    for line in sys.stdin:
        match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
        if match:
            target, help = match.groups()
            print("%-20s %s" % (target, help))
endef

define START_DOCKER_CONTAINER
if [ `$(DOCKER) inspect -f {{.State.Running}} $(CONTAINER_NAME)` = "false" ] ; then
        $(DOCKER) start $(CONTAINER_NAME)
fi
endef

###########################################################################################################
## VARIABLES
###########################################################################################################

export DOCKER=docker
export TARGET=
export PWD=`pwd`
export PYTHONPATH=$PYTHONPATH:$(pwd)
export PRINT_HELP_PYSCRIPT
export START_DOCKER_CONTAINER
export PROJECT_NAME=bayesian_public_goods_game
export IMAGE_NAME=$(PROJECT_NAME)-image
export DOCKERFILE=docker/Dockerfile
export OTREE_HOST_PORT=8001
export OTREE_CONTAINER_PORT=8001
export CONTAINER_NAME=$(PROJECT_NAME)-container
export JUPYTER_HOST_PORT=8888
export JUPYTER_CONTAINER_PORT=8888
export PYTHON=poetry run python
export PYSEN=poetry run pysen
export PYTEST=poetry run pytest

###########################################################################################################
## ADD TARGETS SPECIFIC TO "Bayesian_public_goods_game"
###########################################################################################################

run: ## run otree
	cd experiments && poetry run otree prodserver $(OTREE_HOST_PORT)

###########################################################################################################
## GENERAL TARGETS
###########################################################################################################

help: ## show this message
	@$(PYTHON) -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

init-docker: ## initialize docker image
	$(DOCKER) build -t $(IMAGE_NAME) -f $(DOCKERFILE) .

create-container: ## create docker container
	$(DOCKER) run -it -v $(PWD):/work -p $(OTREE_HOST_PORT):$(OTREE_CONTAINER_PORT) --name $(CONTAINER_NAME) $(IMAGE_NAME)

create-container-no-mount: ## create docker container no mount
	$(DOCKER) run -it -p $(OTREE_HOST_PORT):$(OTREE_CONTAINER_PORT) --name $(CONTAINER_NAME) $(IMAGE_NAME)

start-container: ## start docker container
	@echo "$$START_DOCKER_CONTAINER" | $(SHELL)
	@echo "Launched $(CONTAINER_NAME)..."
	$(DOCKER) attach $(CONTAINER_NAME)

jupyter: ## start Jupyter Notebook server
	$(POETRY) jupyter-notebook --ip=0.0.0.0 --port=${JUPYTER_CONTAINER_PORT}

test: ## run test cases in tests directory
	$(PYTEST)

lint: ## check style with pysen
	$(PYSEN) run lint

format:
	$(PYSEN) run format
