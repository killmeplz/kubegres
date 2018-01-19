build:
	docker build -t postgres:test ./pg-client/
test:
	docker build -t dharbor.gs-labs.tv/kubegres/apiserv:test . 
	docker push dharbor.gs-labs.tv/kubegres/apiserv:test
	docker build -t dharbor.gs-labs.tv/kubegres/pgnode:test ./pg-client
	docker push dharbor.gs-labs.tv/kubegres/pgnode:test
