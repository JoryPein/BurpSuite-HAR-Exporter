# BurpSuite-HAR-Exporter

**BurpSuite-HAR-Exporter**, is a Python-based tool designed to facilitate the conversion of saved Burp Suite HTTP items to the HTTP Archive (HAR) format.

## Installation

To use **BurpSuite-HAR-Exporter**, make sure you have Python installed on your system. You can then install the necessary dependencies using the following command:

```shell
poetry install
```

## CLI Usage

You can convert Burp Suite exported XML files to HAR format using the following command:

```shell
bpi2har exported.xml
```

Replace `exported.xml` with the path to your Burp Suite exported XML file.

## Example

```shell
bpi2har burp_export.xml
```

This command will generate a HAR file named `burp_export.har` in the current directory.

