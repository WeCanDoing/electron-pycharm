// 引入 worker_threads 模块，该模块提供创建工作线程的功能  
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');  
  
// 定义一个 ThreadPool 类，用于创建和管理线程池  
class ThreadPool {  
    // 构造函数，初始化线程池的最大大小和当前工作线程数组  
    constructor(maxSize) {  
        this.maxSize = maxSize; // 线程池的最大大小  
        this.workers = []; // 当前的工作线程数组  
        this.queue = []; // 等待执行的任务队列  
        this.currentTask = 0; // 当前任务的ID计数器  
    }  
  
    // 运行任务的方法，返回一个Promise，表示任务的执行结果  
    runTask(task) {  
        return new Promise((resolve,) => {  
            // 为当前任务分配一个唯一的ID  
            const id = this.currentTask++;  
            console.log("task"+task)    
            // 如果线程池中的工作线程数量小于最大大小，并且当前不是主线程  
            if (this.workers.length < this.maxSize && !isMainThread) {  
                // 创建一个新的工作线程，并将任务和任务的ID作为workerData传递  
                this.workers.push(new Worker(__filename, { workerData: { id, task } }));  
            } else {  
                // 如果线程池已满，将任务放入队列中等待执行  
                this.queue.push({ id, task, resolve, reject });  
            }  
            resolve(task)
        });  
    }  
  
    // 当从工作线程接收到消息时调用的方法  
    onMessage(msg) {  
        // 从消息中提取ID和结果  
        const { id, result } = msg;  
        // 从队列中取出等待执行的任务  
        const task = this.queue.shift();  
  
        // 如果有等待执行的任务，则运行该任务并处理其结果  
        if (task) {  
            this.runTask(task.task).then(result => task.resolve(result)).catch(task.reject);  
        }  
    }  
}  
  
// 如果当前不是主线程（即在一个工作线程中），则执行以下代码  
if (!isMainThread) {  
    try {  
        // 从workerData中提取ID和任务  
        const { id, task } = workerData;  
        // 执行任务并获取结果  
        const result = task();  
        // 将结果和ID作为消息发送给主线程  
        parentPort.postMessage({ id, result });  
    } catch (error) {  
        // 如果执行任务时发生错误，将错误消息发送给主线程  
        parentPort.postMessage({ id, error: error.message });  
    }  
} else {  
    // 如果是主线程，则创建线程池实例，并监听来自工作线程的消息  
    const pool = new ThreadPool(4); // 创建一个最大为4个工作线程的线程池  
    // 当主线程接收到消息时，调用 pool.onMessage 方法处理消息  
    process.on('message', pool.onMessage.bind(pool));  
    // 导出线程池实例，以便其他模块可以使用  
    module.exports = pool;  
}