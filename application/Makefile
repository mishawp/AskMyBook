.PHONY: fix-perms

# Выставить владельца папки app (uid=999 — такой же, как nonroot в Dockerfile)
fix-perms:
	sudo setfacl -R -m u:$(shell id -u):rwX,u:999:rwX,g:$(shell id -g):rwX ./app
	sudo setfacl -Rd -m u:$(shell id -u):rwX,u:999:rwX,g:$(shell id -g):rwX ./app
