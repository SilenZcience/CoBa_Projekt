
## Installation

- Git Clone or Download (zip) the Projekt

Expected Directory Structure:
```
- CoBa_Projekt
    |_ compiler
        |_ src
            |_ ...
        |_ main.py
        |_ ...
```

- Download the ANTLR tool itself (>= v.4.13.1):
    - [ANTLR Download Page](https://www.antlr.org/download.html)
    - [Direct Download](https://github.com/antlr/website-antlr4/raw/gh-pages/download/antlr-4.13.1-complete.jar) (from the Github Repo)

Expected Directory Structure:
```
- CoBa_Projekt
    |_ compiler
        |_ src
            |_ ...
        |_ main.py
        |_ ...
    |_ antlr-4.13.1-complete.jar
```

- Download Java JDK (>= v.11):
    - [Adoptium](https://adoptium.net/de/)
    - [Eclipse Temurin Releases](https://adoptium.net/de/temurin/releases/)
- Download Python (>= v.3.10):
    - [Python](https://www.python.org/downloads/)

- Install the Python ANTLR Module:
    - run:
    
    ```python -m pip install antlr4-python3-runtime~=4.13.1```

- Generate the ANTLR Lexer -and Parser:
    - run (from the 'CoBa_Projekt' direcory):

    ```java -jar <antlr-*-complete.jar> -Dlanguage=Python3 ./compiler/src/CoBaLexer.g4 ./compiler/src/CoBaParser.g4 -o ./compiler/src```




## Usage

- Use the Project as a Python Module/Package:
    - run (from the 'CoBa_Projekt' direcory):

    ```python -m compiler -compile <file.jl>```

- Otherwise:
    - run

    ```python <main.py> -compile <file.jl>```
