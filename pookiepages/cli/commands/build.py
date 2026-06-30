from __future__ import annotations
import click


@click.command("build")
@click.option("--no-minify-css", is_flag=True, default=False)
@click.option("--no-minify-js", is_flag=True, default=False)
@click.option("--output", default="", help="Output directory (overrides config)")
def buildCommand(no_minify_css: bool, no_minify_js: bool, output: str):
    """Build and minify static assets."""
    import os, sys
    sys.path.insert(0, os.getcwd())

    from pookiepages.config import loadConfig
    appConfig, buildConfig, _, _ = loadConfig(os.getcwd())

    outputDir = output or buildConfig.outputDir
    staticDir = appConfig.staticDir

    from pookiepages.assets.pipeline import runBuildPipeline
    counts = runBuildPipeline(
        static_dir=staticDir,
        output_dir=outputDir,
        minify_css=not no_minify_css and buildConfig.minifyCss,
        minify_js=not no_minify_js and buildConfig.minifyJs,
        minify_html_flag=buildConfig.minifyHtml,
    )
    print(
        f"pookiepages: build complete: {counts['css']} CSS files, "
        f"{counts['js']} JS files minified -> {outputDir}/"
    )
