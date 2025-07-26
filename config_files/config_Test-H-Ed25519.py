# --- General Settings ---
DEBUG_MODE = True
ITERATIONS = 1001
RESULTS_DIR = "Results"
SIGNAL_FILE = "/tmp/stop_server_perf"

# --- PERF Settings ---
PERF_COMMAND = [
    "perf", "stat", "-e",
    "cycles,instructions,cache-misses,branch-misses,page-faults,context-switches,cpu-migrations"
]

# --- Server Settings ---
SERVER_BINARY = "/usr/sbin/sshd"
SERVER_CONFIG_FILE = "/root/experiment/sshd_config/sshd_config_h_ed25519"
SERVER_ARGS = ["-D", "-e", "-p", "2222", "-f", SERVER_CONFIG_FILE]
PORT_TO_CHECK = 2222

# --- Client Settings ---
CLIENT_BINARY = "/usr/bin/ssh"
CLIENT_SSH_USER = "testuser"
CLIENT_SSH_HOST = "10.10.10.242"
CLIENT_SSH_PORT = PORT_TO_CHECK
CLIENT_SSH_KEY = "/root/experiment/client_keys/id_ed25519_key"

REMOTE_COMMAND = f"touch {SIGNAL_FILE}"
KEY_TYPE = "ssh-ed25519"
KEY_ALGORITHMS = f"HostKeyAlgorithms={KEY_TYPE}"
PUBKEY_ALGORITHMS = f"PubkeyAcceptedAlgorithms={KEY_TYPE}"
ALGORITHMS = "sntrup761x25519-sha512@openssh.com"
KEX_ALGORITHMS = f"KexAlgorithms={ALGORITHMS}"
CLIENT_HOST = f"{CLIENT_SSH_USER}@{CLIENT_SSH_HOST}"
CLIENT_ARGS = [
    "-p", str(PORT_TO_CHECK),"-i", CLIENT_SSH_KEY, "-o", "BatchMode=yes", "-o", "ForwardX11=no",
    "-o", "StrictHostKeyChecking=no", "-o", KEY_ALGORITHMS, "-o", PUBKEY_ALGORITHMS, "-o", "UserKnownHostsFile=/dev/null", "-o", KEX_ALGORITHMS, f"{CLIENT_SSH_USER}@{CLIENT_SSH_HOST}",
    REMOTE_COMMAND
]

TEST_NAME = "Test-H-Ed25519"

# --- Graph Settings ---
DEFAULT_SINGLE_AXIS_PLOT_OUTPUT = "performance_plot.html"
DEFAULT_DUAL_AXIS_PLOT_OUTPUT = "dual_axis_plot.html"
PLOT_WIDTH = 1200
PLOT_HEIGHT = 800
PLOT_BG_COLOR = "#f3f3f3"
TITLE_FONT_SIZE = "18pt"
AXIS_LABEL_FONT_SIZE = "12pt"
MAJOR_LABEL_FONT_SIZE = "10pt"
