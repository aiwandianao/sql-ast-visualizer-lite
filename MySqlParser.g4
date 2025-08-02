parser grammar MySqlParser;

options {
    tokenVocab = MySqlLexer;
}

// Root rule
root
    : sqlStatements? EOF
    ;

sqlStatements
    : sqlStatement (SEMICOLON sqlStatement?)* SEMICOLON?
    ;

sqlStatement
    : selectStatement
    | insertStatement
    | updateStatement
    | deleteStatement
    | createStatement
    | dropStatement
    ;

// SELECT statement
selectStatement
    : SELECT selectElements fromClause? whereClause? groupByClause? havingClause? orderByClause? limitClause?
    ;

selectElements
    : (DISTINCT | ALL)? selectElement (COMMA selectElement)*
    ;

selectElement
    : (tableName DOT)? columnName (AS? alias)?
    | functionCall (AS? alias)?
    | MULTIPLY
    ;

fromClause
    : FROM tableSource (COMMA tableSource)*
    ;

tableSource
    : tableName (AS? alias)?
    | tableName joinPart*
    ;

joinPart
    : (INNER | LEFT | RIGHT)? JOIN tableName (AS? alias)? ON expression
    ;

whereClause
    : WHERE expression
    ;

groupByClause
    : GROUP BY columnName (COMMA columnName)*
    ;

havingClause
    : HAVING expression
    ;

orderByClause
    : ORDER BY orderByExpression (COMMA orderByExpression)*
    ;

orderByExpression
    : columnName (ASC | DESC)?
    ;

limitClause
    : LIMIT INTEGER (OFFSET INTEGER)?
    ;

// INSERT statement
insertStatement
    : INSERT INTO tableName (LPAREN columnName (COMMA columnName)* RPAREN)? VALUES LPAREN literal (COMMA literal)* RPAREN
    ;

// UPDATE statement
updateStatement
    : UPDATE tableName SET updateElement (COMMA updateElement)* whereClause?
    ;

updateElement
    : columnName EQ literal
    ;

// DELETE statement
deleteStatement
    : DELETE FROM tableName whereClause?
    ;

// CREATE statement
createStatement
    : CREATE TABLE tableName LPAREN columnDefinition (COMMA columnDefinition)* RPAREN
    ;

columnDefinition
    : columnName dataType columnConstraint*
    ;

dataType
    : IDENTIFIER (LPAREN INTEGER (COMMA INTEGER)? RPAREN)?
    ;

columnConstraint
    : NOT NULL
    | PRIMARY KEY
    | UNIQUE
    | AUTO_INCREMENT
    | DEFAULT literal
    ;

// DROP statement
dropStatement
    : DROP TABLE tableName
    ;

// Expressions
expression
    : expression AND expression
    | expression OR expression
    | predicate
    ;

predicate
    : expressionAtom comparisonOperator expressionAtom
    | expressionAtom IS NOT? NULL
    | expressionAtom IN LPAREN literal (COMMA literal)* RPAREN
    | expressionAtom BETWEEN expressionAtom AND expressionAtom
    | expressionAtom LIKE STRING
    | EXISTS LPAREN selectStatement RPAREN
    | LPAREN expression RPAREN
    ;

comparisonOperator
    : EQ | NE | LT | LE | GT | GE
    ;

expressionAtom
    : columnName
    | literal
    | functionCall
    | LPAREN expression RPAREN
    ;

functionCall
    : functionName LPAREN (functionArg (COMMA functionArg)*)? RPAREN
    ;

functionName
    : COUNT | SUM | AVG | MAX | MIN | IDENTIFIER
    ;

functionArg
    : expression
    | MULTIPLY
    ;

// Basic elements
tableName
    : IDENTIFIER | BACKTICK_IDENTIFIER
    ;

columnName
    : IDENTIFIER | BACKTICK_IDENTIFIER
    ;

alias
    : IDENTIFIER | BACKTICK_IDENTIFIER
    ;

literal
    : STRING
    | INTEGER
    | DECIMAL
    | NULL
    ;