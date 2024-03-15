export default class ConcurrencyLimiter {  
  constructor(concurrency) {  
    this.concurrency = concurrency;  
    this.running = 0;  
    this.queue = [];  
  }  
  
  async add(promiseCreator) {  
    return new Promise((resolve, reject) => {  
      const run = async () => {  
        try {  
          this.running++;  
          const result = await promiseCreator();  
          this.running--;  
          if (this.queue.length) {  
            this.queue.shift()();  
          }  
          resolve(result);  
        } catch (error) {  
          this.running--;  
          reject(error);  
        }  
      };  
  
      if (this.running < this.concurrency) {  
        run();  
      } else {  
        this.queue.push(run);  
      }  
    });  
  }  
}  

 