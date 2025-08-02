lexer grammar MySqlLexer;

options {
    caseInsensitive = true;
}

// Keywords
SELECT: 'SELECT';
FROM: 'FROM';
WHERE: 'WHERE';
AND: 'AND';
OR: 'OR';
INSERT: 'INSERT';
INTO: 'INTO';
VALUES: 'VALUES';
UPDATE: 'UPDATE';
SET: 'SET';
DELETE: 'DELETE';
CREATE: 'CREATE';
TABLE: 'TABLE';
DROP: 'DROP';
ALTER: 'ALTER';
INDEX: 'INDEX';
PRIMARY: 'PRIMARY';
KEY: 'KEY';
NOT: 'NOT';
NULL: 'NULL';
DEFAULT: 'DEFAULT';
AUTO_INCREMENT: 'AUTO_INCREMENT';
UNIQUE: 'UNIQUE';
FOREIGN: 'FOREIGN';
REFERENCES: 'REFERENCES';
INNER: 'INNER';
LEFT: 'LEFT';
RIGHT: 'RIGHT';
JOIN: 'JOIN';
ON: 'ON';
GROUP: 'GROUP';
BY: 'BY';
ORDER: 'ORDER';
HAVING: 'HAVING';
LIMIT: 'LIMIT';
OFFSET: 'OFFSET';
ASC: 'ASC';
DESC: 'DESC';
DISTINCT: 'DISTINCT';
AS: 'AS';
COUNT: 'COUNT';
SUM: 'SUM';
AVG: 'AVG';
MAX: 'MAX';
MIN: 'MIN';
IN: 'IN';
BETWEEN: 'BETWEEN';
LIKE: 'LIKE';
IS: 'IS';
EXISTS: 'EXISTS';

// Operators
EQ: '=';
NE: '!=' | '<>';
LT: '<';
LE: '<=';
GT: '>';
GE: '>=';
PLUS: '+';
MINUS: '-';
MULTIPLY: '*';
DIVIDE: '/';
MOD: '%';

// Punctuation
SEMICOLON: ';';
COMMA: ',';
LPAREN: '(';
RPAREN: ')';
DOT: '.';

// Literals
INTEGER: [0-9]+;
DECIMAL: [0-9]+ '.' [0-9]+;
STRING: '\'' (~[\'] | '\'\'')* '\'';
IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;
BACKTICK_IDENTIFIER: '`' (~[`] | '``')* '`';

// Comments
SINGLE_LINE_COMMENT: '--' ~[\r\n]* -> skip;
MULTI_LINE_COMMENT: '/*' .*? '*/' -> skip;

// Whitespace
WS: [ \t\r\n]+ -> skip;