# Specialized File Types Guide

## Overview
Specialized file types serve unique purposes in development workflows, from academic documentation to task automation. This guide covers essential specialized file formats and their applications.

## File Types Reference

| **File Type** | **Core Files** | **Supporting Files** | **Purpose** |
|--------------|----------------|---------------------|------------|
| **LaTeX Documents** | `.tex`, `.bib` | `.cls`, `.sty` | Academic papers, mathematical documents |
| **Makefiles** | `Makefile`, `makefile` | `GNUmakefile` | Build automation, task running |
| **Regular Expressions** | `.regex`, `.re` | `.pattern` | Pattern matching, text validation |
| **Cron Files** | `crontab`, `.cron` | - | Scheduled task automation |
| **Log Files** | `.log`, `.txt` | `.out`, `.err` | Debugging, monitoring, auditing |

## Use Cases & Examples

### LaTeX Documents
**Best For:** Research papers, theses, mathematical documentation
```latex
% paper.tex - Academic paper template
\documentclass[12pt, a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath, amssymb, amsthm}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{algorithm}
\usepackage{algorithmic}
\usepackage{listings}
\usepackage{biblatex}

\addbibresource{references.bib}

\title{Machine Learning Approaches for Time Series Forecasting}
\author{John Doe\thanks{Department of Computer Science} \and Jane Smith}
\date{\today}

\newtheorem{theorem}{Theorem}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{definition}{Definition}

\begin{document}

\maketitle

\begin{abstract}
This paper presents a comprehensive analysis of machine learning techniques
for time series forecasting. We propose a novel hybrid approach combining
LSTM networks with attention mechanisms, achieving state-of-the-art results
on benchmark datasets.
\end{abstract}

\section{Introduction}
Time series forecasting is a fundamental problem in many domains
\cite{box2015time}. Recent advances in deep learning have shown promising
results \cite{hochreiter1997long}.

\section{Methodology}

\subsection{Problem Formulation}
Given a time series $\{x_t\}_{t=1}^T$, we aim to predict future values
$\hat{x}_{t+h}$ where $h$ is the forecast horizon.

\begin{definition}[Autoregressive Model]
An autoregressive model of order $p$, denoted $AR(p)$, is defined as:
\begin{equation}
x_t = c + \sum_{i=1}^{p} \phi_i x_{t-i} + \epsilon_t
\end{equation}
where $\phi_i$ are parameters and $\epsilon_t$ is white noise.
\end{definition}

\subsection{Proposed Architecture}
Our model combines LSTM layers with attention:

\begin{algorithm}
\caption{Attention-LSTM Forecasting}
\begin{algorithmic}[1]
\REQUIRE Time series $X = \{x_1, ..., x_T\}$
\ENSURE Forecast $\hat{x}_{T+1}$
\STATE $H \leftarrow \text{LSTM}(X)$
\STATE $\alpha \leftarrow \text{softmax}(W_a \cdot H)$
\STATE $c \leftarrow \sum_{i=1}^{T} \alpha_i h_i$
\STATE $\hat{x}_{T+1} \leftarrow W_o \cdot c + b_o$
\RETURN $\hat{x}_{T+1}$
\end{algorithmic}
\end{algorithm}

\section{Experiments}

\begin{table}[h]
\centering
\begin{tabular}{|l|c|c|c|}
\hline
\textbf{Model} & \textbf{RMSE} & \textbf{MAE} & \textbf{MAPE} \\
\hline
ARIMA & 0.142 & 0.098 & 8.3\% \\
LSTM & 0.089 & 0.067 & 5.2\% \\
\textbf{Ours} & \textbf{0.072} & \textbf{0.054} & \textbf{4.1\%} \\
\hline
\end{tabular}
\caption{Performance comparison on test dataset}
\label{tab:results}
\end{table}

\section{Conclusion}
We demonstrated that attention mechanisms significantly improve LSTM
performance for time series forecasting.

\printbibliography

\end{document}
```

**BibTeX References:**
```bibtex
% references.bib
@book{box2015time,
  title={Time Series Analysis: Forecasting and Control},
  author={Box, George EP and Jenkins, Gwilym M and Reinsel, Gregory C},
  year={2015},
  publisher={John Wiley \& Sons}
}

@article{hochreiter1997long,
  title={Long short-term memory},
  author={Hochreiter, Sepp and Schmidhuber, J{\"u}rgen},
  journal={Neural computation},
  volume={9},
  number={8},
  pages={1735--1780},
  year={1997}
}
```
**Example Projects:** PhD theses, journal papers, conference proceedings

