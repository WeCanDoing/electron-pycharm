<template>
  <div>
    <!-- 使用 flex 布局的容器 -->
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>通用设置</span>
      </div>
      <div style="display: flex; align-items: center;">
        <!-- 使用 flex-grow 属性来分配剩余空间 -->
        <span style="width: 150px;">图片文件夹下载地址</span>

        <el-input placeholder="请输入内容" v-model="imageAddress" clearable style="width: 250px;"></el-input>
        <div>
          <el-button type="primary" @click="selectDirectory">选择文件夹</el-button>
          <input type="file" id="file-selector" style="display: none" webkitdirectory @change="handleFiles"
            ref="fileSelector">

        </div>


        <span style="width: 150px; margin-left: 10px;">Excel下载地址</span>
        <el-input placeholder="请输入内容" v-model="excelAddress" clearable style="width: 250px;"></el-input>
      </div>
    </el-card>

    <div>
      <!-- 使用 flex 布局的容器 -->
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span>脚本参数设置</span>
        </div>
        <div style="display: flex; align-items: center;">
          <!-- 使用 flex-grow 属性来分配剩余空间 -->
          <span style="width: 150px;">网页地址</span>
          <el-input placeholder="请输入内容" v-model="catUrl" clearable style="width: 150px;"></el-input>
          <span style="width: 150px; margin-left: 10px;">页数</span>
          <el-input placeholder="请输入内容" v-model="page" clearable style="width: 150px;"></el-input>
          <el-radio v-model="radio" label=0>导出文本和图片</el-radio>
          <el-radio v-model="radio" label=1>仅导出文本</el-radio>
        </div>
      </el-card>
    </div>
    <div>
      <div>
        脚本名称：{{ message }}
        <el-popconfirm @confirm="clickRun" title="确认执行脚本？">
          <el-button type="success" slot="reference" :loading = "runDisabled">执行</el-button>
        </el-popconfirm>
        <el-button @click="illustrateShow" type="primary" style="margin-left: 16px;">
          文件使用说明
        </el-button>
        <el-button @click="forceStop" type="danger" style="margin-left: 16px;" :disabled="!runDisabled">
          强制停止
        </el-button>
        <el-drawer
        title="文件使用说明"
        :visible.sync="drawer"
        >
        <span v-html="inputDesc"></span>
        <span v-html="illustrate"></span>
      </el-drawer>
      </div>
    <el-divider></el-divider>
    <div class="my-class">
        <el-input
          type="textarea"
          style="color: #333; height: 300px; overflow-y: auto;"
        :autosize="{ 'min-rows': 20 }"
          v-model="description"
          clearable
          disabled
        >
        </el-input>
      </div>
  </div>
</div></template>

<script>
// const exec =  window.require('child_process').exec
const path = window.require('path');
var iconv = require('iconv-lite');
const { spawn } = window.require('child_process');
const fs = window.require('fs');

export default {
  props: {
    message: String // 修改了这里
  },
  data() {
    return {
      excelAddress: 'D://示例文本.xlsx',
      imageAddress: 'D://',
      catUrl: 'www.baidu.com',
      page: 0,
      description: '',
      folderPath: '', // 存放所选文件夹的路径
      drawer: false,
      illustrate: '文件使用说明',
      inputDesc: '参数说明',
      radio: '0',
      runDisabled: false,
      child: null, // 存储子进程对象
      logFilePath: '' // 日志文件路径
    };
  },
  mounted() { },
  methods: {

    selectDirectory() {
      this.$refs.fileSelector.click();
    },

    //选择文件夹
    handleFiles(event) {
      const filePath = event.target.files[0].path;
      this.folderPath = path.dirname(filePath);
      console.log(this.folderPath)
      this.imageAddress = this.folderPath
    },

    //点击事件
    clickRun() {
      let t = this
      //控制按钮为加载的样式，无法点击
      this.runDisabled = true
      console.log(this.runDisabled)
      //清除之前的控制台缓存
      t.description = ''
      // 生成带有时间戳的日志文件名
      const timestamp = new Date().toISOString().replace(/[-:.]/g, '');
      this.logFilePath = `E://yujianTool/log_${timestamp}.txt`;
      this.cmdCopy(this.excelAddress, this.imageAddress, this.catUrl, this.page,this.radio, function (e) {
        // t.description = e // 这里直接赋值可能不会更新视图
        t.description = t.description + iconv.decode(e, 'utf-8')
        console.log("打印 --", t.description)

      })
    },

    forceStop() {
      if (this.child) {
        this.child.kill('SIGTERM');
        this.runDisabled = false;
        console.log("脚本已被强制停止");
      }
    },

    // 修改cmdCopy方法
    cmdCopy(excelAddress, imageAddress, catUrl, page, radio, callbackFun) {
      try {
        const cmd = `python -u ${path.resolve(this.message)} ${catUrl} ${excelAddress} ${imageAddress} ${page} ${radio}`;
        console.log("cmd命令:" + cmd)
        this.child = spawn(cmd, { 
          shell: true,
          encoding: 'buffer',
          stdio: ['pipe', 'pipe', 'pipe']
        });

        let bufferStore = '';
        const handleData = (buffer) => {
          const decodedBuffer = iconv.decode(buffer, 'utf-8');
          bufferStore += decodedBuffer;
          const lines = bufferStore.split(/\r?\n/);
          bufferStore = lines.pop();
          lines.forEach(line => {
            callbackFun(line + '\n');
            // 将输出写入日志文件
            fs.appendFileSync(this.logFilePath, line + '\n', 'utf-8');
          });
        };

        this.child.stdout.on('data', (buffer) => {
          handleData(buffer);
        });

        this.child.stderr.on('data', (buffer) => {
          handleData(buffer);
        });

        this.child.on('close', () => {
          if (bufferStore) {
            callbackFun(bufferStore + '\n');
            // 将剩余的输出写入日志文件
            fs.appendFileSync(this.logFilePath, bufferStore + '\n', 'utf-8');
          }
          this.runDisabled = false;
          this.child = null;
        });

      } catch (e) {
        console.error(e);
        this.runDisabled = false;
      }
    },

    //python文件参数说明
    illustrateShow() {
      this.drawer = true
      this.inputDesc = "图片文件夹下载地址：图片保存的路径 <br> Excel下载地址:拍品文本的下载地址，需要具体到文件名称 如D：//示例文本.xlsx <br> 网页地址: 需要抓取的网址 <br> "
      if (this.message.includes("drouot")) {
        this.illustrate = `本脚本抓取的是www.drouot.com网址专用的脚本 抓取的网址获取方式为：<br>
        1.打开要抓取的网页（必须是drouot网站）<br>
        2.负责上方网页链接填入抓取地址 <br>
        3.在起始页码处填写0  <br>
        4.执行脚本 <br>
        `
      }
    }
  } 
}
</script>

<style>
.text {
  font-size: 14px;
}

.item {
  margin-bottom: 0px;
}

.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}

.clearfix:after {
  clear: both
}

.box-card {
  width: 600;
}

/* 修改文本域的边框颜色和圆角 */
.my-class ::v-deep .el-textarea__inner {
  border: 1px solid #3d66e4;
  border-radius: 4px;
  color: #333;
}
</style>