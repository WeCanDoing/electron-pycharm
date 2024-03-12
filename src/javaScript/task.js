// 引入线程池模块  
const pool = require('./threadPool'); // 引入上面定义的线程池  
  
// 定义一个计算斐波那契数列的函数  
function fibonacci(n) {  
    if (n <= 1) return n;  
    return fibonacci(n - 1) + fibonacci(n - 2);  
}  
  
// 使用异步函数处理斐波那契数列的计算，并输出结果  
async function processFibonacci(n) {  
    console.log(n)
    // 通过线程池运行计算斐波那契数列的任务，并等待结果  
    const result = await pool.runTask(n).then(res=>{
      fibonacci(n)
    });  
    // 输出结果  
    console.log(`Fibonacci of ${n} is: ${result}`);  
}  
  
// 并行处理多个斐波那契数列的计算  
processFibonacci(30); // 计算第30项斐波那契数  
processFibonacci(35); // 计算第35项斐波那契数  
processFibonacci(40); // 计算第40项斐波那契数