from datetime import datetime
import re
from typing import Any, Optional

def parse_years_to_float(years_value: Any) -> Optional[float]:
        """Parses numeric values, date ranges, and strings into a float."""
        if years_value is None: return None
        if isinstance(years_value, (int, float)): return float(years_value)
        if not isinstance(years_value, str): return None

        try:
            return float(years_value)
        except ValueError:
            pass

        # Regex for "Sep 2020 - Present" or "2019 - 2023"
        date_pattern = r'(\d{4})\s*-\s*(\d{4}|Present|Now)'
        match = re.search(date_pattern, years_value, re.IGNORECASE)
        if match:
            start_year = int(match.group(1))
            end_str = match.group(2).lower()
            end_year = datetime.now().year if end_str in ('present', 'now') else int(end_str)
            return float(max(0, end_year - start_year))

        return None