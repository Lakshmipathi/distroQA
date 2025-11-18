# distroQA Design Document

## 1. Overview

### 1.1 Project Purpose
**distroQA** is an automated operating system GUI testing framework designed to validate Linux distributions and GUI applications through image-based automation. The framework provides comprehensive test execution recording, visual validation, and HTML-based reporting capabilities.

### 1.2 Goals
- Enable automated GUI testing without dependency on specific UI frameworks
- Provide visual validation through image recognition
- Generate comprehensive test reports with screenshots and video recordings
- Support containerized test execution for reproducibility
- Enable CI/CD integration for automated testing pipelines

### 1.3 Target Audience
- Linux distribution maintainers
- QA engineers testing GUI applications
- DevOps teams implementing automated testing
- Open source projects requiring GUI validation

---

## 2. Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Test Execution Layer                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ run_tests.sh│→ │run_ci_tests.sh│→ │Docker Container  │   │
│  └─────────────┘  └──────────────┘  │(laks/gui_tester) │   │
│                                      └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Core Automation Engine                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   distroqa.py                         │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│  │  │YAML Parser │→ │Image         │→ │Action       │  │  │
│  │  │            │  │Recognition   │  │Executor     │  │  │
│  │  └────────────┘  └──────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Test Resources Layer                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PNG Images│  │TXT (cmds)│  │KEY (hkey)│  │SH Scripts│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Recording & Reporting Layer                     │
│  ┌──────────────────┐        ┌───────────────────────┐     │
│  │FFmpeg Recorder   │───────→│HTML Report Generator  │     │
│  │(screen_recorder) │        │(report.sh)            │     │
│  └──────────────────┘        └───────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
                     ┌─────────────────┐
                     │  Test Results   │
                     │  (HTML + Video) │
                     └─────────────────┘
```

### 2.2 Component Descriptions

#### 2.2.1 Test Execution Layer
**Purpose**: Orchestrate test execution in containerized environments

**Components**:
- `run_tests.sh`: Main entry point for test execution
- `run_ci_tests.sh`: CI/CD pipeline wrapper
- `run_tests_existing_ct.sh`: Execute tests on existing containers
- Docker container: Isolated test environment with GUI capabilities

**Responsibilities**:
- Container lifecycle management
- Environment setup and teardown
- Test orchestration
- Result collection

#### 2.2.2 Core Automation Engine (`distroqa.py`)
**Purpose**: Execute GUI automation based on test definitions

**Key Modules**:
- **YAML Parser**: Read and parse test task definitions
- **Image Recognition**: Locate GUI elements using PyAutoGUI/PyScreeze
- **Action Executor**: Perform automated actions (click, type, hotkey, etc.)
- **State Manager**: Track test execution state and results

**Core Algorithm**:
```python
for each action in test_definition:
    1. Parse action type and timer
    2. Locate element via image recognition (70% confidence)
    3. Retry up to 10 times with 60-second intervals
    4. Execute action (click, type, hotkey, shell command)
    5. Capture screenshot
    6. Update test status (PASS/FAIL)
    7. Move mouse every 30s to prevent timeout
    8. Refresh screen every 5 minutes for long tests