### Makefiles
**Best For:** Build automation, cross-platform task running
```makefile
# Makefile - Project build automation
.PHONY: all build test clean install docker help

# Variables
CC := gcc
CXX := g++
CFLAGS := -Wall -Wextra -O2
LDFLAGS := -lm -lpthread

SRC_DIR := src
BUILD_DIR := build
BIN_DIR := bin
TEST_DIR := tests

SOURCES := $(wildcard $(SRC_DIR)/*.c)
OBJECTS := $(SOURCES:$(SRC_DIR)/%.c=$(BUILD_DIR)/%.o)
EXECUTABLE := $(BIN_DIR)/myapp

# Default target
all: build

# Build the application
build: $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS) | $(BIN_DIR)
	@echo "Linking $@..."
	@$(CC) $(OBJECTS) -o $@ $(LDFLAGS)
	@echo "Build complete!"

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c | $(BUILD_DIR)
	@echo "Compiling $<..."
	@$(CC) $(CFLAGS) -c $< -o $@

# Create directories
$(BUILD_DIR) $(BIN_DIR):
	@mkdir -p $@

# Run tests
test: build
	@echo "Running tests..."
	@python -m pytest $(TEST_DIR) -v
	@./$(EXECUTABLE) --test

# Clean build artifacts
clean:
	@echo "Cleaning..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR)
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -delete

# Install dependencies
install:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt
	@npm install

# Docker operations
docker: docker-build docker-run

docker-build:
	@echo "Building Docker image..."
	@docker build -t myapp:latest .

docker-run:
	@echo "Running Docker container..."
	@docker run -d -p 8080:8080 --name myapp myapp:latest

docker-stop:
	@docker stop myapp && docker rm myapp

# Development server
dev:
	@echo "Starting development server..."
	@nodemon --watch $(SRC_DIR) --exec "make build && ./$(EXECUTABLE)"

# Production deployment
deploy: test
	@echo "Deploying to production..."
	@rsync -avz --exclude-from=.rsyncignore . user@server:/path/to/app
	@ssh user@server "cd /path/to/app && make install && make build"

# Database operations
db-migrate:
	@echo "Running database migrations..."
	@alembic upgrade head

db-rollback:
	@echo "Rolling back last migration..."
	@alembic downgrade -1

# Help target
help:
	@echo "Available targets:"
	@echo "  make build    - Build the application"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Clean build artifacts"
	@echo "  make install  - Install dependencies"
	@echo "  make docker   - Build and run Docker container"
	@echo "  make dev      - Start development server"
	@echo "  make deploy   - Deploy to production"
	@echo "  make help     - Show this help message"
```
**Example Projects:** C/C++ projects, multi-language builds, deployment automation

### Regular Expressions
**Best For:** Validation, text processing, pattern extraction
```javascript
// regex-patterns.js - Common regex patterns
const patterns = {
  // Email validation
  email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  
  // URL validation
  url: /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/,
  
  // Phone number (US format)
  phone: /^\+?1?\s*\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$/,
  
  // Credit card
  creditCard: /^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})$/,
  
  // IPv4 address
  ipv4: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
  
  // Password (min 8 chars, 1 upper, 1 lower, 1 number, 1 special)
  password: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
  
  // Username (alphanumeric, underscore, 3-16 chars)
  username: /^[a-zA-Z0-9_]{3,16}$/,
  
  // Hex color
  hexColor: /^#?([a-f0-9]{6}|[a-f0-9]{3})$/i,
  
  // Date (YYYY-MM-DD)
  date: /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/,
  
  // Time (HH:MM:SS)
  time: /^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$/
};

// Text extraction patterns
const extractors = {
  // Extract all URLs from text
  extractUrls: (text) => {
    const urlRegex = /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/gi;
    return text.match(urlRegex) || [];
  },
  
  // Extract hashtags
  extractHashtags: (text) => {
    const hashtagRegex = /#[a-zA-Z0-9_]+/g;
    return text.match(hashtagRegex) || [];
  },
  
  // Extract mentions
  extractMentions: (text) => {
    const mentionRegex = /@[a-zA-Z0-9_]+/g;
    return text.match(mentionRegex) || [];
  }
};

// Replacement patterns
const replacers = {
  // Sanitize HTML
  sanitizeHtml: (html) => {
    return html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
               .replace(/<[^>]+>/g, '');
  },
  
  // Mask sensitive data
  maskEmail: (email) => {
    return email.replace(/^(.{2})(.*)(@.*)$/, '$1***$3');
  },
  
  maskPhone: (phone) => {
    return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
  }
};
```
**Example Projects:** Form validation, log parsing, data extraction

