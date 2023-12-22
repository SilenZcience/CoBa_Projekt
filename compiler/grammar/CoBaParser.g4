parser grammar CoBaParser;

options {
    tokenVocab = CoBaLexer;
}


main: NEWLINE* structure NEWLINE* EOF;
structure: function* main_function function* main_function_call;


main_function: main_function_header function_body K_END NEWLINE+;
main_function_header: K_FUNCTION K_MAIN T_LPAR T_RPAR NEWLINE+;

function: function_header function_body K_END NEWLINE+;
function_header: K_FUNCTION IDENTIFIER T_LPAR function_parameter? T_RPAR type_assignement? NEWLINE+;
function_parameter: IDENTIFIER type_assignement (T_COMMA function_parameter)?;
function_body: declaration* instruction*? (return_statement NEWLINE+)?;
return_statement: K_RETURN expression?;

main_function_call: K_MAIN T_LPAR T_RPAR NEWLINE*;

function_call: (IDENTIFIER | K_MAIN) T_LPAR function_argument? T_RPAR;
function_argument: expression (T_COMMA function_argument)?;


declaration: IDENTIFIER type_assignement T_EQUAL expression NEWLINE+;

instruction: (assignement
             | block_structure
             | control_structure
             | print
             | function_call
             | return_statement) NEWLINE+;

assignement: IDENTIFIER T_EQUAL expression;
block_structure: K_BEGIN NEWLINE+ instruction* K_END;
control_structure: if_structure
                 | while_structure
                 ;
print: K_PRINTLN T_LPAR expression? T_RPAR;

if_structure: K_IF bool_expression NEWLINE* then_branch (K_ELSE NEWLINE* else_branch)? K_END;
then_branch: instruction*;
else_branch: instruction*;
while_structure: K_WHILE bool_expression NEWLINE* instruction* K_END;

bool_expression: expression;
expression: UNARY=(T_PLUS | T_MINUS | T_EXCLAMATION) RIGHT=expression
          | LEFT=expression (T_STAR | T_SLASH | T_PERCENT) RIGHT=expression
          | LEFT=expression (T_PLUS | T_MINUS) RIGHT=expression
          | LEFT=expression (T_NOTEQUAL | T_D_EQUAL | T_LESS | T_GREATER | T_LESSEQUAL | T_GREATEREQUAL) RIGHT=expression
          |<assoc=right> LEFT=expression T_D_AND RIGHT=expression
          |<assoc=right> LEFT=expression T_D_VBAR RIGHT=expression
          | function_call
          | atom
          ;

atom: T_LPAR expression T_RPAR
    | type_element
    | IDENTIFIER
    ;

type_assignement: T_D_COLON type_spec;
type_spec       : (K_INTEGER | K_FLOAT64)
                | K_BOOL
                | K_STRING
                ;
type_element    : (INTEGER_NUMBER | FLOAT_NUMBER)
                | (K_TRUE | K_FALSE)
                | STRING
                ;


/*
Struktur/Structure:
function main()
    # more code
end
# more functions
main()


Kommentar/Comment: 
x = 42 # Comment
#= multiline
comment =#


Literal/Literal:
Integer 11,-1,42
Float64 1.0, 3.12,-0.45
String "Hallo Welt"
Bool true,false


Operator/Operator:
Arithmetisch/Arithmetic:
a+b +b
a-b -b
a*b
a/b
a%b
Vergleich/Comparison:
a==b
a<b
a>b
a<=b
a>=b
a!=b
Boolsche (rechtsassoziativ):
a&&b
a||b
!b
Reihenfolge/Order:
1,+,- (unitär rechtsassoziativ)
*,/,%
+,-
!=,==,>,<,<=,>=
&&
||


Ausdruck/Expression:
Literale, Operatoren, Funktionsaufrufe **
Literals, Operators, FunctionCalls **


Variablen/Variables:
Deklaration/Declaration:
Bezeichner::Typ = Ausdruck
Identifier::Type = Expression


Typ/Type:
Integer
Float64
String
Bool


Zuweisung/Assignement:
Variable = Ausdruck
Variable = Expression


Block-Struktur/Block-Structure:
begin
    Anweisung1/Instruction1
    ...
    AnweisungN/InstructionN
end


Kontrollstruktur/Controlstructure:
if BoolscherAusdruck/BoolscheExpression Anweisung1/Instruction1
if BoolscherAusdruck/BoolscheExpression Anweisung1/Instruction1 else Anweisung2/Instruction2
while BoolscherAusdruck/BoolscheExpression Anweisung1/Instruction1 end


Funktion/Function:
function Bezeichner/Identifier(Bezeichner/Identifier::Typ/Type ... )::Typ/Type
    Deklarationen/Declarations
    Anweisungen/Instructions
    return Ausdruck/Expression
end


Anweisung/Instruction:
Ausdrücke/Expressions
Zuweisung/Assignement
Block-Struktur/Block-Structure
Kontrollstruktur/Controlstructure
 */
