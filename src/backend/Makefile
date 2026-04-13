.PHONY: run test test-integration test-eval lint typecheck

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/unit/ -v --tb=short --cov=app --cov-report=term-missing

test-integration:
	pytest tests/integration/ -v --tb=short

test-eval:
	DEMO_MODE=true python tests/eval/run_eval.py

lint:
	ruff check .

typecheck:
	mypy app/