### Cron Expressions
**Best For:** Scheduled tasks, periodic jobs, automation
```bash
# crontab - System cron jobs
# Format: minute hour day month weekday command
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
# │ │ │ │ │
# * * * * * command

# Backup database every day at 2:30 AM
30 2 * * * /usr/local/bin/backup-db.sh

# Clear temp files every hour
0 * * * * find /tmp -type f -mtime +7 -delete

# Generate reports every Monday at 9 AM
0 9 * * 1 python /opt/scripts/generate_weekly_report.py

# Update SSL certificates on 1st of every month
0 0 1 * * /usr/local/bin/certbot renew --quiet

# Run system updates every Sunday at 3 AM
0 3 * * 0 apt-get update && apt-get upgrade -y

# Monitor disk space every 30 minutes
*/30 * * * * /usr/local/bin/check_disk_space.sh

# Send reminder emails weekdays at 8 AM
0 8 * * 1-5 python /opt/scripts/send_reminders.py

# Rotate logs weekly
0 0 * * 0 /usr/sbin/logrotate /etc/logrotate.conf

# Sync data to cloud every 6 hours
0 */6 * * * rsync -av /data/ cloud-backup:/backup/

# Run performance metrics at midnight on the last day of month
0 0 28-31 * * [ $(date +\%d -d tomorrow) = 01 ] && /opt/scripts/monthly_metrics.sh
```
**Example Projects:** Backup systems, report generation, maintenance tasks

### Log File Formats
**Best For:** Debugging, monitoring, auditing
```log
# application.log - Structured logging
2024-01-15T10:30:45.123Z [INFO] Application started successfully
2024-01-15T10:30:45.456Z [DEBUG] Database connection established: postgresql://localhost:5432/myapp
2024-01-15T10:30:46.789Z [INFO] Server listening on port 8080
2024-01-15T10:31:02.234Z [INFO] Request: GET /api/users - IP: 192.168.1.100 - User-Agent: Mozilla/5.0
2024-01-15T10:31:02.345Z [DEBUG] Query executed: SELECT * FROM users LIMIT 10 - Duration: 23ms
2024-01-15T10:31:02.456Z [INFO] Response: 200 OK - Duration: 222ms
2024-01-15T10:31:15.678Z [WARN] High memory usage detected: 85% of available memory
2024-01-15T10:31:30.890Z [ERROR] Failed to process payment: Invalid card number
  Stack trace:
    at PaymentService.process (payment.js:45:12)
    at handlePayment (routes/payment.js:23:8)
    at Layer.handle (express/lib/router/layer.js:95:5)
2024-01-15T10:31:31.012Z [INFO] Sending error notification to admin@example.com
2024-01-15T10:32:00.123Z [INFO] Cache cleared: 1234 entries removed
2024-01-15T10:32:30.456Z [CRITICAL] Database connection lost: Connection timeout
2024-01-15T10:32:30.567Z [INFO] Attempting to reconnect to database...
2024-01-15T10:32:35.678Z [INFO] Database reconnected successfully
```
**Example Projects:** Application monitoring, error tracking, audit trails

## Best Practices

1. **LaTeX:** Use BibTeX for references, separate chapters into files
2. **Makefiles:** Use variables, provide help target, avoid hardcoding
3. **Regex:** Comment complex patterns, use named groups, test thoroughly
4. **Cron:** Log output, handle errors, use absolute paths
5. **Logs:** Use structured logging, rotate logs, set appropriate levels

## File Organization Pattern
```
project/
├── docs/
│   ├── latex/
│   │   ├── main.tex
│   │   └── chapters/
│   ├── Makefile
│   └── build/
├── scripts/
│   ├── cron/
│   └── regex/
└── logs/
    ├── app.log
    └── error.log
```

## Performance Considerations
- LaTeX: Use draft mode for faster compilation during writing
- Makefiles: Parallelize builds with -j flag
- Regex: Avoid catastrophic backtracking
- Cron: Stagger job times to avoid load spikes
- Logs: Implement log rotation and compression

## Specialized Tools
- **LaTeX:** TeXLive, MiKTeX, Overleaf
- **Make:** GNU Make, CMake, Ninja
- **Regex:** regex101.com, RegExr, grep/sed/awk
- **Cron:** crontab, systemd timers, Task Scheduler
- **Logging:** syslog, journald, ELK stack, Splunk