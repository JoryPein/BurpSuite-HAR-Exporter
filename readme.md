# BurpSuite-HAR-Exporter

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

**BurpSuite-HAR-Exporter** 🚀 is a Python-based tool crafted to streamline the conversion of saved Burp Suite HTTP items to the HTTP Archive (HAR) format.

## Installation

To get started with **BurpSuite-HAR-Exporter**, ensure that you have Python installed on your system. Then, install the necessary dependencies using the following command:

```shell
poetry install
```

## CLI Usage

Easily convert Burp Suite exported XML files to the HAR format using the following command:

```shell
bpi2har exported.xml
```

Replace `exported.xml` with the path to your Burp Suite exported XML file.

## Example

```shell
bpi2har burp_export.xml
```

This command will generate a HAR file named `burp_export.har` in the current directory. 📦
