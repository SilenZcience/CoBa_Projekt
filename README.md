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
            <li><a href="#execution">Execution</a></li>
         </ul>
      <li><a href="#examples">Examples</a></li>
         <ul>
            <li><a href="#compiling">Compiling</a></li>
            <li><a href="#liveness">Liveness</a></li>
            <ul>
                <li><a href="#explanation">Explanation</a></li>
            </ul>
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

- Download the Jasmin Java Assembler (>=2.4):
    - [Jasmin Home Page](https://jasmin.sourceforge.net/)
    - [Jasmin SourceForge Download Page](https://sourceforge.net/projects/jasmin/files/)

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
    |_ jasmin.jar
```

- Download & Install the Java JDK (>= v.11):
    - [Adoptium](https://adoptium.net/de/)
    - [Eclipse Temurin Releases](https://adoptium.net/de/temurin/releases/)
- Download & Install Python (>= v.3.9):
    - [Python](https://www.python.org/downloads/)

<p align="right">(<a href="#top">back to top</a>)</p>

## Installation

- Install the Python ANTLR Module:
    - run:
    
    ```console
    python -m pip install antlr4-python3-runtime~=4.13.1
    ```

- Generate the ANTLR Lexer -and Parser (aswell as a Visitor and Listener):
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

- Otherwise use:
    - ```python stups_compiler.py```

### Arguments

- -compile IN_FILE
    - compile the given Julia IN_FILE into Jasmin-Bytecode.
- -liveness IN_FILE
    - generate a register interference graph for the given IN_FILE.
- -output OUT_FILE
    - specify the output OUT_FILE used for compilation.
    - default is the input-file with a .j extension.
- -debug
    - show additional debug information (e.g. SymbolTable, ControlFlowGraph).

### Execution

- compile the generated Jasmin Bytecode using the Jasmin Assembler
    - run:

    ```console
    java -jar ./jasmin.jar <file.j>
    ```
- run the compiled .class file
    - run:

    ```console
    java -cp <classpath> <file.class>
    ```

<p align="right">(<a href="#top">back to top</a>)</p>

## Examples

```julia
# Example Code (test.jl):
function x()
    println("x")
end

function main()
    a::Integer = 1
        b::Integer = 1
        temp::Integer = 0
    println("Fibonacci:")
        while a < 144
            temp = b
                b = a + b
                a = temp
                println(a)
        end
    println("Calling other functions:")
    println(test_function("a"))
    x()
end

function test_function(x::String)::Float64
    a::Float64 = 20/3
    a = 5
    if (5/5+5*2 > 2)
        println(a)
    end
    return a
end

main()
```

### Compiling

```console
> python -m compiler -compile test.jl
Status: reading file test.jl
Status: parsing...
Status: parsing successful.
Status: typechecking...
Status: typechecking successful.
Status: generating...
Status: writing file test.j
Status: generating successful.

> java -jar ./jasmin.jar test.j
Generated: test.class

> java -cp . test
Fibonacci:
1
2
3
5
8
13
21
34
55
89
144
Calling other functions:
5.0
5.0
x
```

### Liveness

```console
> python -m compiler -liveness test.jl
...
Status: liveness result:

Function: x
Registers: 0
-------------------------
-------------------------

Function: main
Registers: 3
-------------------------
Nodes (#3) [Name(Register)]:
a(0),b(1),temp(2)
Adjacency List:
   a: {'temp', 'b'}
   b: {'temp', 'a'}
temp: {'a', 'b'}
-------------------------

Function: test_function
Registers: 1
-------------------------
Nodes (#2) [Name(Register)]:
x(0),a(0)
Adjacency List:
x: {}
a: {}
-------------------------
```

#### Explanation

Every Variable is assigned a Register, shown within the Parentheses.
```bat
a(0),b(1),temp(2)

defines:
a    -> RegisterId 0
b    -> RegisterId 1
temp -> RegisterId 2
```
Every Variable defines a Node.
The Adjacency List defines the Edges between given Nodes.
Such the Register-Interference-Graph is defined.
```bash
Adjacency List:
   a: {'temp', 'b'}
   b: {'temp', 'a'}
temp: {'a', 'b'}

defines the Graph:
   temp
  /    \
 /      \
a ------ b
```

<p align="right">(<a href="#top">back to top</a>)</p>

## Contact

> **SilenZcience** <br/>
[![GitHub-SilenZcience][GitHub-SilenZcience]](https://github.com/SilenZcience)

[GitHub-SilenZcience]: https://img.shields.io/badge/GitHub-SilenZcience-orange

[OS-Windows]: https://img.shields.io/badge/os-windows-green
[OS-Linux]: https://img.shields.io/badge/os-linux-green
[OS-MacOS]: https://img.shields.io/badge/os-macOS-green
