from setuptools import setup
from setuptools import find_packages

print(find_packages(exclude=["test*", "explorations"]))

setup(
    name="travel_planner",
    version="0.0.1",
    description="""
    This package is used for travel planning in public transpoirt.
    It has backend, frontend and utils.
    """,
    author="Kokchun Giang",
    author_email="cool_email842jjeld@gmail.com",
    install_requires=[
        "streamlit",
        "pandas",
        "requests",
        "folium",
        "python-dotenv",
    ],
    packages=find_packages(exclude=["test*", "explorations"]),
    entry_points={"console_scripts": ["dashboard = utils.run_dashboard:run_dashboard"]},
)