from setuptools import setup, find_packages
from make_sphinx_documentation import BuildDocsCommand

BuildDocsCommand.sourcedir = "docs"

setup(
    name="SoundCraftAI",
    version="0.1.0",
    description="SoundCraft AI — Metaphysical SoundScape Assistant for Pyto and Ollama integration",
    author="Mikah Smith (Anonymous Schizophrenic)",
    author_email="contact@schizostudios.org",
    url="https://schizostudios.org",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.25.0",
        "psutil>=5.9.0",
        "mido>=1.3.0",
        "music21>=9.1.0",
        "numpy>=1.26.0",
        "pathspec>=0.10.1",
    ],
    python_requires=">=3.9",
    cmdclass={"build_docs": BuildDocsCommand},
    entry_points={
        "console_scripts": ["soundcraft-ai = soundcraft_ai.ai_helper:main"],
    },
)