```

**Supported Action Types**:
- `*.png`: Image-based element location and click
- `*.txt`: Shell command execution
- `*.key`: Keyboard hotkey/shortcut
- `*.mouse`: Mouse action (left/right click, double-click)
- `*.sh`: Shell script execution
- `*.csv`: Keyboard macro replay

#### 2.2.3 Test Resources Layer
**Purpose**: Store test artifacts and reference data

**Resource Types**:
- **PNG Images**: Reference screenshots for visual validation (grayscale mode)
- **Text Files**: Shell commands to execute
- **Key Files**: Keyboard shortcuts and hotkeys
- **Mouse Files**: Mouse action specifications
- **Shell Scripts**: Complex test operations
- **CSV Files**: Recorded keyboard macros

**Organization**:
```
images/baseimage/<test-name>/
├── step1_action.png
├── step2_command.txt
├── step3_hotkey.key
└── step4_script.sh
```

#### 2.2.4 Recording & Reporting Layer
**Purpose**: Capture test execution and generate reports

**Components**:
- **screen_recorder**: FFmpeg-based screen recording (25 fps)
- **report.sh**: HTML report generation with embedded media

**Report Features**:
- Color-coded test status (green=PASS, red=FAIL)
- Screenshot gallery for each test step
- Embedded video playback (5x accelerated)
- Video concatenation for multi-test runs
- Organized task hierarchy

---

## 3. Technology Stack

### 3.1 Core Technologies

| Technology | Purpose | Version/Details |
|------------|---------|-----------------|
| Python 3 | Main automation engine | Core language |
| Bash/Shell | Orchestration scripts | Setup, CI, reporting |
| Docker | Containerization | Isolated test environments |
| QEMU | Virtual machine emulation | OS testing |
| FFmpeg | Video recording/processing | 25fps, H.264 encoding |
| YAML | Test definition format | Human-readable configs |

### 3.2 Python Dependencies

| Library | Purpose | Key Usage |
|---------|---------|-----------|
| `pyautogui` | GUI automation | Screen capture, click detection, mouse/keyboard control |
| `pyscreeze` | Image recognition | Element location with confidence threshold |
| `oyaml` | YAML parsing | Ordered YAML parsing (maintains sequence) |
| `fabric` | Remote execution | SSH command execution |

### 3.3 Infrastructure

- **CI/CD**: GitLab CI with Docker-in-Docker support
- **Display Protocol**: SPICE (Simple Protocol for Independent Computing Environments)
- **Container Registry**: Custom Docker images (`laks/gui_tester`)

---

## 4. Workflow & Process

### 4.1 Test Execution Workflow

```
1. User invokes run_tests.sh
   ├─ Specify task file (*.yml)
   └─ Optional: existing container ID

2. Container Setup
   ├─ Create Docker container (or use existing)
   ├─ Mount test resources
   └─ Start display server (SPICE)

3. Test Execution (distroqa.py)
   ├─ Parse YAML task file
   ├─ Initialize screen recorder
   ├─ For each action:
   │  ├─ Locate element (image recognition)
   │  ├─ Execute action with retry logic
   │  ├─ Capture screenshot
   │  └─ Update test status
   └─ Stop screen recorder

4. Post-Processing
   ├─ Accelerate video (5x speedup)
   ├─ Generate HTML report
   └─ Publish artifacts

5. Cleanup
   └─ Optionally remove container
```

### 4.2 Image Recognition Algorithm

```python
def locate_and_click(image_path):
    confidence = 0.7
    max_retries = 10
    retry_interval = 60  # seconds

    for attempt in range(max_retries):
        location = pyautogui.locateOnScreen(
            image_path,
            grayscale=True,
            confidence=confidence
        )

        if location:
            center = pyautogui.center(location)
            pyautogui.click(center)
            return SUCCESS

        if attempt < max_retries - 1:
            time.sleep(retry_interval)
            move_mouse_prevent_timeout()

    return FAIL
```

### 4.3 Timer Semantics

| Timer Value | Behavior |
|-------------|----------|
| Positive (e.g., 30) | Wait N seconds before executing action |
| 0 | Infinite wait (up to 1 hour max) |
| Negative (e.g., -10) | Wait \|N\| seconds, then check for element |

### 4.4 CI/CD Pipeline

```yaml
Stages:
  1. test:
     - Run automated tests
     - Generate results
     - Create video recordings

  2. deploy:
     - Publish HTML reports
     - Archive artifacts (videos, screenshots)
     - Update GitLab Pages
