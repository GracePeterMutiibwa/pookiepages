from __future__ import annotations
import os
import rcssmin
import rjsmin
from pookiepages.exceptions import PookiePagesError


def minifyCss(content: str) -> str:
    return rcssmin.cssmin(content)


def minifyJs(content: str) -> str:
    return rjsmin.jsmin(content)


def minifyHtml(content: str) -> str:
    try:
        import minify_html
        return minify_html.minify(content, minify_js=False, minify_css=False)
    except ImportError:
        # minify-html is optional; fall back to basic whitespace compression
        import re
        content = re.sub(r">\s+<", "><", content)
        return content.strip()


def runBuildPipeline(
    static_dir: str,
    output_dir: str,
    minify_css: bool = True,
    minify_js: bool = True,
    minify_html_flag: bool = False,
) -> dict:
    if not os.path.isdir(static_dir):
        raise PookiePagesError(
            f"Build failed. Static directory '{static_dir}' does not exist. "
            f"Create the directory or update APP.staticDir in your config."
        )

    os.makedirs(output_dir, exist_ok=True)

    cssCount = 0
    jsCount = 0
    htmlCount = 0

    for dirPath, _, fileNames in os.walk(static_dir):
        relativePath = os.path.relpath(dirPath, static_dir)
        outputSubDir = os.path.join(output_dir, relativePath)
        os.makedirs(outputSubDir, exist_ok=True)

        for fileName in fileNames:
            inputPath = os.path.join(dirPath, fileName)
            outputPath = os.path.join(outputSubDir, fileName)

            with open(inputPath, "r", encoding="utf-8", errors="ignore") as inputFile:
                content = inputFile.read()

            if fileName.endswith(".css") and minify_css:
                content = minifyCss(content)
                cssCount += 1
            elif fileName.endswith(".js") and minify_js:
                content = minifyJs(content)
                jsCount += 1
            elif fileName.endswith(".html") and minify_html_flag:
                content = minifyHtml(content)
                htmlCount += 1

            with open(outputPath, "w", encoding="utf-8") as outputFile:
                outputFile.write(content)

    return {"css": cssCount, "js": jsCount, "html": htmlCount}
