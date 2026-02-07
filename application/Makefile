.PHONY: fix-perms

# Выставить владельца папок app, ingestion и shared (uid=999 — такой же, как nonroot в Dockerfile)
fix-perms:
	sudo setfacl -R -m u:$(shell id -u):rwX,u:999:rwX,g:$(shell id -g):rwX ./app ./ingestion ./shared
	sudo setfacl -Rd -m u:$(shell id -u):rwX,u:999:rwX,g:$(shell id -g):rwX ./app ./ingestion ./shared