```

---

## 5. Key Design Decisions

### 5.1 Image-Based Automation
**Decision**: Use image recognition instead of UI framework APIs

**Rationale**:
- Framework-agnostic (works with any GUI toolkit)
- Simulates real user interaction
- Validates actual visual appearance
- No dependency on application internals

**Trade-offs**:
- Sensitive to resolution/theme changes
- Requires reference image maintenance
- Slower than API-based automation

### 5.2 Containerization
**Decision**: Run all tests in Docker containers

**Rationale**:
- Reproducible test environments
- Isolation from host system
- Parallel test execution capability
- Easy cleanup and reset

**Trade-offs**:
- Additional overhead
- Display server complexity
- Network configuration requirements

### 5.3 YAML Test Definitions
**Decision**: Use YAML for test case specification

**Rationale**:
- Human-readable and writable
- Easy version control
- Supports complex data structures
- Wide tooling support

**Trade-offs**:
- Limited programming logic
- No native conditional execution
- Requires external orchestration

### 5.4 FFmpeg Recording
**Decision**: Record all test execution with FFmpeg

**Rationale**:
- Visual debugging capability
- Audit trail for test runs
- Demonstration/documentation value
- Failure analysis support

**Trade-offs**:
- Storage requirements
- Processing overhead
- Potential performance impact

---

## 6. Configuration & Customization

### 6.1 Tunable Parameters

| Parameter | Location | Default | Purpose |
|-----------|----------|---------|---------|
| Confidence Threshold | `distroqa.py` | 0.7 (70%) | Image recognition sensitivity |
| Max Retries | `distroqa.py` | 10 | Element location attempts |
| Retry Interval | `distroqa.py` | 60s | Time between retries |
| Mouse Move Interval | `distroqa.py` | 30s | Prevent timeout |
| Screen Refresh | `distroqa.py` | 5min | Long-running test refresh |
| Video FPS | `screen_recorder` | 25 | Recording frame rate |
| Video Speedup | `report.sh` | 5x | Playback acceleration |

### 6.2 Test Task Format

```yaml
# Example: hello_world.yml
hello_world:
  startmenu.png: 10        # Wait 10s, locate and click
  type_terminal.txt: 0     # Execute command immediately
  terminal_icon.png: 30    # Wait 30s, locate and click
  ctrl_l.key: 5            # Wait 5s, press Ctrl+L
  hello_world.txt: 0       # Type "Hello World"
  close_terminal.mouse: 2  # Wait 2s, close window
```

---

## 7. Error Handling & Resilience

### 7.1 Failure Scenarios

| Scenario | Detection | Recovery |
|----------|-----------|----------|
| Element not found | Image recognition timeout | Retry with exponential backoff |
| Container crash | Exit code monitoring | Restart container, resume test |
| Network failure | SSH connection error | Retry with Fabric |
| Display server issue | Screenshot capture failure | Restart SPICE server |
| Resource exhaustion | Docker errors | Clean up old containers/images |

### 7.2 Retry Logic

```python
Retry Strategy:
  - Max attempts: 10
  - Initial wait: 60 seconds
  - Strategy: Fixed interval
  - Timeout: 1 hour (for timer=0 cases)

Actions during retry:
  - Move mouse to prevent screensaver
  - Refresh screen every 5 minutes
  - Log each attempt
  - Capture screenshots
```

---

## 8. Results & Artifacts

### 8.1 Directory Structure

```
results/
└── {container-id}/
    └── {task-name}/
        ├── index.html              # Main report
        ├── final_video.mp4         # Consolidated video
        ├── {action-name}_0001.png  # Screenshot 1
        ├── {action-name}_0002.png  # Screenshot 2
        └── ...
