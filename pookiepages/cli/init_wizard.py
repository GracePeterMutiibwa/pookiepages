from __future__ import annotations
import os
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, Input, Select, Button, Static
from textual.containers import Vertical, Horizontal
from textual.screen import Screen


PROJECT_TYPES = [("Dynamic (full stack)", "dynamic"), ("Static (no backend)", "static")]


class InitWizardApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    #wizard-box {
        width: 70;
        padding: 2 4;
        border: round $primary;
    }
    Label {
        margin: 1 0 0 0;
    }
    Input {
        margin: 0 0 1 0;
    }
    #buttons {
        margin-top: 2;
    }
    """

    BINDINGS = [("ctrl+c", "quit", "Quit")]

    def __init__(self):
        super().__init__()
        self.projectName = ""
        self.projectType = "dynamic"
        self.outputDir = ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="wizard-box"):
            yield Static("pookiepages init - Project Scaffold Wizard", classes="title")
            yield Label("Project name:")
            yield Input(placeholder="my-project", id="project-name")
            yield Label("Project type:")
            yield Select(
                [(label, value) for label, value in PROJECT_TYPES],
                id="project-type",
                value="dynamic",
            )
            yield Label("Output directory (leave blank for current directory):")
            yield Input(placeholder=".", id="output-dir")
            with Horizontal(id="buttons"):
                yield Button("Create Project", variant="primary", id="create")
                yield Button("Cancel", variant="default", id="cancel")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "cancel":
            self.exit(result=None)
            return

        nameInput = self.query_one("#project-name", Input)
        typeSelect = self.query_one("#project-type", Select)
        dirInput = self.query_one("#output-dir", Input)

        self.projectName = nameInput.value.strip() or "my-project"
        self.projectType = str(typeSelect.value)
        self.outputDir = dirInput.value.strip() or "."

        self.exit(result={
            "name": self.projectName,
            "type": self.projectType,
            "dir": self.outputDir,
        })


def scaffoldProject(name: str, project_type: str, output_dir: str):
    projectDir = os.path.join(output_dir, name) if output_dir != "." else name
    os.makedirs(projectDir, exist_ok=True)

    dirs = ["pages", "static", "static/css", "static/js"]
    if project_type == "dynamic":
        dirs += ["models", "routes", "migrations"]

    for directory in dirs:
        os.makedirs(os.path.join(projectDir, directory), exist_ok=True)

    configContent = f"""from pookiepages.config import AppConfig, DevConfig

APP = AppConfig(
    secretKey="change-me-to-a-long-random-secret",
    pagesDir="pages",
    staticDir="static",
    routes=["routes.api"],
    publicConfig={{}},
    bridge=True,
)

DEV = DevConfig(port=8000, host="127.0.0.1", reload=True, apiDocs=True)
"""
    with open(os.path.join(projectDir, "pookiepages.config.py"), "w") as configFile:
        configFile.write(configContent)

    if project_type == "dynamic":
        settingsContent = """from pookiepages.database import DatabaseConfig

DATABASE = DatabaseConfig(url="sqlite:///app.db")
"""
        with open(os.path.join(projectDir, "settings.py"), "w") as settingsFile:
            settingsFile.write(settingsContent)

        with open(os.path.join(projectDir, "routes", "__init__.py"), "w") as routeInitFile:
            routeInitFile.write("")
        with open(os.path.join(projectDir, "routes", "api.py"), "w") as apiFile:
            apiFile.write("""from pookiepages.api import api
from pookiepages.request import Request
from pookiepages.response import JsonResponse


@api.get("/api/hello")
def hello(req: Request) -> JsonResponse:
    return JsonResponse({"message": "hello from pookiepages"})
""")

    indexContent = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Welcome to pookiepages</title>
</head>
<body>
<h1>Welcome to pookiepages</h1>
<p>Edit pages/index.html to get started.</p>
</body>
</html>
"""
    with open(os.path.join(projectDir, "pages", "index.html"), "w") as indexFile:
        indexFile.write(indexContent)

    gitignoreContent = """.pookiepages.key
.progress/
__pycache__/
*.pyc
dist/
.venv/
vectors/
uploads/
*.db
.env
"""
    with open(os.path.join(projectDir, ".gitignore"), "w") as gitignoreFile:
        gitignoreFile.write(gitignoreContent)

    print(f"pookiepages: project '{name}' created at {projectDir}/")
    print(f"pookiepages: run 'cd {projectDir} && pookiepages run' to start.")


def runInitWizard():
    wizardApp = InitWizardApp()
    result = wizardApp.run()

    if result is None:
        print("pookiepages: init cancelled.")
        return

    scaffoldProject(result["name"], result["type"], result["dir"])
