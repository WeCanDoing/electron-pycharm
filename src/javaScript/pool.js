// pool.js
// 引入 child_process 模块
const { spawn } = require('child_process');
// 定义线程池的大小
const poolSize = 4;
// 定义线程池，用一个数组来存储子进程
const pool = [];
// 定义任务队列，用一个数组来存储待处理的数据
const queue = [];
// 定义结果数组，用一个数组来存储处理后的结果
const results = [];

// 定义一个函数，用于创建子进程并添加到线程池中
function createWorker() {
  // 创建一个子进程，执行 task.js 文件
  const worker = spawn('node', ['task.js'],{stdio: 'pipe'});
  // 监听子进程的标准输出流，获取结果
  worker.stdout.on('data', (data) => {
    // 将结果转换为数字并添加到结果数组中
    results.push(Number(data));
    // 检查任务队列是否为空
    if (queue.length > 0) {
      // 如果不为空，取出队列头部的数据，并发送给子进程
      const task = queue.shift();
      worker.stdin.write(task + '\n');
    } else {
      // 如果为空，结束子进程的输入流，释放资源
      console.log("进程结束")
      worker.stdin.end();
    }
  });
  // 监听子进程的退出事件，从线程池中移除
  worker.on('exit', () => {
    // 获取子进程在线程池中的索引
    const index = pool.indexOf(worker);
    // 如果存在，从线程池中删除
    if (index !== -1) {
      pool.splice(index, 1);
    }
    // 检查线程池是否为空
    if (pool.length === 0) {
      // 如果为空，表示所有任务都已完成，打印结果数组
      console.log(results);
    }
  });
  // 将子进程添加到线程池中
  pool.push(worker);
}

// 定义一个函数，用于向线程池中的子进程分配任务
function assignTask(data) {
    console.log("线程池" + data)
  // 遍历线程池中的子进程
  for (const worker of pool) {
    // 检查子进程的输入流是否可写
    if (worker.stdin.writable) {
      // 如果可写，将数据发送给子进程，并返回
      console.log("可写数据" +data)
      worker.stdin.write(data + '\n');
      return;
    }
  }
  // 如果没有可写的子进程，将数据添加到任务队列中
  queue.push(data);
}

// 创建线程池
for (let i = 0; i < poolSize; i++) {
  createWorker();
}

// 分配任务，假设有 10 个任务，分别是计算 1 到 10 的平方
for (let i = 1; i <= 10; i++) {
  assignTask(i);
}
