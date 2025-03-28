from setuptools import setup, find_packages

setup(
    name="nautobot-mcp",
    version="0.1.2",
    description="Nautobot MCP",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Geury Torres",
    author_email="geuryt@yahoo.com",
    license="Apache-2.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.6.0",
    ],
    url="https://github.com/gt732/nautobot-app-mcp",
)
