The `TypeError` and `UnicodeDecodeError` in `dashboard.py` have been addressed.

The `subprocess.run` calls for "运行每日分析" and "AI策略优化" have been modified to:
1. Capture output as bytes (`capture_output=True`, `text=False`).
2. Manually decode `stdout` and `stderr` using `decode('utf-8', errors='replace')`. This ensures that even if the subprocess outputs non-UTF-8 characters, they will be replaced, preventing `UnicodeDecodeError` and ensuring `stdout`/`stderr` are always strings for concatenation, thus resolving the `TypeError`.
---

### Bug Fix: `TypeError: 'int' object is not iterable` in Dashboard

*   **Date:** 2025-11-20
*   **File Affected:** `dashboard.py`
*   **Bug Description:** The application would crash when viewing the "澳门分析" or "香港分析" pages. This was caused by the `render_analysis_results` function attempting to iterate over a dictionary item (`"分析期号"`) which contained a single integer value, not a list. This happened after the analysis scripts were modified to include the period number in their JSON output.
*   **Solution:** The `render_analysis_results` function in `dashboard.py` was updated. It now explicitly checks for the `"分析期号"` key. If found, it displays it as a title and then skips it during the main loop which renders grid items. This prevents the `TypeError` and also improves the UI by showing the user which period's analysis is being displayed. The rendering logic for special analysis results was also made more robust to handle different data structures.
---

### Bug Fix: `ValueError: Unknown format code 'f'` in Dashboard

*   **Date:** 2025-11-20
*   **File Affected:** `dashboard.py`
*   **Bug Description:** After a previous fix, the app still crashed when rendering the "特码推荐生肖" section. The analysis script was creating a pre-formatted string (e.g., "蛇 (分数: 12.50)"), but the dashboard was incorrectly trying to parse this string again and apply float formatting (`.2f`) to a substring, causing a `ValueError`.
*   **Solution:** The rendering logic for "特码推荐生肖" in `dashboard.py` was simplified. It now directly displays the pre-formatted string that it receives from the JSON analysis file, which resolves the formatting conflict and prevents the crash.