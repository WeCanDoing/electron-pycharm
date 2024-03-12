<template>
  <div>
    <el-main>
      <el-table :data="fileList" @row-click="sendEvent">
        <el-table-column prop="name" label="文件名称" width="140">
        </el-table-column>
      </el-table>
    </el-main>
  </div>
</template>

<script>
const path = require('path');
const fs = window.require('fs');
export default {

  props: {
    disr: String
  },
  data() {
    return {
      fileList: [{
            name: '王小虎'
          }],
      info: "测试"
    };
  },
  mounted() {
      console.log("监听方法")
      this.getFiles(this.disr);
  },

  methods: {
    getFiles(disr) {  
    this.getDirectories(disr);  
    console.log("值"+ this.fileList)
  },  
  
  getDirectories(srcpath) {  
    console.log(srcpath)
    const files = fs.readdirSync(srcpath);  
    console.log(files)
    this.fileList = [];
    files.forEach(file => {
      if(fs.lstatSync(path.join(srcpath, file)).isDirectory()){
        console.log(String(file))
        this.fileList.push({ name: String(file) }); // 将目录名作为对象添加到fileList中  
      }else{
        console.log("不是目录")
      }
    });
  },  
  
  sendEvent(row, column, cell, event) {  
    // 假设你希望发送目录名称，那么应该发送 row.name  
    this.$emit('my-event', row.name);  
    console.log(column)
    console.log(cell)
    console.log(event)

  }  
  },
  watch: {
    disr() {
      console.log("监听方法")
      this.getFiles(this.disr);
    }
  },
};
</script>