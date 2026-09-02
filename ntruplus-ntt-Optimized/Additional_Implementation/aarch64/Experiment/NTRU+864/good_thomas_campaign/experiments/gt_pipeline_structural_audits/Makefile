.PHONY: check report clean

check:
	python3 audit.py --check

report:
	python3 audit.py --write

clean:
	rm -f audit-results.json AUDIT_REPORT.md
