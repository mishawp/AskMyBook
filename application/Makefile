.PHONY: fix-perms

# Выставить владельца папки app (uid=999 — такой же, как nonroot в Dockerfile)
fix-perms:
	sudo chown -R 999:$(shell id -g) ./app
	sudo chmod -R g+rwX ./app

