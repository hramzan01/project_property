from setuptools import setup, find_packages

# list dependencies from requirements.txt
# list dependencies from file
with open('requirements.txt') as f:
    content = f.readlines()
requirements = [x.strip() for x in content]

setup(
    name='scraper',
    description='A web scraper to scrape property data from a rightmove.co.uk search page.',
    version='0.1',
    packages=find_packages(),
    install_requires=requirements
)
