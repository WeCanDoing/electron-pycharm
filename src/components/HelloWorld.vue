<template>
  <div class="hello">
    <el-container style="height: 1000px; border: 1px solid #eee">
  <el-aside width="400px" style="background-color:#fdfdfd">
    <div data-v-469af010="" style="
    height: 60px;
    background-color: #B3C0D1;"></div>

    
    <div  style="width: 380px;">
      <file-list v-on:my-event="handleEvent"></file-list>
       <el-button type="primary" @click="selectDirectory">选择文件夹</el-button>
        <input type="file" id="file-selector" style="display: none" webkitdirectory @change="handleFiles" ref="fileSelector">
    </div>
  </el-aside>
  
  <el-container>
    <el-header style="text-align: right; font-size: 20px">
      <el-dropdown>
        <i class="el-icon-setting" style="margin-right: 15px"></i>
        <el-dropdown-menu slot="dropdown">
        </el-dropdown-menu>
      </el-dropdown>
      <span>管理员</span>
    </el-header>
    
    <el-main>
      <py-controller :message = "msg"></py-controller>
    </el-main>
  </el-container>
</el-container>

  </div>
</template>

<script>
const exec = window.require('child_process').exec
const path = window.require('path');
import FileList from './FileList.vue';
import PyController from './PyController.vue';

export default {
  name: 'HelloWorld',
  components: {
    FileList,
    PyController
  },

  data() {
    const item = {
      date: '2016-05-02',
      name: '王小虎',
      address: '上海市普陀区金沙江路 1518 弄'
    };
    return {
      tableData: Array(20).fill(item),
      msg: "脚本名称"
    }
  },
  methods: {
    selectDirectory() {
      this.$refs.fileSelector.click();
    },
    //选择文件夹
    handleFiles(event) {
      const files = event.target.files;
      console.log(files);
      for (let i = 0; i < files.length; i++) {
        // 文件夹中的py文件移动当当前目录
        this.cmdCopy(files[i].path,path.resolve('./resources/pyScript'),function (x) {
        console.log(x)
      })
      }
      location.reload()
    },
    //复制文件
    cmdCopy (src, dest, callbackFun) {
    try {
        exec(`copy ${ src } ${ dest } /Y /V`, (err) => {
          if (err) {
            console.log(err)
            callbackFun(false)
            return
          }
          callbackFun(true)
        })
    } catch (e) {
      console.log(e)
      callbackFun(false)
    }
  },
  handleEvent(data) {
        // data 是子组件传递过来的参数，获取路径
        console.log("地址",data)
        this.msg = data
      }
  
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}

.el-header {
  background-color: #B3C0D1;
  color: #333;
}

.el-aside {
  color: #333;
}</style>
