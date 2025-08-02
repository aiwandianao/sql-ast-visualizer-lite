#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL AST 解析器
读取 input.sql 中的 SQL 语句，使用 ANTLR 生成语法树，并输出简化的 JSON 格式
"""

import os
import sys
import json

# 实现一个基础的SQL解析器
class SimpleSQLParser:
    def __init__(self):
        self.tokens = []
        self.current = 0
    
    def tokenize(self, sql):
        """简单的词法分析"""
        import re
        # 移除注释
        sql = re.sub(r'--.*?\n', ' ', sql)
        sql = re.sub(r'/\*.*?\*/', ' ', sql, flags=re.DOTALL)
        
        # 定义token模式
        patterns = [
            (r'\bSELECT\b', 'SELECT'),
            (r'\bFROM\b', 'FROM'),
            (r'\bWHERE\b', 'WHERE'),
            (r'\bAND\b', 'AND'),
            (r'\bOR\b', 'OR'),
            (r'\bINSERT\b', 'INSERT'),
            (r'\bINTO\b', 'INTO'),
            (r'\bVALUES\b', 'VALUES'),
            (r'\bUPDATE\b', 'UPDATE'),
            (r'\bSET\b', 'SET'),
            (r'\bDELETE\b', 'DELETE'),
            (r'\bCREATE\b', 'CREATE'),
            (r'\bTABLE\b', 'TABLE'),
            (r'\bDROP\b', 'DROP'),
            (r'\bJOIN\b', 'JOIN'),
            (r'\bINNER\b', 'INNER'),
            (r'\bLEFT\b', 'LEFT'),
            (r'\bRIGHT\b', 'RIGHT'),
            (r'\bON\b', 'ON'),
            (r'\bGROUP\b', 'GROUP'),
            (r'\bBY\b', 'BY'),
            (r'\bORDER\b', 'ORDER'),
            (r'\bHAVING\b', 'HAVING'),
            (r'\bLIMIT\b', 'LIMIT'),
            (r'\bAS\b', 'AS'),
            (r'\bDISTINCT\b', 'DISTINCT'),
            (r'\bNULL\b', 'NULL'),
            (r'\bNOT\b', 'NOT'),
            (r'\bIS\b', 'IS'),
            (r'\bLIKE\b', 'LIKE'),
            (r'\bIN\b', 'IN'),
            (r'\bBETWEEN\b', 'BETWEEN'),
            (r'\bCOUNT\b', 'COUNT'),
            (r'\bSUM\b', 'SUM'),
            (r'\bAVG\b', 'AVG'),
            (r'\bMAX\b', 'MAX'),
            (r'\bMIN\b', 'MIN'),
            (r'>=', 'GE'),
            (r'<=', 'LE'),
            (r'<>', 'NE'),
            (r'!=', 'NE'),
            (r'=', 'EQ'),
            (r'<', 'LT'),
            (r'>', 'GT'),
            (r'\+', 'PLUS'),
            (r'-', 'MINUS'),
            (r'\*', 'MULTIPLY'),
            (r'/', 'DIVIDE'),
            (r'%', 'MOD'),
            (r';', 'SEMICOLON'),
            (r',', 'COMMA'),
            (r'\(', 'LPAREN'),
            (r'\)', 'RPAREN'),
            (r'\.', 'DOT'),
            (r"'[^']*'", 'STRING'),
            (r'`[^`]*`', 'BACKTICK_IDENTIFIER'),
            (r'\d+\.\d+', 'DECIMAL'),
            (r'\d+', 'INTEGER'),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),
        ]
        
        tokens = []
        pos = 0
        while pos < len(sql):
            # 跳过空白字符
            if sql[pos].isspace():
                pos += 1
                continue
                
            matched = False
            for pattern, token_type in patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                match = regex.match(sql, pos)
                if match:
                    value = match.group(0)
                    tokens.append({
                        'type': token_type,
                        'value': value,
                        'start': pos,
                        'end': pos + len(value)
                    })
                    pos = match.end()
                    matched = True
                    break
            
            if not matched:
                pos += 1  # 跳过无法识别的字符
        
        return tokens
    
    def parse(self, sql):
        """解析SQL并生成AST"""
        self.tokens = self.tokenize(sql)
        self.current = 0
        
        if not self.tokens:
            return {'type': 'root', 'children': []}
        
        try:
            return self.parse_statement()
        except Exception as e:
            print(f"解析错误: {e}")
            return {'type': 'error', 'message': str(e), 'children': []}
    
    def current_token(self):
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return None
    
    def consume(self, expected_type=None):
        token = self.current_token()
        if token:
            self.current += 1
            if expected_type and token['type'] != expected_type:
                raise Exception(f"期望 {expected_type}，但得到 {token['type']}")
        return token
    
    def peek(self, offset=0):
        pos = self.current + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def parse_statement(self):
        token = self.current_token()
        if not token:
            return {'type': 'empty', 'children': []}
        
        if token['type'] == 'SELECT':
            return self.parse_select()
        elif token['type'] == 'INSERT':
            return self.parse_insert()
        elif token['type'] == 'UPDATE':
            return self.parse_update()
        elif token['type'] == 'DELETE':
            return self.parse_delete()
        elif token['type'] == 'CREATE':
            return self.parse_create()
        else:
            return {'type': 'unknown_statement', 'value': token['value'], 'children': []}
    
    def parse_select(self):
        """解析SELECT语句，生成AST和执行计划"""
        # 生成AST（语法结构）
        ast_result = {
            'type': 'select_statement',
            'description': 'SQL查询语句的抽象语法树表示',
            'children': []
        }
        
        # 生成执行计划（逻辑执行顺序）
        execution_plan = {
            'type': 'execution_plan',
            'description': 'SQL查询的逻辑执行计划',
            'children': []
        }
        
        # 存储各个子句用于执行计划排序
        clauses = {}
        
        # 解析SELECT关键字
        if self.current_token() and self.current_token()['type'] == 'SELECT':
            self.consume('SELECT')
            
            # 创建select_expression_list节点
            select_list = self.parse_select_list()
            select_expr_list = {
                'type': 'select_expression_list',
                'children': [select_list]
            }
            ast_result['children'].append(select_expr_list)
            clauses['SELECT'] = {
                'type': 'select_operation',
                'execution_order': 5,
                'description': '选择指定的列或表达式',
                'children': [select_list]
            }
            
            # 解析FROM子句
            if self.current_token() and self.current_token()['type'] == 'FROM':
                from_clause = self.parse_from_clause()
                table_references = {
                    'type': 'table_references',
                    'children': [from_clause]
                }
                ast_result['children'].append(table_references)
                clauses['FROM'] = {
                    'type': 'table_scan',
                    'execution_order': 1,
                    'description': '扫描基础表，建立工作集',
                    'children': [from_clause]
                }
            
            # 解析JOIN子句
            join_clauses = []
            while (self.current_token() and 
                   self.current_token()['type'] in ['LEFT', 'RIGHT', 'INNER', 'JOIN']):
                join_clause = self.parse_join_clause()
                join_clauses.append(join_clause)
            
            if join_clauses:
                joined_table = {
                    'type': 'joined_table',
                    'children': join_clauses
                }
                ast_result['children'].append(joined_table)
                clauses['JOIN'] = {
                    'type': 'join_operation',
                    'execution_order': 2,
                    'description': '执行表连接操作',
                    'children': join_clauses
                }
            
            # 解析WHERE子句
            if self.current_token() and self.current_token()['type'] == 'WHERE':
                where_clause = self.parse_where_clause()
                where_expr = {
                    'type': 'where_expression',
                    'children': [where_clause]
                }
                ast_result['children'].append(where_expr)
                clauses['WHERE'] = {
                    'type': 'filter_operation',
                    'execution_order': 3,
                    'description': '过滤不符合条件的行',
                    'children': [where_clause]
                }
            
            # 解析GROUP BY子句
            if (self.current_token() and self.current_token()['type'] == 'GROUP' and
                self.peek(1) and self.peek(1)['type'] == 'BY'):
                group_by_clause = self.parse_group_by_clause()
                group_by_expr = {
                    'type': 'group_by_expression',
                    'children': [group_by_clause]
                }
                ast_result['children'].append(group_by_expr)
                clauses['GROUP_BY'] = {
                    'type': 'group_operation',
                    'execution_order': 4,
                    'description': '按指定列分组数据',
                    'children': [group_by_clause]
                }
            
            # 解析HAVING子句
            if self.current_token() and self.current_token()['type'] == 'HAVING':
                having_clause = self.parse_having_clause()
                having_expr = {
                    'type': 'having_expression',
                    'children': [having_clause]
                }
                ast_result['children'].append(having_expr)
                clauses['HAVING'] = {
                    'type': 'group_filter_operation',
                    'execution_order': 6,
                    'description': '过滤分组后的结果',
                    'children': [having_clause]
                }
            
            # 解析ORDER BY子句
            if (self.current_token() and self.current_token()['type'] == 'ORDER' and
                self.peek(1) and self.peek(1)['type'] == 'BY'):
                order_by_clause = self.parse_order_by_clause()
                order_by_expr = {
                    'type': 'order_by_expression',
                    'children': [order_by_clause]
                }
                ast_result['children'].append(order_by_expr)
                clauses['ORDER_BY'] = {
                    'type': 'sort_operation',
                    'execution_order': 7,
                    'description': '对结果进行排序',
                    'children': [order_by_clause]
                }
            
            # 解析LIMIT子句
            if self.current_token() and self.current_token()['type'] == 'LIMIT':
                limit_clause = self.parse_limit_clause()
                limit_expr = {
                    'type': 'limit_expression',
                    'children': [limit_clause]
                }
                ast_result['children'].append(limit_expr)
                clauses['LIMIT'] = {
                    'type': 'limit_operation',
                    'execution_order': 8,
                    'description': '限制返回的行数',
                    'children': [limit_clause]
                }
        
        # 按执行顺序排序执行计划
        sorted_clauses = sorted(clauses.values(), key=lambda x: x['execution_order'])
        execution_plan['children'] = sorted_clauses
        
        # 返回包含AST和执行计划的结构
        return {
            'type': 'query_analysis',
            'description': 'SQL查询分析结果',
            'children': [
                ast_result,
                execution_plan
            ]
        }
    
    def parse_select_list(self):
        """解析SELECT列表 - 符合MySQL AST标准"""
        select_items = []
        
        while True:
            # 解析选择项
            if self.current_token():
                select_item = self.parse_select_item()
                select_items.append(select_item)
                
                # 检查是否有逗号
                if self.current_token() and self.current_token()['type'] == 'COMMA':
                    self.consume('COMMA')
                else:
                    break
            else:
                break
        
        return {
            'type': 'select_item_list',
            'children': select_items
        }
    
    def parse_select_item(self):
        """解析单个选择项"""
        token = self.current_token()
        if not token:
            return {'type': 'empty_select_item', 'children': []}
        
        # 检查是否是通配符
        if token['type'] == 'MULTIPLY':
            self.consume('MULTIPLY')
            return {
                'type': 'select_star',
                'value': '*',
                'children': []
            }
        
        # 解析表达式（列名、函数调用等）
        expr = self.parse_expression()
        
        # 检查是否有别名
        alias = None
        if self.current_token() and self.current_token()['type'] == 'AS':
            self.consume('AS')
            if self.current_token():
                alias = self.current_token()['value']
                self.consume()
        elif (self.current_token() and 
              self.current_token()['type'] == 'IDENTIFIER' and
              self.current_token()['value'].upper() not in ['FROM', 'WHERE', 'GROUP', 'ORDER', 'HAVING', 'LIMIT']):
            alias = self.current_token()['value']
            self.consume()
        
        select_item = {
            'type': 'select_item',
            'children': [expr]
        }
        
        if alias:
            select_item['children'].append({
                'type': 'alias',
                'value': alias,
                'children': []
            })
        
        return select_item
    
    def parse_expression(self):
        """解析表达式"""
        token = self.current_token()
        if not token:
            return {'type': 'empty_expression', 'children': []}
        
        # 函数调用
        if (token['type'] in ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN'] and
            self.peek(1) and self.peek(1)['type'] == 'LPAREN'):
            return self.parse_function_call()
        
        # 列引用
        if token['type'] == 'IDENTIFIER':
            return self.parse_column_reference()
        
        # 字面量
        if token['type'] in ['STRING', 'INTEGER', 'DECIMAL']:
            value = token['value']
            self.consume()
            return {
                'type': 'literal',
                'value': value,
                'data_type': token['type'].lower(),
                'children': []
            }
        
        # 默认处理
        value = token['value']
        self.consume()
        return {
            'type': 'expression',
            'value': value,
            'children': []
        }
    
    def parse_from_clause(self):
        """解析FROM子句 - 符合MySQL AST标准"""
        # 消费 FROM 关键字
        self.consume('FROM')
        
        # 解析表引用
        table_ref = self.parse_table_reference()
        
        return {
            'type': 'from_clause',
            'children': [table_ref] if table_ref else []
        }
    
    def parse_join_clause(self):
        node = {'type': 'JOIN', 'children': []}
        
        # 解析 JOIN 类型（LEFT, RIGHT, INNER 或直接 JOIN）
        join_type = ''
        if self.current_token() and self.current_token()['type'] in ['LEFT', 'RIGHT', 'INNER']:
            join_type_token = self.consume()
            join_type = join_type_token['value']
            node['children'].append({'type': 'join_type', 'value': join_type, 'children': []})
        
        # 消费 JOIN 关键字
        if self.current_token() and self.current_token()['type'] == 'JOIN':
            join_token = self.consume('JOIN')
            node['children'].append({'type': 'keyword', 'value': join_token['value'], 'children': []})
        else:
            return None
        
        # 解析表名
        table = self.parse_table_reference()
        if table:
            node['children'].append(table)
        
        # 解析 ON 条件
        if self.current_token() and self.current_token()['type'] == 'ON':
            on_token = self.consume('ON')
            on_node = {'type': 'ON', 'children': []}
            on_node['children'].append({'type': 'keyword', 'value': on_token['value'], 'children': []})
            
            # 解析 ON 后的条件
            condition = self.parse_join_condition()
            if condition:
                on_node['children'].append(condition)
            
            node['children'].append(on_node)
        
        return node
    
    def parse_join_condition(self):
        # 解析类似 users.id = orders.user_id 的条件
        left = self.parse_qualified_column()
        
        if self.current_token() and self.current_token()['type'] in ['EQ', 'NE', 'LT', 'LE', 'GT', 'GE']:
            op_token = self.consume()
            right = self.parse_qualified_column()
            
            return {
                'type': 'join_condition',
                'operator': op_token['value'],
                'children': [left, right]
            }
        
        return left
    
    def parse_qualified_column(self):
        # 解析 table.column 格式的列引用
        if not self.current_token():
            return None
        
        first_token = self.current_token()
        if first_token['type'] in ['IDENTIFIER', 'BACKTICK_IDENTIFIER']:
            first_name = self.consume()
            
            # 检查是否有点号
            if self.current_token() and self.current_token()['type'] == 'DOT':
                self.consume('DOT')
                if self.current_token() and self.current_token()['type'] in ['IDENTIFIER', 'BACKTICK_IDENTIFIER']:
                    second_name = self.consume()
                    return {
                        'type': 'qualified_column',
                        'table': first_name['value'],
                        'column': second_name['value'],
                        'children': []
                    }
            else:
                # 只是普通的列名
                return {'type': 'column', 'value': first_name['value'], 'children': []}
        
        return None
    
    def parse_where_clause(self):
        """解析WHERE子句 - 符合MySQL AST标准"""
        # 消费 WHERE 关键字
        self.consume('WHERE')
        
        # 解析条件表达式
        condition = self.parse_condition()
        
        return {
            'type': 'where_clause',
            'children': [condition] if condition else []
        }
    
    def parse_condition(self):
        left = self.parse_simple_condition()
        
        while self.current_token() and self.current_token()['type'] in ['AND', 'OR']:
            op_token = self.consume()
            right = self.parse_simple_condition()
            
            left = {
                'type': 'logical_operation',
                'operator': op_token['value'],
                'children': [left, right]
            }
        
        return left
    
    def parse_simple_condition(self):
        left = self.parse_expression_atom()
        
        # 处理比较操作符
        if self.current_token() and self.current_token()['type'] in ['EQ', 'NE', 'LT', 'LE', 'GT', 'GE']:
            op_token = self.consume()
            right = self.parse_expression_atom()
            
            return {
                'type': 'comparison',
                'operator': op_token['value'],
                'children': [left, right]
            }
        
        # 处理 IS NULL / IS NOT NULL
        elif self.current_token() and self.current_token()['type'] == 'IS':
            self.consume('IS')
            
            # 检查是否有 NOT
            is_not = False
            if self.current_token() and self.current_token()['type'] == 'NOT':
                self.consume('NOT')
                is_not = True
            
            # 消费 NULL
            if self.current_token() and self.current_token()['type'] == 'NULL':
                self.consume('NULL')
                return {
                    'type': 'null_check',
                    'operator': 'IS NOT NULL' if is_not else 'IS NULL',
                    'children': [left]
                }
        
        return left
    
    def parse_expression_atom(self):
        # 解析表达式原子（列引用、字面值等）
        if not self.current_token():
            return None
        
        token = self.current_token()
        
        # 处理带表名的列引用
        if token['type'] in ['IDENTIFIER', 'BACKTICK_IDENTIFIER']:
            return self.parse_qualified_column()
        
        # 处理字面值
        elif token['type'] in ['STRING', 'INTEGER', 'DECIMAL']:
            value_token = self.consume()
            return {'type': 'literal', 'value': value_token['value'], 'data_type': token['type'], 'children': []}
        
        # 处理函数调用
        elif token['type'] in ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN']:
            return self.parse_function_call()
        
        return None
    
    def parse_function_call(self):
        if not self.current_token():
            return None
        
        func_token = self.consume()
        node = {'type': 'function_call', 'function_name': func_token['value'], 'children': []}
        
        # 消费左括号
        if self.current_token() and self.current_token()['type'] == 'LPAREN':
            self.consume('LPAREN')
            
            # 解析参数（简化处理）
            if self.current_token() and self.current_token()['type'] == 'MULTIPLY':
                star_token = self.consume('MULTIPLY')
                node['children'].append({'type': 'wildcard', 'value': star_token['value'], 'children': []})
            elif self.current_token() and self.current_token()['type'] not in ['RPAREN']:
                # 解析其他参数
                arg = self.parse_expression_atom()
                if arg:
                    node['children'].append(arg)
            
            # 消费右括号
            if self.current_token() and self.current_token()['type'] == 'RPAREN':
                self.consume('RPAREN')
        
        return node
    
    def parse_column_reference(self):
        """解析列引用 - 符合MySQL AST标准"""
        if not self.current_token():
            return None
        
        token = self.current_token()
        if token['type'] in ['IDENTIFIER', 'BACKTICK_IDENTIFIER']:
            first_name = self.consume()['value']
            
            # 检查是否有点号（表名.列名）
            if self.current_token() and self.current_token()['type'] == 'DOT':
                self.consume('DOT')
                if self.current_token() and self.current_token()['type'] in ['IDENTIFIER', 'BACKTICK_IDENTIFIER']:
                    column_name = self.consume()['value']
                    return {
                        'type': 'column_reference',
                        'table_name': first_name,
                        'column_name': column_name,
                        'children': []
                    }
            else:
                # 只是列名
                return {
                    'type': 'column_reference',
                    'column_name': first_name,
                    'children': []
                }
        
        return None
    
    def parse_table_reference(self):
        """解析表引用 - 符合MySQL AST标准"""
        if not self.current_token():
            return None
        
        token = self.current_token()
        if token['type'] in ['IDENTIFIER', 'BACKTICK_IDENTIFIER']:
            table_name = self.consume()['value']
            
            # 检查是否有别名
            alias = None
            if self.current_token() and self.current_token()['type'] == 'AS':
                self.consume('AS')
                if self.current_token() and self.current_token()['type'] == 'IDENTIFIER':
                    alias = self.consume()['value']
            elif (self.current_token() and 
                  self.current_token()['type'] == 'IDENTIFIER' and
                  self.current_token()['value'].upper() not in ['LEFT', 'RIGHT', 'INNER', 'JOIN', 'WHERE', 'GROUP', 'ORDER', 'HAVING', 'LIMIT']):
                alias = self.consume()['value']
            
            table_ref = {
                'type': 'table_reference',
                'table_name': table_name,
                'children': []
            }
            
            if alias:
                table_ref['alias'] = alias
            
            return table_ref
        
        return None
    
    def parse_value(self):
        if not self.current_token():
            return None
        
        token = self.current_token()
        if token['type'] in ['STRING', 'INTEGER', 'DECIMAL']:
            value_token = self.consume()
            return {'type': 'literal', 'value': value_token['value'], 'data_type': token['type'], 'children': []}
        elif token['type'] in ['IDENTIFIER', 'BACKTICK_IDENTIFIER']:
            return self.parse_column_reference()
        
        return None
    
    def parse_group_by_clause(self):
        node = {'type': 'GROUP_BY', 'children': []}
        
        # 消费 GROUP BY 关键字
        group_token = self.consume('GROUP')
        by_token = self.consume('BY')
        node['children'].append({'type': 'keyword', 'value': f"{group_token['value']} {by_token['value']}", 'children': []})
        
        # 解析分组列列表
        group_list = {'type': 'group_list', 'children': []}
        
        while True:
            column = self.parse_qualified_column()
            if column:
                group_list['children'].append(column)
            
            # 检查是否有更多列（逗号分隔）
            if self.current_token() and self.current_token()['type'] == 'COMMA':
                self.consume('COMMA')
            else:
                break
        
        node['children'].append(group_list)
        return node
    
    def parse_having_clause(self):
        node = {'type': 'HAVING', 'children': []}
        
        # 消费 HAVING 关键字
        having_token = self.consume('HAVING')
        node['children'].append({'type': 'keyword', 'value': having_token['value'], 'children': []})
        
        # 解析 HAVING 条件
        condition = self.parse_condition()
        if condition:
            node['children'].append(condition)
        
        return node
    
    def parse_order_by_clause(self):
        node = {'type': 'ORDER_BY', 'children': []}
        
        # 消费 ORDER BY 关键字
        order_token = self.consume('ORDER')
        by_token = self.consume('BY')
        node['children'].append({'type': 'keyword', 'value': f"{order_token['value']} {by_token['value']}", 'children': []})
        
        # 解析排序列列表
        order_list = {'type': 'order_list', 'children': []}
        
        while True:
            column = self.parse_qualified_column()
            if column:
                order_item = {'type': 'order_item', 'children': [column]}
                
                # 检查是否有 ASC/DESC
                if (self.current_token() and 
                    self.current_token()['value'].upper() in ['ASC', 'DESC']):
                    direction_token = self.consume()
                    order_item['children'].append({
                        'type': 'sort_direction',
                        'value': direction_token['value'],
                        'children': []
                    })
                
                order_list['children'].append(order_item)
            
            # 检查是否有更多列（逗号分隔）
            if self.current_token() and self.current_token()['type'] == 'COMMA':
                self.consume('COMMA')
            else:
                break
        
        node['children'].append(order_list)
        return node
    
    def parse_limit_clause(self):
        node = {'type': 'LIMIT', 'children': []}
        limit_token = self.consume('LIMIT')
        node['children'].append({'type': 'keyword', 'value': limit_token['value'], 'children': []})
        
        if self.current_token() and self.current_token()['type'] == 'INTEGER':
            num_token = self.consume('INTEGER')
            node['children'].append({'type': 'literal', 'value': num_token['value'], 'data_type': 'INTEGER', 'children': []})
        
        return node
    
    def parse_insert(self):
        return {'type': 'INSERT', 'children': []}
    
    def parse_update(self):
        return {'type': 'UPDATE', 'children': []}
    
    def parse_delete(self):
        return {'type': 'DELETE', 'children': []}
    
    def parse_create(self):
        return {'type': 'CREATE', 'children': []}

def main():
    # 读取输入文件
    input_file = 'input.sql'
    if not os.path.exists(input_file):
        print(f"错误：找不到文件 {input_file}")
        sys.exit(1)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            sql_content = f.read().strip()
        
        if not sql_content:
            print("错误：SQL文件为空")
            sys.exit(1)
        
        print(f"正在解析SQL: {sql_content}")
        
        # 解析SQL
        parser = SimpleSQLParser()
        ast = parser.parse(sql_content)
        
        # 输出到JSON文件
        output_file = 'ast.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ast, f, ensure_ascii=False, indent=2)
        
        print(f"AST已生成并保存到 {output_file}")
        print("\n生成的AST结构:")
        print(json.dumps(ast, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)

# 添加HTTP服务器支持
import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

class SQLParserHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/parse-sql':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                sql = data.get('sql', '')
                if not sql:
                    self.send_error(400, 'No SQL provided')
                    return
                
                # 使用现有的解析器解析SQL
                parser = SimpleSQLParser()
                ast = parser.parse(sql)
                
                # 返回JSON响应
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                response = json.dumps(ast, ensure_ascii=False, indent=2)
                self.wfile.write(response.encode('utf-8'))
                
            except Exception as e:
                self.send_error(500, f'Parse error: {str(e)}')
        else:
            super().do_POST()
    
    def do_OPTIONS(self):
        # 处理CORS预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def start_server(port=8001):
    """启动HTTP服务器"""
    with socketserver.TCPServer(("", port), SQLParserHTTPHandler) as httpd:
        print(f"SQL解析服务器启动在端口 {port}")
        print(f"访问 http://localhost:{port} 查看可视化")
        httpd.serve_forever()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'server':
        # 启动服务器模式
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8001
        start_server(port)
    else:
        # 原有的文件解析模式
        main()