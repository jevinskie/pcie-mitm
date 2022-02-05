from setuptools import setup, find_packages

setup(
    name="pcie-mitm",
    version="1.0.0",
    url="https://github.com/jevinskie/pcie-mitm",
    author="Jevin Sweval",
    author_email="jevinsweval@gmail.com",
    description="LiteX-based PCIe MITM, sniffing, fuzzing, device emulation",
    packages=find_packages(),
    install_requires=[
        "rich",
    ],
)
