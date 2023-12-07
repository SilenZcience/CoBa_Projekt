lexer grammar JuliaLexer;


// --- Keywords ---
K_INTEGER  : 'Integer';
K_FLOAT64  : 'Float64';
K_BOOL     : 'Bool';
K_STRING   : 'String';

K_TRUE     : 'true';
K_FALSE    : 'false';

K_IF       : 'if';
K_ELSE     : 'else';
K_BEGIN    : 'begin';
K_WHILE    : 'while';
K_END      : 'end';
K_FUNCTION : 'function';
K_RETURN   : 'return';
K_PRINTLN  : 'println';
K_MAIN     : 'main';



// --- Module-Tokens ---
T_LPAR             : '('; // OPEN_PAREN
T_RPAR             : ')'; // CLOSE_PAREN
// T_COLON            : ':';
T_D_COLON          : '::';
T_COMMA            : ',';

T_EQUAL            : '=';

T_PLUS             : '+';
T_MINUS            : '-';
T_STAR             : '*';
T_SLASH            : '/';
T_PERCENT          : '%';

T_D_EQUAL          : '==';
T_LESS             : '<';
T_GREATER          : '>';
T_LESSEQUAL        : '<=';
T_GREATEREQUAL     : '>=';
T_NOTEQUAL         : '!=';

T_D_AND            : '&&';
T_D_VBAR           : '||';
T_EXCLAMATION      : '!';



// --- Literals ---
IDENTIFIER: [a-zA-Z_$][a-zA-Z_$0-9]*; // Any character-sequence (Java-like)

// NUMBER: INTEGER_NUMBER | FLOAT_NUMBER;
FLOAT_NUMBER: INTEGER_NUMBER '.' INTEGER_NUMBER;
INTEGER_NUMBER: [1-9] [0-9]* | '0'+;

STRING: STRING_LITERAL;

NEWLINE: OS_INDEPENDENT_NL+;



// --- Skippable ---
COMMENT   : (LINE_COMMENT | BLOCK_COMMENT) -> skip;
WHITESPACE: [ \t\f]+ -> skip;


ERROR_TOKEN: .; // catch the unrecognized characters and redirect these errors to the parser



// --- Fragments ---
fragment STRING_LITERAL: '"' ~["\r\n]* '"';

fragment LINE_COMMENT : '#' ~[\r\n]*;
fragment BLOCK_COMMENT : '#=' ( BLOCK_COMMENT | . )*? '=#';

fragment OS_INDEPENDENT_NL: '\r'? '\n';

// fragment NAME: [a-zA-Z_][a-zA-Z_0-9];//[\u0000-\u007F]; // ASCII characters (0x7F = 0127)
