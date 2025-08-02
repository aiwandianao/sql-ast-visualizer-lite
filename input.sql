-- 示例 SQL，用户可修改
SELECT id, name FROM users 
LEFT JOIN orders ON users.id = orders.user_id 
WHERE age > 18 AND name = '张三' AND orders.id IS NULL 
GROUP BY id, name 
HAVING count(*) = 0;
