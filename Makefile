sub-init:
	echo "SUB_ID=<input subscription_id>\nEMAIL_ID=<your email id>" > sub.env

infra:
	./setup/create-resources.sh

venv_setup:
	rm -rf .venv
	python3.11 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r ./requirements.txt

branch=$(shell git symbolic-ref --short HEAD)
now=$(shell date '+%F_%H:%M:%S' )
git-push:
	git add . && git commit -m "Changes as of $(now)" && git push -u origin $(branch)
