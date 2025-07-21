import re

# The header row for the CSV file.
CSV_HEADERS = [
    "iteration", "cycles", "instructions", "cache-misses", "branch-misses",
    "page-faults", "context-switches", "cpu-migrations", "time_elapsed_s",
    "user_time_s", "sys_time_s"
]

def parse_perf_output(output, iteration):
    """
    Parses the stderr output from 'perf stat' to extract key metrics.

    Args:
        output (str): The stderr string from the perf command.
        iteration (int): The current iteration number to include in the results.

    Returns:
        dict: A dictionary containing the parsed metrics.
    """
    metrics = {key: 0 for key in CSV_HEADERS}
    metrics["iteration"] = iteration

    # Regex to find the value and the metric name on each line
    # Handles commas in numbers and various whitespace.
    perf_line_re = re.compile(r"^\s*([\d,.]+)\s+([a-zA-Z-]+)")

    for line in output.split('\n'):
        line = line.strip()
        match = perf_line_re.match(line)
        if not match:
            continue

        value_str = match.group(1).replace(',', '')
        key = match.group(2)

        try:
            value = float(value_str)
        except ValueError:
            continue

        if key in metrics:
            metrics[key] = value
        elif "seconds time elapsed" in line:
            metrics["time_elapsed_s"] = value
        elif "seconds user" in line:
            metrics["user_time_s"] = value
        elif "seconds sys" in line:
            metrics["sys_time_s"] = value

    return metrics
