grammar Nomos;

spec 
  : import_ input_* vars_* precondition* output* program postcondition* 
;

import_ 
  : 'import ' dataset=('german_credit' | 'compas' | 'mnist' | 'speech_command' | 'hotel_review' | 'lunar' | 'bipedal') SEMICOLON
;

input_
  : INPUT inp=inpvar SEMICOLON
;

output
  : OUTPUT out=outvar SEMICOLON
;

vars_
  : VARKW assignment SEMICOLON
;

program
  : prog=PROGRAM
;

assignment 
  : left=record ASS right_rec=record
  | left=record ASS right_math=math
;

precondition 
  : REQUIRES expr SEMICOLON
;

postcondition 
  : ENSURES expr SEMICOLON
;

expr
  : NOT expr                                # exprNot
  | LBR expr RBR                            # exprPrn
  | left=expr (AND | OR | IMPL) right=expr  # exprBinary
  | left=record op=cmpOp right=record       # exprPred
;

record 
  : NUM                                   # recNum
  | EMPTYSTR                              # recEmptyStr
  | ( inpvar | outvar | commonvar)        # recVar
  | feature                               # recFtr
  | var=inpvar '.' ftr=feature            # recVarFtr
  | func=FUNC LBR  params=funcParam RBR   # recFunc 
  | var=inpvar (LSBR assignment RSBR)+    # recFtrAss
;

math
  : LBR math RBR                            # mathPrn
  | left=math (PLUS | MINUS | MULT | DIV) right=math   # mathBinary
  | record   # mathRec
;


funcParam
  : param=record
  | param=record COMMA funcParam
;

cmpOp
  : LSQ 
  | GRQ 
  | LSS 
  | GRT 
  | EQL 
  | NEQ
;

commonvar 
  : 'v' NUM
;

inpvar 
  : ('x'|'s') NUM 
;

outvar 
  : ('d'|'o')  NUM 
;

feature 
  : 'f' NUM            # llvlFeature
  | ( 'pos' | 'neg' )  # hlvlFeature
;

PROGRAM : 
  LCBR
  .*?
  RCBR
;

INPUT : 'input';
OUTPUT : 'output' ;
VARKW : 'var' ;
REQUIRES : 'requires' ;
ENSURES : 'ensures' ;

PLUS  : '+' ;
MINUS : '-' ;
MULT  : '*' ;
DIV   : '/' ;

NUM :   '-'?[0-9]+ ('.' [0-9]+)? ([eE] [+-]? [0-9]+)? ;

FUNC : [A-Za-z-]+ ;

EMPTYSTR : '\"\"' ;

LCBR : '{' ;
RCBR : '}' ;
LSBR : '[' ;
RSBR : ']' ;
LBR :  '(' ;
RBR :  ')' ;

LSS :  '<'  ;
LSQ :  '<=' ;
GRT :  '>'  ;
GRQ :  '>=' ;
EQL :  '==' ;
NEQ :  '!=' ;
AND :  '&&' ;
OR  :  '||' ;
NOT :  '!'  ;
IMPL:  '==>' ;
ASS :  ':=' ;
// SAMPLE : '~' ;

COMMA : ',' ;
SEMICOLON : ';' ;

WS : [ \t\r\n]+ -> skip ;

COMMENT : '/*' .*? '*/' -> skip ;

LINE_COMMENT : '//' ~[\r\n]* -> skip ;
