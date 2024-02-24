<template>
    <div>
      <el-main>
      <el-table :data="fileList"  @row-click="sendEvent">
        <el-table-column prop="name" label="文件名称" width="140">
        </el-table-column>
        <!-- <el-table-column prop="size" label="大小" width="120">
        </el-table-column> -->
        <el-table-column prop="isDirectory" label="地址" width="180">
        </el-table-column>
      </el-table>
    </el-main>
    </div>
  </template>
  
  <script>
  const fs = window.require('fs');
  
  export default {
    data() {
      return {
        fileList: [],
        info: "测试"
      };
    },
    mounted() {
      // const dir = './src/pyScript'; // 替换为您的目录路径
      const dir ='./resources/pyScript';
      this.fileList = this.getFiles(dir);
    },
    methods: {
      getFiles(dir) {
        const files = fs.readdirSync(dir);
        return files.map((file) => {
          const filePath = `${dir}/${file}`;
          const stats = fs.statSync(filePath);
          return {
            name: file,
            size: stats.size,
            isDirectory: filePath,
          };
        });
      },
      sendEvent(row, column, cell, event) {
        // 使用 $emit 方法触发一个名为 my-event 的自定义事件，并将 info 作为参数传递
        console.log("row", row)
        console.log(column)
        console.log(cell)
        console.log(event)

        this.$emit('my-event', row.isDirectory)
      }
      
    }
  };
  </script>
  