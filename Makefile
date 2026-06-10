# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: rvaz-da- <rvaz-da-@student.s19.be>         +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/10 12:29:32 by rvaz-da-          #+#    #+#              #
#    Updated: 2026/06/10 12:29:32 by rvaz-da-         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

PKG = -m src
VENV = .venv
PY = python
 
 install:
	uv python install 3.12
	uv sync
	@echo Virtual environment setup complete!

run:
	uv run $(PY) $(PKG)

debug:
	uv run $(PY) -m pdb $(PKG)

lint:
	uv run flake8 src --exclude=.venv
	uv run mypy src --ignore-missing-imports

lint-strict:
	uv run flake8 src --exclude=.venv
	uv run mypy --strict src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

clean:
	rm -rf src/__pycache__/
	rm -rf src/.mypy_cache/
	rm -rf src/.pytest_cache
	rm -rf llm_sdk/__pycache__/
	rm -rf llm_sdk/llm_sdk/__pycache__/
	find . -type f -name "*.pyc" -delete
	@echo Project cleanup complete!

fclean: clean
	rm -rf .venv/
	@echo Project reset complete

re: clean run

.PHONY: install run debug lint lint-strict clean fclean re