```

### 8.2 Report Contents

**HTML Report (`index.html`)**:
- Test metadata (task name, timestamp, container ID)
- Status summary with color coding
- Screenshot gallery with captions
- Embedded video player
- Navigation and filtering

**Video Artifacts**:
- Raw recording (25 fps)
- Accelerated version (5x speedup)
- Concatenated multi-test video

---

## 9. Limitations & Constraints

### 9.1 Current Limitations

1. **Image Sensitivity**: Resolution, theme, and anti-aliasing affect recognition
2. **Sequential Execution**: No parallel action support
3. **Limited Conditionals**: No native if/else logic in YAML
4. **Manual Image Creation**: Reference images require manual capture
5. **Display Dependency**: Requires X11/SPICE display server
6. **Language Support**: Python 3 only, no multi-language support

### 9.2 Performance Constraints

- **Retry Overhead**: 10 retries × 60s = 10 minutes max per action
- **Recording Impact**: FFmpeg consumes CPU during test execution
- **Container Startup**: ~5-10 seconds per container launch
- **Image Recognition**: ~0.5-2 seconds per locate operation

---

## 10. Future Enhancements

### 10.1 Planned Features

1. **Dynamic Image Recognition**
   - Template matching with multiple confidence levels
   - OCR-based text detection
   - Adaptive threshold adjustment

2. **Advanced Test Logic**
   - Conditional execution (if/else)
   - Loop support (for/while)
   - Variable substitution
   - Data-driven testing (CSV/JSON input)

3. **Parallel Execution**
   - Multi-container orchestration
   - Distributed test execution
   - Result aggregation

4. **Enhanced Reporting**
   - Test comparison (baseline vs. current)
   - Performance metrics (execution time)
   - Failure trend analysis
   - Integration with test management systems

5. **Improved Resilience**
   - Self-healing test cases
   - Alternative element locators
   - Graceful degradation

6. **Developer Experience**
   - Test recording mode (capture user actions)
   - Visual test editor
   - Image library management
   - CI/CD integration templates

### 10.2 Research Areas

- **AI/ML Integration**: Train models for better element detection
- **Cross-Platform Support**: Windows and macOS testing
- **Cloud Integration**: AWS/GCP/Azure test execution
- **Performance Testing**: Load testing GUI applications

---

## 11. Security Considerations

### 11.1 Test Environment Isolation

- **Container Security**: Run tests in unprivileged containers
- **Network Isolation**: Separate test network namespace
- **Volume Permissions**: Read-only mounts for test resources

### 11.2 Artifact Security

- **Screenshot Sanitization**: Redact sensitive information
- **Access Control**: Restrict report access to authorized users
- **Artifact Retention**: Define cleanup policies

### 11.3 Execution Safety

- **Resource Limits**: CPU/memory constraints on containers
- **Timeout Protection**: Prevent infinite test execution
- **Command Injection**: Sanitize user inputs in YAML

---

## 12. Maintenance & Operations

### 12.1 Image Library Management

**Best Practices**:
- Version control all reference images
- Document image capture conditions (resolution, theme)
- Maintain multiple variants for different environments
- Regular validation and updates

### 12.2 Container Management

**Lifecycle**:
- Build: Automated via CI/CD
- Test: Validation before deployment
- Deploy: Push to container registry
- Monitor: Resource usage tracking
- Retire: Remove deprecated versions

### 12.3 Result Archival

**Strategy**:
- Keep results for 30 days by default
- Archive critical test runs indefinitely
- Compress videos for long-term storage
- Index reports for searchability

---

## 13. Glossary

| Term | Definition |
|------|------------|
| **Action** | Single automation step (click, type, hotkey, etc.) |
| **Task** | Collection of actions defined in YAML file |
| **Timer** | Delay before executing action (in seconds) |
| **Confidence** | Image recognition match threshold (0.0-1.0) |
| **Container ID** | Unique identifier for Docker container |
| **Base Image** | Directory containing test resource files |
| **Screen Recorder** | FFmpeg-based recording utility |
| **SPICE** | Display protocol for remote access |

---

## 14. References

- **Project Repository**: https://github.com/Lakshmipathi/distroQA
- **FOSSASIA Summit 2020**: Cloud Track presentation
- **PyAutoGUI Documentation**: https://pyautogui.readthedocs.io/
- **FFmpeg Documentation**: https://ffmpeg.org/documentation.html
- **QEMU Documentation**: https://www.qemu.org/docs/

---

## 15. Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-18 | Initial design document | Claude AI |

---

## Appendix A: Example Test Case

**File**: `tasks/hello_world.yml`

```yaml
hello_world:
  # Open start menu
  startmenu.png: 10

  # Search for terminal
  type_terminal.txt: 0

  # Click terminal icon
  terminal_icon.png: 30

  # Clear screen
  ctrl_l.key: 5

  # Type hello world command
  hello_world.txt: 0

  # Close terminal
  alt_f4.key: 2
```

**Resources**:
- `images/baseimage/hello_world/startmenu.png`
- `images/baseimage/hello_world/type_terminal.txt` → "terminal"
- `images/baseimage/hello_world/terminal_icon.png`
- `images/baseimage/hello_world/ctrl_l.key` → "ctrl+l"
- `images/baseimage/hello_world/hello_world.txt` → "echo 'Hello World'"
- `images/baseimage/hello_world/alt_f4.key` → "alt+f4"

---

## Appendix B: CI/CD Configuration

```yaml
# .gitlab-ci.yml
stages:
  - test
  - deploy

test_gui:
  stage: test
  script:
    - ./run_ci_tests.sh
  artifacts:
    paths:
      - results/
    expire_in: 30 days

pages:
  stage: deploy
  dependencies:
    - test_gui
  script:
    - mv results/ public/
  artifacts:
    paths:
      - public
  only:
    - master
```

---

**Document Status**: Draft
**Last Updated**: 2025-11-18
**Next Review**: Quarterly
