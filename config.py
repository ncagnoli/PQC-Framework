# --- General Settings ---
# Set to True to see detailed commands and outputs from the scripts.
DEBUG_MODE = True
# The number of times the client-server test iteration should run.
ITERATIONS = 1500
# Directory where the resulting CSV files will be stored.
RESULTS_DIR = "Results"
# The file used by the client to signal the server to stop.
SIGNAL_FILE = "/tmp/stop_server_perf"

# --- Server Settings (`server_perf.py`) ---
# The server binary to be benchmarked.
SERVER_BINARY = "/usr/sbin/sshd"
# Arguments for the server binary. The config file path is referenced here.
SERVER_CONFIG_FILE = "/root/experiment/sshd_config/sshd_config_t_rsa_2048"
SERVER_ARGS = ["-D", "-e", "-p", "2222", "-f", SERVER_CONFIG_FILE]
# The port to check for availability before starting the server. 'None' to disable.
PORT_TO_CHECK = 2222

# --- Client Settings (`client_perf.py`) ---
# These settings are used by the client to connect to the server for signaling.
# In the current direct-signal workflow, these are only used if the main
# client command is changed to not include the signaling.
# The client configurations
SIGNAL_SSH_USER = "testuser"
SIGNAL_SSH_HOST = "10.10.10.242"
SIGNAL_SSH_PORT = PORT_TO_CHECK
SIGNAL_SSH_KEY = "/root/experiment/client_keys/id_rsa_2048"

SIGNAL_HOST = f"{SIGNAL_SSH_USER}@{SIGNAL_SSH_HOST}"

# The command to be executed on the remote server, which also acts as the signal.
REMOTE_COMMAND = f"touch {SIGNAL_FILE}"
# The client binary that will be measured by perf.
CLIENT_COMMAND = "ssh"
# Algorithms to be used on KEX process
ALGORITHMS = "curve25519-sha256@libssh.org"
# Command line for KEX
KEX_ALGORITHMS = f"KexAlgorithms={ALGORITHMS}"
# Arguments for the client binary.
CLIENT_ARGS = [
    "-p", str(PORT_TO_CHECK), "-i", SIGNAL_SSH_KEY, "-o", "BatchMode=yes", "-o", "ForwardX11=no",
    "-o", KEX_ALGORITHMS, SIGNAL_HOST, REMOTE_COMMAND
]
# A friendly name for the test, used in the output filename.
TEST_NAME = "Test-RSA-2048"

# --- Graph Settings (`graph.py` and `dual_axis_graph.py`) ---
# Default output filename for the single-axis plot.
DEFAULT_SINGLE_AXIS_PLOT_OUTPUT = "performance_plot.html"
# Default output filename for the dual-axis plot.
DEFAULT_DUAL_AXIS_PLOT_OUTPUT = "dual_axis_plot.html"
# Plot dimensions
PLOT_WIDTH = 1200
PLOT_HEIGHT = 800
# Background color for the plot
PLOT_BG_COLOR = "#f3f3f3"
# Font sizes
TITLE_FONT_SIZE = "18pt"
AXIS_LABEL_FONT_SIZE = "12pt"
MAJOR_LABEL_FONT_SIZE = "10pt"
