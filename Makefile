infra:
	./setup/create-resources.sh

install:
	#conda create -n speech python=3.8 -y
	pip install python-dotenv
	pip install requests
	pip install azure-cognitiveservices-speech
