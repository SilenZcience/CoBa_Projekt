<div id="top"></div>

[![OS-Windows]][OS-Windows]
[![OS-Linux]][OS-Linux]
[![OS-MacOS]][OS-MacOS]

<br/>
<div align="center">
<h2 align="center">CoBa_Projekt</h2>
   <p align="center">
      A Julia to Jasmin compiler using ANTLR in Python as defined in the CoBa-Project.
   </p>
</div>

<details>
   <summary>Table of Contents</summary>
   <ol>
      <li>
         <a href="#getting-started">Getting Started</a>
         <ul>
            <li><a href="#prerequisites">Prerequisites</a></li>
            <li><a href="#installation">Installation</a></li>
         </ul>
      </li>
      <li><a href="#usage">Usage</a></li>
         <ul>
            <li><a href="#arguments">Arguments</a></li>
         </ul>
      <li><a href="#contact">Contact</a></li>
   </ol>
</details>

## Getting Started

```console
Developed with the following Version Specifications:

Java:
openjdk 21 2023-09-19 LTS
OpenJDK Runtime Environment Temurin-21+35 (build 21+35-LTS)
OpenJDK 64-Bit Server VM Temurin-21+35 (build 21+35-LTS, mixed mode, sharing)

Python:
Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr  5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)]

ANTLR:
antlr-4.13.1-complete

Julia:
julia version 1.9.4
```

### Prerequisites

- Git Clone or Download (zip) the Project

```
Expected Directory Structure:
- CoBa_Projekt
    |_ compiler
        |_ src
            |_ ...
        |_ grammar
            |_ CoBaLexer.g4
            |_ CoBaParser.g4
        |_ stups_compiler.py
        |_ ...
```

- Download the ANTLR tool itself (>= v.4.13.1):
    - [ANTLR Download Page](https://www.antlr.org/download.html)
    - [Direct Download](https://github.com/antlr/website-antlr4/raw/gh-pages/download/antlr-4.13.1-complete.jar) (from the official Github Repo)

```
Expected Directory Structure:
- CoBa_Projekt
    |_ compiler
        |_ src
            |_ ...
        |_ grammar
            |_ CoBaLexer.g4
            |_ CoBaParser.g4
        |_ stups_compiler.py
        |_ ...
    |_ antlr-4.13.1-complete.jar
```

- Download & Install Java JDK (>= v.11):
    - [Adoptium](https://adoptium.net/de/)
    - [Eclipse Temurin Releases](https://adoptium.net/de/temurin/releases/)
- Download & Install Python (>= v.3.10):
    - [Python](https://www.python.org/downloads/)

<p align="right">(<a href="#top">back to top</a>)</p>

## Installation

- Install the Python ANTLR Module:
    - run:
    
    ```console
    python -m pip install antlr4-python3-runtime~=4.13.1
    ```

- Generate the ANTLR Lexer -and Parser:
    - run (from the 'CoBa_Projekt' direcory):

    ```console
    java -jar ./antlr-4.13.1-complete.jar -Dlanguage=Python3 ./compiler/grammar/CoBaLexer.g4 ./compiler/grammar/CoBaParser.g4 -listener -visitor -o ./compiler/src
    ```

<p align="right">(<a href="#top">back to top</a>)</p>

## Usage

```console
stups_compiler.py [-h] [-compile IN_FILE] [-liveness IN_FILE] [-output OUT_FILE] [-debug]
```

- Use the Project as a Python Module/Package (run from the 'CoBa_Projekt' directory):
    - ```python -m compiler```

- Otherwise
    - ```python stups_compiler.py```

### Arguments

- -compile FILE
    - compile the given Julia IN_FILE into Jasmin-Bytecode.
- -liveness FILE
    - generate a register interference graph for the given IN_FILE.
- -output FILE
    - specify the output OUT_FILE used for compilation..
    - default is the input-file with a .j extension.
- -debug
    - show additional debug information.


<p align="right">(<a href="#top">back to top</a>)</p>

## Contact

> **SilenZcience** <br/>
[![GitHub-SilenZcience][GitHub-SilenZcience]](https://github.com/SilenZcience)

[GitHub-SilenZcience]: https://img.shields.io/badge/GitHub-SilenZcience-orange

[OS-Windows]: https://img.shields.io/badge/os-windows-green
[OS-Linux]: https://img.shields.io/badge/os-linux-green
[OS-MacOS]: https://img.shields.io/badge/os-macOS-green
