from setuptools import find_packages, setup

print(find_packages(exclude=["test*", "explorations"]))

setup(
    name="travel_planner",
    version="0.0.1",
    description="""
    This package is used for travel planning in public transpoirt.
    It has backend, frontend and utils.
    """,
    author="Hampus E, Yassine, Mosen, Dan",
    author_email="",
    install_requires=[
        "streamlit",
        "pandas",
        "requests",
        "folium",
        "python-dotenv",
    ],
    packages=find_packages(
        include=["backend", "frontend", "utils"], exclude=["test*", "explorations"]
    ),
    entry_points={"console_scripts": ["dashboard = utils.run_dashboard:run_dashboard"]},
)
